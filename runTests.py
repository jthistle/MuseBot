#!/usr/bin/env python3

import sys

from tests.grammar.grammars import test as grammarTest
from tests.grammar.parseCommands import test as parseCommandsTest
from tests.musebot.webhooks import test as webhookTest
from tests.musebot.messages import test as messagesTest

tests = [
    grammarTest,
    parseCommandsTest,
    webhookTest,
    messagesTest,
]

if __name__ == "__main__":
    print("Running tests...")

    failures = 0
    successes = 0
    for test in tests:
        success = test.run()
        if not success:
            failures += 1
        else:
            successes += 1

    print("\nOVERALL: {} failure{}, {} pass{}".format(
        failures,
        "s" if failures != 1 else "",
        successes,
        "es" if successes != 1 else ""
    ))

    if failures > 0:
        print("\nThe test suite finished with failures.")
        sys.exit(1)
    else:
        print("\nThe test suite passed.")
        sys.exit(0)
