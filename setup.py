#!/usr/bin/env python
from setuptools import setup
import sys
import platform

__VERSION__ = "1.0" 

requires = []
if sys.version_info < (2,7):
    requires = ['simplejson']
    requires.append('argparse')

setup(
    name = "pcl",
    version = __VERSION__,
    url = 'http://idning.github.com/',
    author = 'ning',
    author_email = 'idning@gmail.com',
    description = "python common libs",
    long_description=open('README.rst').read(),
    packages = ['pcl'],
    include_package_data = True,
    install_requires = requires,
    scripts = [],
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
)

