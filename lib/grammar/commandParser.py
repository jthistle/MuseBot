#!/usr/bin/env python3

"""The command parser and token object"""

import re
from ..getLogger import getLogger

logger = getLogger()

class Token:
    """A grammatical token in a sequence.

    Arguments:
    action -- a string identifier for the overall action this token belongs to
    accept -- a regex string that will match chars that are accepted as matches for this token
    collect -- the ident to which the collected value should be matched (default: None)
    nxt -- the list of tokens that can follow this one (default: None)
    """
    def __init__(self, action, accept, collect=None, nxt=None):
        self.action = action
        self.accept = re.compile(accept)
        self.next   = nxt or []
        self.collect = collect

    @staticmethod
    def fromToken(token, action=None, collect=None):
        """Return a copy of a token, overwriting action/collect if specified"""
        return Token(
            action if action is not None else token.action,
            token.accept,
            token.nxt,
            collect if collect is not None else token.collect
        )

    def addNext(self, token):
        """Add a token to come after this one in the sequence. Returns the added token."""
        self.next.append(token)
        return token

    def loopback(self):
        """Let this token be followed by itself"""
        self.next.append(self)
        return self

    def terminates(self):
        """If this token terminates the sequence"""
        return len(self.next) == 0

    def doCollect(self):
        """If this token should have the value found for it collected"""
        return self.collect is not None

    def isValid(self, char):
        """If char matches this token's acceptance criteria"""
        return self.accept.search(char) is not None

    def validNext(self, char):
        """Get the valid token coming directly after this one, for a matching char"""
        for token in self.next:
            if token.isValid(char):
                return token
        return None


class Command:
    """A basic container type for a parsed command"""
    def __init__(self, ident, data):
        self.ident = ident
        self.data = data


class CommandParser:
    """An object that will take a grammar, and parse any strings according to it."""
    def __init__(self, master):
        self.master = master
        self.currentToken = master

    def parse(self, string):
        """Parse a `string` according to the given grammar"""
        parsed = []
        collections = {}
        string += " "
        for c in string:
            reset = True
            validNext = self.currentToken.validNext(c)
            if validNext is not None:
                self.currentToken = validNext

                # If we need to collect the value of this token, do it
                if self.currentToken.doCollect():
                    if self.currentToken.collect not in collections:
                        collections[self.currentToken.collect] = ""
                    collections[self.currentToken.collect] += c

                if self.currentToken.terminates():
                    parsed.append(Command(self.currentToken.action, collections))
                else:
                    reset = False

            if reset:
                self.currentToken = self.master
                self.collections = {}

        return parsed
