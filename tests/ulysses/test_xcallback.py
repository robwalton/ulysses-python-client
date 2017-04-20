#
# Copyright (c) 2016 Rob Walton <dhttps://github.com/robwalton>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-04-17


import pytest

from ulysses.xcallback import call_ulysses, UlyssesError


def test_connection():
    assert call_ulysses('get-version')['apiVersion'] >= 2


def test_xerror():
    with pytest.raises(UlyssesError) as excinfo:
        call_ulysses('an-invalid-action')
    assert 'Invalid Action. Code=100.' in str(excinfo.value)


# Note: should technically test access-token & silent mode
