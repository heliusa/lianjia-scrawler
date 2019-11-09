# -*- coding: utf-8 -*-
import datetime
import time
from stack import Stack
import settings
from util.logger import logging

class Tracking(object):
    
    def __init__(self):
        self.stack = Stack()

    def start(self, name = None):
        if name: 
            logging.info(name)
        self.stack.push(datetime.datetime.now())
        return self;

    def end(self):
        endtime =  datetime.datetime.now()
        
        if not self.stack.is_empty():
            starttime = self.stack.pop()
            logging.info("time: %s", starttime)
            logging.info("Run time: %s", endtime - starttime)

        return self;

    def reset(self):
        self.stack.clear()
        return self;

    def log_progress(self, function, address, page, total):
        logging.info("Progress: %s %s: current page %d total pages %d" %
            (function, address, page, total))
        return self;