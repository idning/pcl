#!/usr/bin/env python
#coding: utf-8
#file   : example.py
#author : ning
#date   : 2012-11-14 14:39:26


import urllib, urllib2
import os, sys
import re, time
import logging

from common import *

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


if __name__ == "__main__":
    main()

