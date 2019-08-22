#!/usr/bin/env python3

from ..testbase import TestBase
from ..testLib.musebot import MuseBot

import os
from random import randint

class WebhooksTest(TestBase):
    def test(self):
        base = "./tests/testQueue/"
        files = ["push.txt"]

        for file in files:
            try:
                os.stat(base + file)
            except:
                print("The expected hook {} was not found".format(file))
                self.expect(False)

        instance = MuseBot()
        instance.integrate(randint(-2492832, 2382852))
        instance.getWebhooks()

        for file in files:
            try:
                os.stat(base + file)
            except FileNotFoundError:
                pass
            else:
                print("The hook {} has not been removed".format(file))
                self.expect(False)

test = WebhooksTest("Webhook", "the webhook events in the test queue are properly handled")
