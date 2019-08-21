#!/usr/bin/env python3

"""Generators for the rules that allow the command parser to parse MuseBot messages"""

from ..config import *
from .commandParser import Token

def getPRGrammar():
    # PR triggers the pull request parsing
    prStart = Token(PR_IDENT, r"[pP]")
    rChar = prStart.addNext(Token(PR_IDENT, r"[rR]"))

    # Branch off to allow whitespace, which can loop back into itself
    ws = rChar.addNext(Token(PR_IDENT, r"\s"))
    ws.loopback()

    # A hash indicates the start of the number
    hashChar = rChar.addNext(Token(PR_IDENT, r"#"))
    ws.addNext(hashChar)

    # The hash can be followed by whitespace or a digit
    ws = hashChar.addNext(Token(PR_IDENT, r"\s"))
    ws.loopback()

    # Check for a digit, which can loop back into itself
    digit = hashChar.addNext(Token(PR_IDENT, r"[0-9]", collect="number"))
    ws.addNext(digit)
    digit.loopback()

    # Add a terminator
    digit.addNext(Token(PR_IDENT, r"[^0-9]"))
    return prStart


def getNodeGrammar():
    # Node collection is triggered by a hash
    nodeStart = Token(NODE_IDENT, r"#")

    # Loopable whitespace can follow this
    ws = nodeStart.addNext(Token(NODE_IDENT, r"\s"))
    ws.loopback()

    # A digit must come, which can loop into iteelf
    digit = nodeStart.addNext(Token(NODE_IDENT, r"[0-9]", collect="number"))
    ws.addNext(digit)
    digit.loopback()

    # This is terminated
    digit.addNext(Token(NODE_IDENT, r"[^0-9]"))
    return nodeStart


def getCommandGrammar():
    # Commands are initiated by a forward slash
    cmdStart = Token(CMD_IDENT, r"/")

    # Anything goes, apart from whitespace and @. This loops back
    cmdChar = cmdStart.addNext(Token(CMD_IDENT, r"[^@\s]", collect="cmd"))
    cmdChar.loopback()

    # Whitespace ends a command, always
    ws = cmdChar.addNext(Token(CMD_IDENT, r"\s"))

    # ...but if an @ follows, check for the username string following it
    last = cmdChar.addNext(Token(CMD_IDENT, r"@"))

    for c in USERNAME:
        last = last.addNext(Token(CMD_IDENT, c))

    # And terminate the bot name with whitespace
    last.addNext(ws)
    return cmdStart


def getAllGrammar():
    """Returns a master token with all possible grammars following it.

    The master token should be used with the CommandParser as the starting point.
    """

    master = Token("master", r"\[^]")

    master.addNext(getPRGrammar())
    master.addNext(getNodeGrammar())
    master.addNext(getCommandGrammar())

    return master
