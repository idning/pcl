#!/usr/bin/python                                                                                                                                                                                              

import sys, re
usage = """
USAGE: 
    ./gen.py 1M 
    ./gen.py 1K 
    ./gen.py 600K > 600K.data
"""
if len(sys.argv) != 2:
    print usage
    sys.exit()

sizestr = re.search(r'(\d*)', sys.argv[1]).group(1)
size = int(sizestr)
#print size

if sys.argv[1].find("k") > 0 or sys.argv[1].find("K") > 0 :
    size=size*1024
if sys.argv[1].find("m") > 0 or sys.argv[1].find("M") > 0 :
    size=size*1024*1024
#print size

#this is ok:
for i in range(size/16):
    ii = i * 16
    sys.stdout.write('%015x\n' % ii)

for i in range(size%16):
    sys.stdout.write('-')

