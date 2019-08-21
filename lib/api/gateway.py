#!/usr/bin/env python3

"""This module abstracts some functions that deal with creating requests to send via the ApiHandler"""

from ..config import *
from ..getLogger import getLogger

logger = getLogger()

class Gateway:
    def __init__(self, apiHandler):
        self.handler = apiHandler

    def getUpdates(self, timeout, offset):
        return self.handler.makeRequest("getUpdates", {"timeout": timeout, "offset": offset})

    def sendMessage(self, text, channel, previewLinks = True):
        logger.debug("Sending message to {}: {}".format(channel, text))
        return self.handler.makeRequest("sendMessage", {
            "chat_id": channel,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": not previewLinks
        })

    def deleteMessage(self, channel, messageId):
        logger.debug("Deleting message {} in {}".format(messageId, channel))
        self.handler.makeRequest("deleteMessage", {
            "chat_id": channel,
            "message_id": messageId
        })

    def getMeta(self):
        return self.handler.makeRequest("getMe")