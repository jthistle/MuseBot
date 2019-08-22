#!/usr/bin/env python3

from ..testbase import TestBase
from ..testLib.grammar.grammars import getAllGrammar
from ..testLib.grammar.commandParser import CommandParser
from ..testLib.config import *

class Test(TestBase):
    def test(self):
        master = getAllGrammar()
        parser = CommandParser(master)

        commands = [
            ("/help", CMD_IDENT, "help"),
            ("#356", NODE_IDENT, "356"),
            ("pr #5000", PR_IDENT, "5000"),
            ("# 420", NODE_IDENT, "420"),
            ("p r #2324", NODE_IDENT, "2324"),
            (" /integrate  ", CMD_IDENT, "integrate"),
            ("pr        #   123", PR_IDENT, "123"),
            ("#0016", NODE_IDENT, "0016"),
            ("#a342", 0),
            ("/help@cheesebot", 0),
            ("/help@" + USERNAME, CMD_IDENT, "help"),
        ]

        for cmd in commands:
            parsed = parser.parse(cmd[0])

            if cmd[1] is 0:
                self.expect(len(parsed) is 0)
            else:
                self.expect(len(parsed) > 0)

                command = parsed[0]
                value = None
                if command.ident == CMD_IDENT:
                    value = command.data["cmd"]
                else:
                    value = command.data["number"]

                self.expect(cmd[1] == command.ident)
                self.expect(cmd[2] == value)

test = Test("Parse commands", "certain commands are parsed correctly")
