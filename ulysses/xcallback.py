# encoding: utf-8
#
# Copyright (c) 2016 Rob Walton <dhttps://github.com/robwalton>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-04-17

"""
Ulysses specific xcall implementaion.

"""

import logging

import xcall

logger = logging.getLogger(__name__)


# Token provider

class NonPersistedTokenProvider(object):
    """Provides an access-token string.

    Atrributes:

    token -- access-token string
    """
    def __init__(self, token=None):
        self.token = token


token_provider = NonPersistedTokenProvider()


def set_access_token(token):
    """Set access token required for many Ulysses calls."""
    token_provider.token = token


# x-callback-url

class UlyssesError(xcall.XCallbackError):
    """Exception representing an x-error callback from Ulysses.
    """
    pass


def ulysses_xerror_handler(xerror, requested_url):
    d = eval(xerror)
    error_message = d['errorMessage']
    if error_message[-1] != '.':
        error_message += '.'
    error_code = d['errorCode']
    raise UlyssesError(
        ("%(error_message)s Code=%(error_code)s. "
         "In response to sending the url '%(requested_url)s'") % locals())


ULYSSES_XCALL = xcall.XCallClient('ulysses', ulysses_xerror_handler,
                                  json_decode_success=True)


def call_ulysses(action, params={}, send_access_token=False,
                 silent_mode=False, activate_ulysses=False):
    """Perform a Ulysses action and return json restored result.

    action -- the name of the Ulysses action to perform
    params -- dictionary of parameters to pass with call. None entries will
              be removed before sending.
    send_access_token -- append access-token in params if True
    silent-mode -- append silent-mode=YES to params if True. This prevents
                   actions which alter Ulysses content from bring Ulysses
                   forward.
    """

    if send_access_token:
        params['access-token'] = token_provider.token
    if silent_mode:
        params['silent-mode'] = 'YES'

    return ULYSSES_XCALL.xcall(action, params, activate_app=activate_ulysses)


def isID(value):
    """Checks if value looks like a Ulysses ID; i.e. is 22 char long.

    Not an exact science; but good enougth to prevent most mistakes.
    """
    return len(value) == 22
