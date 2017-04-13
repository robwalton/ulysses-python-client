"""
X-callback-url implementation for calling Ulyyses via xcall.

xcall is command line macOS application providing generic access to
applications with x-callback-url schemes:

   https://github.com/martinfinke/xcall

Many Ulysses calls require a Ulysses access-token token. See:

    https://ulyssesapp.com/kb/x-callback-url/#authorization

Extend NonPersistedTokenProvider and set token_provider after importing module.
"""

import urllib
import logging


logger = logging.getLogger(__name__)


class NonPersistedTokenProvider(object):
    """Provides an access-token string.

    Atrributes:

    token -- access-token string
    """
    def __init__(self, token=None):
        self.token = token


token_provider = NonPersistedTokenProvider()


class XCallbackError(Exception):
    """Exception representing an error reported from Ulysses.
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def call_ulysses(action, params={}, send_access_token=False,
                 silent_mode=False):
    """Perform a Ulysses action and return result.

    action -- the name of the Ulysses action to perform
    params -- dictionary of parameters to pass with call
    send_access_token -- append access-token in params if True
    silent-mode -- append silent-mode=YES to params if True. This prevents
                   actions which alter Ulysses content from bring Ulysses
                   forward.
    """

    if send_access_token:
        params['access-token'] = token_provider.token
    if silent_mode:
        params['silent-mode': 'YES']

    cmd = build_url(action, params)
    logger.debug('<<<')
    logger.debug('   Sending: ' + cmd)
    result = xcall(cmd)
    logger.debug('   Received: ' + str(result))
    logger.debug('>>>')
    return result


def xcall(url):
    """Send a URL to Ulyyses via xcall and return result as dictionary.
    
    url -- un-encoded URL to send. Will be encoded before sending. 

    May raise XCallbackError with error message and code from Ulysses.
    """
    from subprocess import Popen, PIPE
    p = Popen(['bin/xcall.app/Contents/MacOS/xcall', '-url', url],
              stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()

    assert (stdout == '') or (stderr == '')
    if stdout:
        return eval(stdout)
    elif stderr:
        d = eval(stderr)
        raise XCallbackError(d['errorMessage'] + '. Code = ' + d['errorCode'])


def build_url(action, action_parameter_dict):
    """Build url to send to Ulysess.

    action -- Ulysses action name
    action_parameter_dict -- parameters for given action
    """
    url = 'ulysses://x-callback-url/%s' % action
    if action_parameter_dict:
        url = url + '?' + urllib.urlencode(action_parameter_dict)
    return url
