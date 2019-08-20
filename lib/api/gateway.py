#!/usr/bin/env python3

"""This module abstracts some functions that deal with creating requests to send via the ApiHandler"""

from config import *
from getLogger import getLogger

logger = getLogger()

class Gateway:
    def __init__(self, apiHandler):
        self.handler = apiHandler

    def sendMessage(self, text, channel, previewLinks = True):
        logger.debug("Sending message to {}: {}".format(channel, text))
        return self.handler.makeRequest("sendMessage", {"chat_id": channel, "text": text, "parse_mode": "HTML", "disable_web_page_preview": not previewLinks})

    def getMeta(self):
        return self.handler.makeRequest("getMe")