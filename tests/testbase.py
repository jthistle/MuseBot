#!/usr/bin/env python3

import traceback

class TestFailure(Exception):
    """A class to distinguish failures from errors"""
    pass

class TestBase:
    """The base class for a test. You must add a `test` function to it for it to be run."""
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc

    def expect(self, condition):
        if not condition:
            raise TestFailure("The expected condition was not met")

    def run(self):
        print("\n==== Running test: ", self.name)
        print("It tests that", self.desc)
        try:
            self.test()
        except TestFailure as e:
            print("\nFAIL: The test failed: {}".format(e))
            traceback.print_exc()
            return False
        except Exception as e:
            print("\nERROR: An error occured during the test: {}".format(e))
            traceback.print_exc()
            return False
        print("\nPASS: The test passed")
        return True
