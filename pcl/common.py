#!/usr/bin/env python
#coding:utf8
import urllib
import urllib2
import httplib
import cookielib
import os
import re
import sys
import time
import logging 
import hmac
import base64
import hashlib
import commands
import mimetypes
import json
import getopt


from cStringIO import StringIO
#from abc import abstractmethod
from urlparse import urlparse
from datetime import datetime

class FileSystemException(Exception):
    def __init__(self, msg=''):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return 'FileSystemException: ' + str(self.msg)

class NotImplementException(Exception):
    def __init__(self, msg=''):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return 'NotImplementException: ' + str(self.msg)


class Ddict(dict):
    def __init__(self, default=dict):
        self.default = default

    def __getitem__(self, key):
        if not self.has_key(key):
            self[key] = self.default()
        return dict.__getitem__(self, key)   


def retry(ExceptionToCheck, tries=4, delay=2, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        excpetions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            try_one_last_time = True
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                    try_one_last_time = False
                    break
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if try_one_last_time:
                return f(*args, **kwargs)
            return
        return f_retry  # true decorator
    return deco_retry

###########################################################
# color system
###########################################################
class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.RED = ''
        self.ENDC = ''

def to_red(s):       return  bcolors.RED+ str(s) + bcolors.ENDC
def to_yellow(s):    return  bcolors.YELLOW+ str(s) + bcolors.ENDC
def to_green(s):     return  bcolors.GREEN + str(s) + bcolors.ENDC
def to_blue(s):      return  bcolors.BLUE+ str(s) + bcolors.ENDC


###########################################################
# misc
###########################################################
def shorten(s, l=80):
    if len(s)<=l:
        return s
    return s[:l-3] + '...'

#commands dose not work on windows..
def system(cmd, log_fun=logging.info):
    if log_fun: log_fun(cmd)
    r = commands.getoutput(cmd)
    return r
	
#def system(cmd, log_fun=logging.info):
    #if log_fun: log_fun(cmd)
    #from subprocess import Popen, PIPE
    #p = Popen(cmd, shell=True, bufsize = 102400, stdout=PIPE)
    #p.wait()
    #r = p.stdout.read()
    #return r

def md5_for_file(f, block_size=2**20):
    f = open(f, 'rb')
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()

def md5_for_content(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def first_second(cur, period='all'):
    '''
    cur=datetime.now()
    '''
    if (period=='all'):
        return datetime(1970,1,1)
    if (period=='year'):
        return datetime(cur.year, 1, 1)
    if (period=='month'):
        return datetime(cur.year, cur.month, 1)
    if (period=='day'):
        return datetime(cur.year, cur.month, cur.day)
    if (period=='hour'):
        return datetime(cur.year, cur.month, cur.day, cur.hour)
    if (period=='min'):
        return datetime(cur.year, cur.month, cur.day, cur.hour,cur.minute)
    return None

#period_arr = ['all', 'year', 'month', 'day', 'hour', 'min']
period_arr = ['month', 'day', 'hour', 'min']
def test_first_second():
    for p in period_arr:
        print first_second(datetime.now(), p)


def parse_size(input):
    K = 1024
    M = K * K
    G = M * K
    T = G * K
    sizestr = re.search(r'(\d*)', input).group(1)
    size = int(sizestr)
    if input.find("k") > 0 or input.find("K") > 0 :
        size=size*K
    if input.find("m") > 0 or input.find("M") > 0 :
        size=size*M
    if input.find("g") > 0 or input.find("G") > 0 :
        size=size*G
    if input.find("t") > 0 or input.find("T") > 0 :
        size=size*T
    return size

def format_size(input):
    input = int(input)
    K = 1024.
    M = K * K
    G = M * K
    T = G * K
    if input >= T: return '%.2fT' % (input /  T)
    if input >= G: return '%.2fG' % (input /  G)
    if input >= M: return '%.2fM' % (input /  M)
    if input >= K: return '%.2fK' % (input /  K)
    return '%d' % input


def format_time(timestamp=None, fmt='%Y-%m-%d %X'):
    if not timestamp:
        timestamp = time.time()
    t = datetime.fromtimestamp(float(timestamp))
    return t.strftime(fmt)

def format_time_to_hour(timestamp=None):
    return format_time(timestamp, '%Y%m%d%H')
def format_time_to_min(timestamp=None):
    return format_time(timestamp, '%Y%m%d%H%M')

class ColorFormatter(logging.Formatter):
    '''
    cool class
    '''
    Black            = '0;30'
    Red              = '0;31'
    Green            = '0;32'
    Brown            = '0;33'
    Blue             = '0;34'
    Purple           = '0;35'
    Cyan             = '0;36'
    Light_Gray       = '0;37'
                     
    Dark_Gray        = '1;30'
    Light_Red        = '1;31'
    Light_Green      = '1;32'
    Yellow           = '1;33'
    Light_Blue       = '1;34'
    Light_Purple     = '1;35'
    Light_Cyan       = '1;36'
    White            = '1;37'

    COLORS = {
        'DEBUG'    : Dark_Gray, #WHITE
        'INFO'     : Light_Blue,
        'NOTICE'   : Light_Green,
        'WARNING'  : Yellow,
        'ERROR'    : Light_Red,
        'CRITICAL' : Yellow,
    }

    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[%sm"
    BOLD_SEQ  = "\033[1m"

    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        color     = ColorFormatter.COLOR_SEQ % (ColorFormatter.COLORS[levelname])
        message   = logging.Formatter.format(self, record)
        return color + message + ColorFormatter.RESET_SEQ

logging.ColorFormatter = ColorFormatter

'''
set_level 设为
'''
def init_logging(logger, set_level = logging.INFO, 
        console = True,
        log_file_path = None):

    logger.setLevel(logging.DEBUG)
    logger.propagate = False # it's parent will not print log (especially when client use a 'root' logger)
    for h in logger.handlers:
        logger.removeHandler(h)
    if console:
        fh = logging.StreamHandler()
        fh.setLevel(set_level)
        formatter = logging.ColorFormatter("%(asctime)-15s [%(threadName)s] [%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    if log_file_path:
        from logging.handlers import TimedRotatingFileHandler

        fh = TimedRotatingFileHandler(log_file_path, backupCount=24*5, when='midnight')
        fh.setLevel(set_level)
        formatter = logging.Formatter("%(asctime)-15s [%(threadName)s] [%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

def parse_args(func, log_filename='stat.log'):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdvw", ["help", "debug", "verbose", "hour"])
    except getopt.GetoptError:
        usage()
        sys.exit(0)
    verbose = 0
    debug = False

    for o, a in opts:
        if o == "-d":
            verbose = True
            debug = True
        if o == "-v":
            verbose += 1
        if o in ("-h", "--help"):
            usage()
            sys.exit()
    log_path = os.path.dirname(os.path.realpath(__file__)) + '/../log/' + log_filename
    if verbose == 0:
        init_logging(logging.root, logging.INFO, False, log_path)
    elif verbose == 1:
        init_logging(logging.root, logging.INFO, True, log_path)
    elif verbose > 1:
        init_logging(logging.root, logging.DEBUG, True, log_path)

    func(args)

# add @ 20130625
def parse_args2(default_log_filename='xxx.log', parser = None):
    import argparse
    if not parser:
        parser= argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', action='count', help="verbose", default=0) 
    parser.add_argument('-o', '--logfile', default=default_log_filename) 

    #(args, remaining) = parser.parse_known_args()
    args = parser.parse_args()
    #print args
    #print args.logfile
    #print args.verbose
    #loggers = [logging.root, logging.getLogger('pyhttpclient')]
    loggers = [logging.root]
    if args.verbose == 0:
        for logger in loggers:
            init_logging(logger, logging.INFO, False, args.logfile)
    elif args.verbose == 1:
        for logger in loggers:
            init_logging(logger, logging.INFO, True, args.logfile)
    elif args.verbose > 1:
        for logger in loggers:
            init_logging(logger, logging.DEBUG, True, args.logfile)

    logging.info("start running: " + ' '.join(sys.argv))
    logging.info(args)
    return args

#add a NOTICE log level
'''
the python logging levels:

debug               10
info (trace)        20
notice              ??  we use 25
warning             30
error               40
fatal/critical      50

we add a notice to it

'''

logging.NOTICE = 25

logging.addLevelName(logging.NOTICE, 'NOTICE')

# define a new logger function for notice
# this is exactly like existing info, critical, debug...etc
def Logger_notice(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'NOTICE'.

    To pass exception information, use the keyword argument exc_info
with
    a true value, e.g.

    logger.notice("Houston, we have a %s", "major disaster", exc_info=1)
    """
    if self.manager.disable >= logging.NOTICE:
        return
    if logging.NOTICE >= self.getEffectiveLevel():
        apply(self._log, (logging.NOTICE, msg, args), kwargs)

# make the notice function known in the system Logger class
logging.Logger.notice = Logger_notice

# define a new root level notice function
# this is exactly like existing info, critical, debug...etc
def root_notice(msg, *args, **kwargs):
    """
    Log a message with severity 'NOTICE' on the root logger.
    """
    if len(logging.root.handlers) == 0:
        basicConfig()
    apply(logging.root.notice, (msg,)+args, kwargs)

# make the notice root level function known
logging.notice = root_notice

# add NOTICE to the priority map of all the levels
#logging.handlers.SysLogHandler.priority_map['NOTICE'] = 'notice'



import json
from time import mktime

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

#print json.dumps(obj, cls = MyEncoder)

def json_encode(j):
    return json.dumps(j, indent=4, cls=MyEncoder)

def json_decode(j):
    return json.loads(j)


#class ConsoleLogging():
    #'''
    #对于console类型的应用, 如mongodeploy, bcsh 之类, 在段时间内在console运行，记录日志通常是没有必要的. 
    #此时有颜色的console logging会更加合适.

    #'''
    #@staticmethod
    #def debug(msg):
        #print('[DEBUG] ' + msg)

    #@staticmethod
    #def info(msg):
        #print to_green('[INFO] ' + msg)

    #@staticmethod
    #def warn(msg):
        #print to_yellow('[WARN]' + msg)

    #@staticmethod
    #def error(msg):
        #print to_red('[ERROR] ' + msg)

#console_logging = ConsoleLogging()


import sys, time
from select import select

import platform
if platform.system() == "Windows":
    import msvcrt

def input_with_timeout_sane(prompt, timeout, default):
    """Read an input from the user or timeout"""
    print prompt,
    sys.stdout.flush()
    rlist, _, _ = select([sys.stdin], [], [], timeout)
    if rlist:
        s = sys.stdin.readline().replace('\n','')
    else:
        s = default
        print s
    return s

def input_with_timeout_windows(prompt, timeout, default): 
    start_time = time.time()
    print prompt,
    sys.stdout.flush()
    input = ''
    while True:
        if msvcrt.kbhit():
            chr = msvcrt.getche()
            if ord(chr) == 13: # enter_key
                break
            elif ord(chr) >= 32: #space_char
                input += chr
        if len(input) == 0 and (time.time() - start_time) > timeout:
            break
    if len(input) > 0:
        return input
    else:
        return default

def input_with_timeout(prompt, timeout, default=''):
    if platform.system() == "Windows":
        return input_with_timeout_windows(prompt, timeout, default)
    else:
        return input_with_timeout_sane(prompt, timeout, default)

def test_colors():
    colors = [
        ('Black'            , '0;30'),
        ('Red'              , '0;31'),
        ('Green'            , '0;32'),
        ('Brown'            , '0;33'),
        ('Blue'             , '0;34'),
        ('Purple'           , '0;35'),
        ('Cyan'             , '0;36'),
        ('Light_Gray'       , '0;37'),
        
        ('Dark_Gray'        , '1;30'),
        ('Light_Red'        , '1;31'),
        ('Light_Green'      , '1;32'),
        ('Yellow'           , '1;33'),
        ('Light_Blue'       , '1;34'),
        ('Light_Purple'     , '1;35'),
        ('Light_Cyan'       , '1;36'),
        ('White'            , '1;37'),
    ]
    COLOR_SEQ = "\033[%sm"
    RESET_SEQ = "\033[0m"
    for c in colors: 
        print COLOR_SEQ % c[1] + c[0] + RESET_SEQ


if __name__ == "__main__":
    test_colors()
