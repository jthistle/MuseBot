#!/usr/bin/env python3

from ..testbase import TestBase, TestFailure
from ..testLib.grammar.grammars import getAllGrammar
from ..testLib.grammar.commandParser import CommandParser

class Test(TestBase):
    def test(self):
        master = getAllGrammar()
        parser = CommandParser(master)

test = Test("Grammars", "each grammar generator generates a grammar readable by the command parser")
