#
# Copyright (c) 2016 Rob Walton <dhttps://github.com/robwalton>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-04-17


import pytest

import ulysses.xcallback

from tests.ulysses.test_calls import MANUALLY_CONFIGURED_TOKEN


# See comment in test_Calls.py on how to set MANUALLY_CONFIGURED_TOKEN

def test_connection():
    assert ulysses.xcallback.call_ulysses('get-version')['apiVersion'] >= 2


def test_action_with_access_token():
    ulysses.xcallback.set_access_token(MANUALLY_CONFIGURED_TOKEN)
    ulysses.xcallback.call_ulysses('get-root-items', locals(),
                                   send_access_token=True)


def test_xerror():
    with pytest.raises(ulysses.xcallback.UlyssesError) as excinfo:
        ulysses.xcallback.call_ulysses('an-invalid-action')
    assert 'Invalid Action. Code=100.' in str(excinfo.value)
