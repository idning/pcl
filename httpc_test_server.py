#!/usr/bin/env python
#coding: utf-8
#file   : httpc_test.py
#author : ning
#date   : 2012-03-07 20:09:13


import urllib, urllib2
import os, sys
import re, time
import logging
import argparse

import os
import cgi
import sys
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
 
#do one thing:
#dump method url , headers, body in response body

class ningHandler(BaseHTTPRequestHandler):
    def dump(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('[method] %s\n' % self.command)
        self.wfile.write('[url] %s\n' % self.raw_requestline)
        headers = self.headers.items()
        headers.sort()
        for (k,v) in headers: 
            if k not in ['accept', 'accept-encoding', 'user-agent', 'expect', 'content-type']:
                self.wfile.write('[header] %s => %s\n' % (k, v))

        if 'Content-Length' in self.headers:
            body_size = int(self.headers['Content-Length'])
            data = self.rfile.read(body_size)
        else:
            body_size = 0
            data = ''
        self.wfile.write('[body_size] %d\n'% body_size)
        self.wfile.write(data)

        self.wfile.close()
        return 

    def do_GET(self):
        self.dump()

    def do_HEAD(self):
        self.dump()
            
    def do_PUT(self):
        self.dump()

    def do_DELETE(self):
        self.dump()

    def do_POST(self):
        ctype,pdict = cgi.parse_header(self.headers.getheader('Content-type'))
        if ctype == 'multipart/form-data':
            query = cgi.parse_multipart(self.rfile, pdict)
            self.send_response(200)
            self.end_headers()
            self.wfile.write('POST multipart')
            self.wfile.write(str(query))
            self.wfile.close()
        else:
            self.dump()
    

def getport():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8000,
                        help="port ") 
    args = parser.parse_args()
    return args.port

def server():
    try:
        server = HTTPServer(('',getport()),ningHandler)
        print 'server started at port 8080'
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close() 

if __name__=='__main__':
    server()
