'''
Created on 7 Apr 2017

@author: walton
'''


import urllib
import logging

logger = logging.getLogger(__name__)

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
    result = xcall(cmd)
    logger.debug('   Received: ' + str(result))
    logger.debug('>>>')
    return result


def xcall(url):
    from subprocess import Popen, PIPE
    p = Popen(['bin/xcall.app/Contents/MacOS/xcall', '-url', url], stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    
    assert (stdout == '') or (stderr == '')
    if stdout:
        return eval(stdout)
    elif stderr:
        d = eval(stderr)
        raise XCallbackError(d['errorMessage'] + '. Code = ' + d['errorCode'])


def encode_request(action, action_parameter_dict):  # , silent_mode=False):
    url = 'ulysses://x-callback-url/%s' % action
    if action_parameter_dict:
        url = url + '?' + urllib.urlencode(action_parameter_dict)
    return url


