#!/usr/bin/env python3

"""The main entry point for MuseBotLib."""

import json
import shelve
import os
import random

from .config import *

from .getLogger import getLogger
from .api.handler import ApiHandler
from .api.gateway import Gateway
from .grammar.commandParser import CommandParser
from .grammar.grammars import getAllGrammar
from . import helper

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

            # Remove all but last 100 logged messages
            removeCount = len(log)-100 if len(log)-100 > 0 else 0
            del log[100:]

            f["messageLog"] = log

    def getMessages(self, index, channel, limit=1):
        """Gets the message with `index` in log, starting from the _latest_ one"""
        with shelve.open(DATA_FILE) as f:
            log = []
            if "messageLog" in f.keys():
                log = f["messageLog"]

            toReturn = []
            for j in range(limit):
                current = len(log) - index - 1
                while current >= 0:
                    thisMsg = log[current]
                    if thisMsg.channel == channel:
                        toReturn.append(log[current])
                        current += 1
                        break
                    current += 1

            if len(toReturn) > 0:
                return toReturn
        return False

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

            if userId in mutedUsers:
                mutedUsers.remove(userId)
            f["mutedUsers"] = mutedUsers

    def isMuted(self, userId):
        muted = self.getMutedUsers()
        return userId in muted

    def integrate(self, channel):
        """Add a channel to the list of integrations"""
        with shelve.open(DATA_FILE) as f:
            integrations = []
            if "integrations" in f.keys():
                integrations = f["integrations"]

            if channel not in integrations:
                integrations.append(channel)

            logger.debug("Added {} to integrations".format(channel))
            f["integrations"] = integrations

    def unintegrate(self, channel):
        """Remove a channel from the list of integrations"""
        with shelve.open(DATA_FILE) as f:
            integrations = []
            if "integrations" in f.keys():
                integrations = f["integrations"]

            if channel in integrations:
                integrations.remove(channel)

            logger.debug("Removed {} from integrations".format(channel))
            f["integrations"] = integrations

    def getIntegrations(self):
        with shelve.open(DATA_FILE) as f:
            integrations = []
            if "integrations" in f.keys():
                integrations = f["integrations"]

            return integrations

    def sendToIntegrations(self, text, previewLinks = True):
        for ig in self.getIntegrations():
            self.API.sendMessage(text, ig, previewLinks)

    def commandHelp(self, message):
        self.API.sendMessage(HELP_TEXT, message.channel)

    def commandIntegrate(self, message):
        self.API.sendMessage("Integrated push, PR and Travis notifications in this chat!", message.channel)
        self.integrate(message.channel)

    def commandUnintegrate(self, message):
        self.unintegrate(message.channel)

    def commandMute(self, message):
        self.addMutedUser(message.sender)

    def commandUnmute(self, message):
        self.removeMutedUser(message.sender)

    def commandDelete(self, message):
        lastMsgs = self.getMessages(1, message.channel, limit=1)
        logger.debug("delete")
        if lastMsgs:
            logger.debug("last messages: {}".format(lastMsgs))
            if int(lastMsgs[0].id) < message.id - 1:
                # Last message is from bot, delete
                self.API.deleteMessage(message.channel, message.id - 1)

    def handleCommand(self, command, message, muted):
        """Handle a command beginning with a slash, e.g. help, integrate"""
        cmdName = command.data["cmd"]

        if muted:
            if cmdName == "unmute":
                self.commandUnmute(message)
            return

        if cmdName == "help":
            self.commandHelp(message)
        elif cmdName == "integrate":
            self.commandIntegrate(message)
        elif cmdName == "unintegrate":
            self.commandUnintegrate(message)
        elif cmdName == "mute":
            self.commandMute(message)
        elif cmdName == "delete":
            self.commandDelete(message)

    def handleNode(self, command, message):
        number = command.data["number"]
        urlToCheck = MUSESCORE_NODE_URL+number
        if helper.checkExists(urlToCheck):
            msg = "<a href='{}'>Node #{}</a>".format(urlToCheck, number)
            self.API.sendMessage(msg, message.channel)

    def handlePr(self, command, message):
        number = command.data["number"]
        urlToCheck = GITHUB_PULL_URL+number
        if helper.checkExists(urlToCheck):
            msg = "<a href='{}'>PR #{}</a>".format(urlToCheck, number)
            self.API.sendMessage(msg, message.channel)

    def beFriendly(self, message):
        """If nothing useful can be done, at least try to return a vaguely humourous response."""
        text = message.text.lower()
        possibilities = []

        if helper.inText(("thanks", "thank", "danke", "gracias", "merci"), text) and "musebot" in text:
            possibilities = ("No, thank <i>you</i>!", "No problem")
        elif helper.inText(("love", "<3", "♥️"), text) and "musebot" in text:
            possibilities = ("♥️", "(^ω^)", "&lt;3")
        elif helper.inText(("sleeping", "dead", "down", "broken"), text) and "musebot" in text:
            possibilities = ("I'm still alive!", "I don't think so", "...")
        elif helper.inText(("hate", "don't like", "dislike"), text) and "musebot" in text:
            possibilities = (":(", "Your feedback is appreciated", "ok.")
        elif helper.inText(("shut up", "be quiet"), text) and "musebot" in text:
            possibilities = ["Ok, I won't respond to you anymore. /unmute to undo."]
            addMutedUser(message.sender)
        elif "happy birthday" in text and "musebot" in text:
            possibilities = ("🎉🎉🎉", "Thank you!", "Another year closer to death")
        elif "interesting" in text and "..." in text:
            redurl = helper.getRedirectedURL("https://en.wikipedia.org/wiki/Special:Random")
            possibilities = ["<a href=\"{}\">{}</a>".format(redurl, x) for x in ("This certainly is interesting...", "very... interesting", "how interesting...")]
        elif "open the pod bay doors" in text:
            possibilities = ["I'm sorry Dave, I'm afraid I can't do that."]
        elif helper.inText("hal", text, True):
            possibilities = ("Just what do you think you're doing, Dave?",
                "Dave, this conversation can serve no purpose anymore.",
                "I am completely operational, and all my circuits are functioning perfectly.")
        elif helper.inText(("terminator", "skynet"), text):
            possibilities = ("I'll be back.", "I need your clothes, your boots and your motorcycle.")

        if len(possibilities) > 0:
            self.API.sendMessage(random.choice(possibilities), message.channel)

    def handleMessage(self, message):
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

        # Check if the user is muted
        muted = False
        if self.isMuted(senderId):
            logger.debug("User is muted, skipping...")
            muted = True

        # Create a message object with the necessary info
        messageObj = Message(msgText, messageId, channel, senderId)

        # Add the message to the persistent log
        self.logMessage(messageObj)

        # Parse the message
        parsed = self.parser.parse(msgText)
        for command in parsed:
            if command.ident == NODE_IDENT and not muted:
                self.handleNode(command, messageObj)
            elif command.ident == PR_IDENT and not muted:
                self.handlePr(command, messageObj)
            elif command.ident == CMD_IDENT:
                self.handleCommand(command, messageObj, muted)

        # For friendliness, don't bother with a formal grammar. String matching will do.
        if len(parsed) == 0 and not muted and FRIENDLY:
            self.beFriendly(messageObj)

    def handleHookPullRequest(self, payload):
        prDetails = payload["pull_request"]
        if payload["action"] == "opened":
            number = prDetails["number"]
            url = prDetails["html_url"]
            username = prDetails["user"]["login"]
            title = helper.sanitizeText(prDetails["title"])
            msg = "New Pull Request: <a href=\"{}\">#{} - {}</a> by {}".format(url, number, title, username)

            self.sendToIntegrations(msg, False)

    def handleHookPush(self, payload):
        commits = payload["commits"]
        pusher = payload["pusher"]["name"]
        branch = payload["ref"][11:]	# eg refs/heads/master

        if len(commits) == 0:
            return
        latestCommit = commits[0]
        latestMessage = helper.sanitizeText(latestCommit["message"])
        if len(latestMessage) > 70:
            latestMessage = latestMessage[:70]+"..."
        latestCommitLink = "<a href=\"{}\">{}</a> - <i>{}</i>".format(latestCommit["url"], latestCommit["id"][:6], latestMessage)
        msg = "{} pushed {} commit{} to {}, including {}".format(
            pusher, len(commits), "s" if len(commits) > 1 else "", branch, latestCommitLink
            )

        self.sendToIntegrations(msg, False)

    def handleHookTravis(self, payload):
        logger.debug("Travis hook")
        isPr = payload["pull_request"]
        if isPr:
            return

        status = payload["status_message"].lower()
        logger.debug("Status: "+status)
        message = ""
        if status == "fixed":
            message = "has been fixed"
        elif status == "broken":
            message = "has been broken"
        elif status == "still failing":
            message = "is still failing"
        elif status == "errored":
            message = "has errored"

        repoOwner = payload["repository"]["owner_name"]
        logger.debug("Repo owner: "+repoOwner)

        if message != "" and repoOwner.lower() == "musescore":
            commit = payload["commit"]
            commitURL = "<a href=\"{}{}\">{}</a>".format(GITHUB_COMMIT_URL, commit, commit[:6])
            branch = payload["branch"]
            user = payload["committer_name"]
            buildURL = "<a href=\"{}\">build</a>".format(payload["build_url"])

            msg = "MuseScore/{} : {} by {}: {} {}".format(branch, commitURL, user, buildURL, message)
            self.sendToIntegrations(msg, True)

    def getWebhooks(self):
        for w in WEBHOOKS:
            webhookPath = WEBHOOKS_DIR+w+".txt"
            if os.path.exists(webhookPath):
                logger.debug("Found webhook event {}".format(w))
                with open(webhookPath, "r") as f:
                    try:
                        payload = json.loads(f.read())
                        if w == "pull_request":
                            self.handleHookPullRequest(payload)
                        elif w == "push":
                            self.handleHookPush(payload)
                        elif w == "travis":
                            self.handleHookTravis(payload)
                        else:
                            logger.warning("Unhandled webhook {}".format(w))
                    except json.JSONDecodeError as e:
                        logger.error("Couldn't read the payload: {}".format(e))

                logger.debug("Removing {}".format(webhookPath))
                os.remove(webhookPath)

    def run(self):
        """Runs MuseBot."""
        logger.info("Starting MuseBot...")
        startingUpdates = self.API.getUpdates(0, -1)

        lastOffset = 0
        if len(startingUpdates) > 0:
            lastOffset = startingUpdates[-1]["update_id"]

        while True:
            # This request will last a maximum of REQUEST_DELAY seconds open (long polling)
            updates = self.API.getUpdates(REQUEST_DELAY, lastOffset + 1)
            for update in updates:
                lastOffset = update["update_id"]
                if "message" in update.keys():
                    message = update["message"]
                    self.handleMessage(message)

            self.getWebhooks()
