#!/usr/bin/env python3

import logging
from config import *

def getLogger():
    logger = logging.getLogger("musebot")
    logger.setLevel(logging.DEBUG)
    f = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')
    h = None
    if DEBUG_TO_FILE:
        h = logging.FileHandler(DEBUG_FILE)
    else:
        h = logging.StreamHandler()
   h.setFormatter(f)
   logger.addHandler(h)

   return logger
