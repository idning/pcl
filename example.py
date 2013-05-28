#!/usr/bin/env python
#coding: utf-8
#file   : example.py
#author : ning
#date   : 2012-11-14 14:39:26


import urllib, urllib2
import os, sys
import re, time
import logging

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + './')

from pcl.common import *
from pcl import httpc

logger = logging.getLogger('pyhttpclient')
init_logging(logger, logging.DEBUG)

def test_httpc():
    c = httpc.CurlHTTPC()
    c = httpc.HttplibHTTPC()
    resp = c.get('http://www.baidu.com')
    print resp['header']

def test_ddict():

    a = Ddict(dict)
    a['3']['8'] = 1
    a['3']['9'] = 1
    print a

    b = Ddict(int)
    b['3'] += 5
    print b

    c = Ddict(list)
    c['3'].append('xx')
    c['3'].append('yy')
    print c

    def gen_ddict():
        return Ddict(int)

    d = Ddict(gen_ddict)
    d['3']['5']+=2
    d['3']['8']+=7
    print d

def main():
    """docstring for main"""
    test_ddict()
    test_httpc()


if __name__ == "__main__":
    main()


