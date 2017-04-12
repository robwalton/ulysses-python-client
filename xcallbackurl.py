'''
Created on 7 Apr 2017

@author: walton
'''


import os.path
from time import sleep
import urlparse
import urllib
import logging

logger = logging.getLogger(__name__)



from AppKit import NSWorkspace  # @UnresolvedImport
import Foundation as fn

from AppKit import NSWorkspaceLaunchWithoutActivation  # @UnresolvedImport


class NonPersistedTokenProvider(object):  
    def __init__(self, token=None):
        self.token = token
    
token_provider = NonPersistedTokenProvider()  
                

class XCallbackError(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)


def call_ulysses(action, action_parameter_dict={}, send_access_token=False,
                 silent_mode=False, leave_ulysses_in_background=True):
    
    if send_access_token:
        action_parameter_dict['access-token'] = token_provider.token
    if silent_mode:
        action_parameter_dict['silent-mode': 'YES']
        
    cmd = encode_request(action, action_parameter_dict)
    logger.debug('<<<')
    logger.debug('   Sending: ' + cmd)
    reply = urlcall(cmd, leave_ulysses_in_background)
    logger.debug('   Received: ' + reply)
    decoded_reply = decode_reply(reply)
    logger.debug('   Decoded to: ' + str(decoded_reply))
    logger.debug('>>>')
    return decoded_reply


def urlcall(url, leave_ulysses_in_background=True):
    sleep(.05)  # seems to be some deadtime after last callback
    ensure_callback_handler_pipe_exists()
    
    ws = NSWorkspace.sharedWorkspace()
    ns_url = fn.NSURL.URLWithString_(url)  # @UndefinedVariable

    
    options = NSWorkspaceLaunchWithoutActivation if leave_ulysses_in_background else None
    ws.openURLs_withAppBundleIdentifier_options_additionalEventParamDescriptor_launchIdentifiers_(
        [ns_url], None, options,  None, None)
    return read_last_line_from_pipe().strip()



def decode_reply(msg):
    """Return result dictionary if x-success called, or raise Exception if x-error called
    """
    split_results = urlparse.urlsplit(msg)
    query_args = urlparse.parse_qs(split_results.query)
    for k,v in query_args.iteritems():
        query_args[k] = v[0]  # pull values out of the list parse_qs results in
    
    if split_results.path == '/success':
        # SplitResult(scheme='ulysses-python-client', netloc='x-callback-url', path='/success', query='buildNumber=33496&apiVersion=2', fragment='')
        return query_args
    
    elif split_results.path == '/error':
        # 'ulysses-python-client://x-callback-url/error?errorMessage=Invalid%20Action&errorCode=100'
        error_message = query_args['errorMessage'].replace('%20', ' ')
        error_code = query_args['errorCode']
        raise XCallbackError(error_message + '. Code = ' + error_code)
    
    else:
        raise AssertionError('enexpected path in callback url: ' + msg)


def encode_request(action, action_parameter_dict):  # , silent_mode=False):
    # [scheme]://[host]/[action]?[x-callback parameters]&[action parameters]
    scheme = 'ulysses'
    host = 'x-callback-url'
    
    x_callback_parameters = (
        'x-success=ulysses-python-client://x-callback-url/success'
        '&x-error=ulysses-python-client://x-callback-url/error')
    
    url = '%(scheme)s://%(host)s/%(action)s?%(x_callback_parameters)s' % locals()
    if action_parameter_dict:
        url = url + '&' + urllib.urlencode(action_parameter_dict)
    
    return url


