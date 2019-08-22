#!/usr/bin/env python3

"""Decorators for functions that should be mocked during tests"""

from .config import *

def mockedAPIRequest(func):
    def wrapper(self, cmd, data=None):
        if TESTING:
            print("Prevented a request with command {}, data: {}".format(cmd, data))
            return {}
        else:
            return func(self, cmd, data)
    return wrapper
