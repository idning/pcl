#!/usr/bin/env python
#coding: utf-8
#file   : cron.py
#author : ning
#date   : 2014-01-06 17:13:23

#cron, we do the task in the main thread, so do not add task run more than 1 minutes
#you can start thread in your task

import time
import logging
from datetime import datetime

class Event(object):
    def __init__(self, desc, func, args=(), kwargs={}):
        """
        desc: min hour day month dow
            day: 1 - num days
            month: 1 - 12
            dow: mon = 1, sun = 7
        """
        self.desc = desc 
        self.func = func
        self.args = args
        self.kwargs = kwargs

    #support: 
    # * 
    # 59
    # 10,20,30
    def _match(self, value, expr):
        #print 'match', value, expr
        if expr == '*':
            return True
        values = expr.split(',')
        for v in values:
            if int(v) == value:
                return True
        return False

    def matchtime(self, t):
        mins, hour, day, month, dow = self.desc.split()
        return self._match(t.minute       , mins)  and\
               self._match(t.hour         , hour)  and\
               self._match(t.day          , day)   and\
               self._match(t.month        , month) and\
               self._match(t.isoweekday() , dow)

    def check(self, t):
        if self.matchtime(t):
            try: 
                self.func(*self.args, **self.kwargs)
            except Exception, e:
                logging.exception(e)

class Cron(object):
    def __init__(self):
        self.events = []

    def add(self, desc, func):
        self.events.append(Event(desc, func))

    def run(self):
        while True:
            #wait to a new minute start
            t = time.time()
            next_minute = t - t%60 + 60
            while t < next_minute:
                sleeptime = 60 - t%60
                logging.info('current time: %s, we will sleep %.2f seconds' %(t, sleeptime))
                time.sleep(sleeptime)
                t = time.time()

            current = datetime(*datetime.now().timetuple()[:5])
            for e in self.events:
                e.check(current)
            time.sleep(1)

def main():
    def minute_task():
        print 'minute_task @ %s' % time.time()
    def day_task():
        print 'day_task @ %s' % time.time()

    cron = Cron()
    cron.add('* * * * *', minute_task) # every minute 
    cron.add('33 * * * *', day_task)    # erery hour
    cron.add('34 18 * * *', day_task)  # every day
    cron.run()

if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
