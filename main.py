# -*- coding: utf-8 -*-


'''
Created on 15 Apr 2017

@author: walton
'''



from subprocess import Popen, PIPE
import json
import urllib
from pprint import pprint
from ulysses_client.xcall_ulysses import xcall
from ulysses_client import ulysses as upc
from test.test_ulysses import MANUALLY_CONFIGURED_TOKEN
from ulysses_client import xcall_ulysses
# url = 'ulysses://x-callback-url/get-item?access-token=c6e4ef1a29e44e62acdcee4e5eabc423&recursive=NO&id=v_u1RvMlGjJHqofzWdvCNw'
# p = Popen(['bin/xcall.app/Contents/MacOS/xcall', '-url', url],
#           stdout=PIPE, stderr=PIPE)
# stdout, stderr = p.communicate()
# print 'stdout = ', stdout
# 
# 
# 
# 
# d = json.loads(urllib.unquote(stdout).decode('utf8'))
# print 'd:'
# pprint(d)
# 
# 
# print json.loads(urllib.unquote(d['item']))['title']
# 
# print '-' * 79
# d = xcall(url)
# 
# print json.loads(urllib.unquote(d['item']))['title']
# 
# print '-' * 79
xcall_ulysses.token_provider.token = MANUALLY_CONFIGURED_TOKEN
# item = upc.get_item('v_u1RvMlGjJHqofzWdvCNw')
# print u'\u2018'
# s = item.__str__()
# print s
# print item
# 
# print '*' * 79


title = u'test_set_sheet_title -- ups test ‘quoted text’ forward / back  semicolon: ampersand & plus +'
title = u"""abcd () \ / ? & xyz ' " ‘quoted text’ - end"""
title  = urllib.quote(title.encode('utf8'))
url = 'ulysses://x-callback-url/set-sheet-title?access-token=c6e4ef1a29e44e62acdcee4e5eabc423&id=JCp8o14KuumTzO1KuYQisw&title=%s&type=heading2' % title
# url = 'ulysses://x-callback-url/get-version'

from subprocess import Popen, PIPE
p = Popen(['bin/xcall.app/Contents/MacOS/xcall', '-url', url],
          stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()

print 'stdout' + stdout
print 'stderr' + stderr
#upc.set_sheet_title('JCp8o14KuumTzO1KuYQisw', title, 'heading2')
# reply = call_ulysses('get-item', {'id': TESTID}, send_access_token=True)
# item = json.loads(urllib.unquote(reply['item']))
# 
# test_sheet = upc.get_item(TESTID, recursive=False)
# print test_sheet