
import xcallbackurl
import time
import pytest
from xcallbackurl import XCallbackError
import urlparse


class TestCallback:
    
    def test_urlcall(self):
        reply = xcallbackurl.urlcall('ulysses-python-client://xyz')   
        assert reply == 'ulysses-python-client://xyz'

    @pytest.mark.skip(reason="speed test takes quite long")
    def test_speed_or_urlcall(self):
        t_start = time.time()
        n = 10
        for i in range(n):
            reply = xcallbackurl.urlcall('ulysses-python-client://%i' % i) 
            assert reply == 'ulysses-python-client://%i' % i
        dt = time.time() - t_start
        time_per_run = dt / n
        assert time_per_run < .3



def test_decode_reply():
    msg = 'ulysses-python-client://x-callback-url/success?key1=val1&key2=val2'
    assert xcallbackurl.decode_reply(msg) == {'key1': 'val1', 'key2': 'val2'}


def test_decode_reply_with_error():
    msg = 'ulysses-python-client://x-callback-url/error?errorMessage=Invalid%20Action&errorCode=100'
    with pytest.raises(XCallbackError) as excinfo:
        xcallbackurl.decode_reply(msg)
    assert 'Invalid Action. Code = 100' in str(excinfo.value)


# SplitResult(scheme='ulysses-python-client', netloc='x-callback-url', path='/success', query='buildNumber=33496&apiVersion=2', fragment='')

def test_encode_request():
    action_parameter_dict = {'param1': 'val1', 'param2': 'val2'}
    result = xcallbackurl.encode_request('some-action', action_parameter_dict)
    
    split_result = urlparse.urlsplit(result)
    args = urlparse.parse_qs(split_result.query)
    for k,v in args.iteritems():
        args[k] = v[0]  # pull values out of the list parse_qs results in
    
    desired_args = {
        'x-success': 'ulysses-python-client://x-callback-url/success',
        'x-error': 'ulysses-python-client://x-callback-url/error'    
        } 
    desired_args.update(action_parameter_dict)
    
    assert split_result.scheme == 'ulysses'
    assert split_result.netloc == 'x-callback-url'
    assert split_result.path == '/some-action'
    assert args == desired_args



        