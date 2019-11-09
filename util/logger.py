# -*- coding: utf-8 -*-
import datetime
import logging
import time
import settings
import sys

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s', level=logging.INFO, filename=settings.LOG_PATH + time.strftime('%Y-%m-%d') +'.log', filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
console.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(console)

def log_progress(self, function, address, page, total):
    logging.info("Progress: %s %s: current page %d total pages %d" %
            (function, address, page, total))
    return self;