#!/usr/bin/python
#coding: utf-8
#file   : httpc_test_client.py
#author : ning
#date   : 2012-03-07 20:47:45


import urllib, urllib2
import os, sys
import re, time
import logging
from common import init_logging, shorten
from httpc import *

init_logging(logger, logging.INFO)

URL = 'http://localhost:8000/'
tmp_file = 'test_pyhttpc.tmp'

def _test_http_client(http_client_class, url, add_header, local_file):
    c = http_client_class()
    
    body = file(local_file).read()
    rst = {}
    rst['get'] = c.get(url, add_header)
    ##rst['head'] = c.head(url) bad!!!!!!!!!!!
    rst['put'] = c.put(url, body, add_header)
    rst['post'] = c.post(url, body, add_header)
    rst['post_multipart']           = c.post_multipart(url, local_file, 'file1', {'k':'v'}, add_header)
    rst['post_multipart_only_field']= c.post_multipart(url, None,       None,    {'k':'v'}, add_header)
    rst['post_multipart_only_file'] = c.post_multipart(url, local_file, 'file2', {},        add_header)

    rst['delete'] = c.delete(url, add_header)

    rst['put_file'] = c.put_file(url, local_file, add_header)
    if len(body) > 8:
        rst['put_file_part']    = c.put_file_part(url, local_file, 1, 8, add_header)
        rst['put_file_part_2']  = c.put_file_part(url, local_file, 1, len(body)-1, add_header)

    rst['get_file'] = c.get_file(url, tmp_file, add_header)
    rst['get_file']['body'] = file(tmp_file).read()
    return rst

header_cases = [
    {},
    {'header1': 'header_value1'}, 
    {'header1': 'header_value1',  'Content-Disposition': 'abc'},
]

body_cases = [
    'testdata/0.data',
    'testdata/9.data',
]

body_cases2 = [ # curl httpclient , 显然不支持换行.
    'httpc.pyc',
    'testdata/600K.data',
    'testdata/10M.data',
]

query_string_case = [
    '',
    '?a=b',
    '?a=b&c=d',
    '?a=b&c=d#xxxxxxx',
]

def test2():
    assert select_best_httpc() == PyCurlHTTPC


def test1():
    i = 0
    for add_header in header_cases:
        for local_file in body_cases + body_cases2:
            for qs  in query_string_case:
                url = URL + str(i)  + qs
                r1 = _test_http_client(PyCurlHTTPC, url, add_header, local_file)
                if local_file not in body_cases2:
                    r2 = _test_http_client(CurlHTTPC, url, add_header, local_file)
                r3 = _test_http_client(HttplibHTTPC, url, add_header, local_file)
                for k in r1.keys():
                    print 'cmpare for ' + k
                    print 'r1:' + shorten(r1[k]['body'])
                    if local_file not in body_cases2:
                        print 'r2:' + shorten(r2[k]['body'])
                    print 'r3:' + shorten(r3[k]['body'])

                    if local_file not in body_cases2:
                        assert( r1[k]['body'] == r2[k]['body'] )
                    assert( r1[k]['body'] == r3[k]['body'] )
                i += 1

def main():
    test1()
    test2()
    #test3()

main()
#_test_http_client(HttplibHTTPC)
#HttplibHTTPC().post_multipart(url, local_file, 'file1')
