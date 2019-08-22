#!/usr/bin/env python3

import logging
from .config import *

def initLogger():
    """Set up the logger. Only use this once, preferably before any calls to getLogger."""
    logger = logging.getLogger("musebot")
    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    f = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')
    h = None
    if DEBUG_TO_FILE:
        h = logging.FileHandler(DEBUG_FILE)
    else:
        h = logging.StreamHandler()
    h.setFormatter(f)
    logger.addHandler(h)
    return logger

def getLogger():
    """Returns a logger configured in a consistent way"""
    return logging.getLogger("musebot")
