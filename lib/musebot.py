#!/usr/bin/env python3

import urllib.request
import json
import time
import datetime
import shelve
import traceback
import os
import smtplib
import random
import re
from email.mime.text import MIMEText

from config import *

from getLogger import getLogger
from api.handler import ApiHandler
from api.gateway import Gateway
from grammar.commandParser import CommandParser
from grammar.grammars import getAllGrammar()

logger = getLogger()

class Message:
    """A container for a message, containing only useful data"""
    def __init__(self, text, msgId, channel, sender):
        self.text = text
        self.channel = channel
        self.sender = sender
        self.id = msgId


class MuseBot:
    """The main MuseBot class. This handles all top-level operations."""
	def __init__(self):
        self.HANDLER = ApiHandler()
		self.API = Gateway(self.HANDLER)
		self.metaData = self.API.getMeta()

        master = getAllGrammar()
        self.parser = CommandParser(master)

    def logMessage(self, msg):
        """Write a message to the persistent message log"""
        with shelve.open(DATA_FILE) as f:
            log = []
            if "messageLog" in f.keys():
                log = f["messageLog"]

            log.append(msg)

            # TODO: and delete all but last 100 messages

            f["messageLog"] = log

    def getMutedUsers(self):
        """Get a list of all the muted users' ids"""
        with shelve.open(DATA_FILE) as f:
            if "mutedUsers" in f.keys():
                return f["mutedUsers"]
            return []

    def addMutedUser(self, userId):
        """Add a user to the list of muted users"""
        with shelve.open(DATA_FILE) as f:
            mutedUsers = []
            if "mutedUsers" in f.keys():
                mutedUsers = f["mutedUsers"]

            if userId not in mutedUsers:
                mutedUsers.append(userId)
            f["mutedUsers"] = mutedUsers

    def removeMutedUser(self, userId):
        """Remove a user from the list of muted users"""
        with shelve.open(DATA_FILE) as f:
            mutedUsers = []
            if "mutedUsers" in f.keys():
                mutedUsers = f["mutedUsers"]

            debug("muted users: {}".format(str(mutedUsers)))
            if userId in mutedUsers:
                mutedUsers.remove(userId)
            f["mutedUsers"] = mutedUsers

    def isMuted(self, userId):
        muted = getMutedUsers()
        return userId in muted

    def commandHelp(self, message):
        self.API.sendMessage(HELP_TEXT, message.channel)

    #def commandIntegrate

    def handleCommand(self, command, message):
        """Handle a command beginning with a slash, e.g. help, integrate"""
        cmdName = command.data.cmd
        if cmdName == "help":
            commandHelp(message)


    def handleMessage(self, message):
        self.logMessage(message)

        # Check if we can parse the message
        if "text" not in message:
            return

        msgText = message["text"]
        channel = int(message["chat"]["id"])
		messageId = int(message["message_id"])
        senderId = None

        if "from" in message:
            senderId = int(message["from"]["id"])

        logger.debug("New message (#{}) from {} in {}: {}".format(messageId, senderId, channel, msgText))

        if self.isMuted(senderId):
            logger.debug("User is muted, skipping...")
            return

        messageObj = Message(msgText, messageId, channel, senderId)

        # Parse the message
        parsed = self.parser.parse(msgText)
        for command in parsed:
            if command.ident == NODE_IDENT:
                pass    # TODO: handle node
            elif command.ident == PR_IDENT:
                pass    # TODO
            elif command.ident == CMD_IDENT:
                handleCommand(command, messageObj)

	def run(self):
		startingUpdates = []
		startingUpdates = HANDLER.makeRequest("getUpdates", {"timeout": 0, "offset": -1})

		lastOffset = 0
		if len(startingUpdates) > 0:
			lastOffset = startingUpdates[-1]["update_id"]

		while True:
			updates = HANDLER.makeRequest("getUpdates", {"timeout": REQUEST_DELAY, "offset": lastOffset + 1})
			for update in updates:
				lastOffset = update["update_id"]
                if "message" in update.keys():
                    message = update["message"]
                    self.handleMessage(message)
