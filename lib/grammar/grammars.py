#!/usr/bin/env python3

from ..config import *
from commandParser import Token

def getPRGrammar():
    # PR triggers the pull request parsing
    prStart = Token(PR_IDENT, "[pP]")
    end = prStart.addNext(Token(PR_IDENT, "[rR]"))

    # Branch off to allow whitespace, which can loop back into itself
    ws = end.addNext(Token(PR_IDENT, "\\s"))
    ws.addNext(ws)

    # A hash indicates the start of the number
    end = end.addNext(Token(PR_IDENT, "#"))
    ws.addNext(end)

    # The hash can be followed by whitespace or a digit
    ws = end.addNext(Token(PR_IDENT, "\\s"))
    ws.addNext(ws)

    # Check for a digit, which can loop back into itself
    end = end.addNext(Token(PR_IDENT, "[0-9]", collect="number"))
    end.addNext(end)
    ws.addNext(end)

    # Add a terminator
    end.addNext(Token(PR_IDENT, "[^0-9]"))
    return prStart


def getNodeGrammar():
    # Node collection is triggered by a hash
    nodeStart = Token(NODE_IDENT, "#")

    # Loopable whitespace can follow this
    ws = nodeStart.addNext(Token(NODE_IDENT, "\\s"))
    ws.addNext(ws)

    # A digit must come
    end = nodeStart.addNext(Token(NODE_IDENT, "[0-9]", collect="number"))
    ws.addNext(end)

    # This is terminated
    end.addNext(Token(NODE_IDENT, "[^0-9]"))
    return nodeStart


def getCommandGrammar():
    # Commands are initiated by a forward slash
    cmdStart = Token(CMD_IDENT, "/")

    # Anything goes, apart from whitespace and @. This loops back
    end = cmdStart.addNext(Token(CMD_IDENT, "[^@\\s]", collect="cmd"))
    end.addNext(end)

    # Whitespace ends a command, always
    ws = end.addNext(Token(CMD_IDENT, "\\s"))

    # ...but if an @ follows, check for the string `musebotbot` following it
    end = end.addNext(Token(CMD_IDENT, "@"))

    for c in "musebotbot":
        end = end.addNext(Token(CMD_IDENT, c))

    # And terminate the bot name with whitespace
    end.addNext(ws)
    return cmdStart


def getAllGrammar():
    master = Token("master", "[^]")

    master.addNext(getPRGrammar())
    master.addNext(getNodeGrammar())
    master.addNext(getCommandGrammar())

    return master
