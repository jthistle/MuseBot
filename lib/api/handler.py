#!/usr/bin/env python3

from ..getLogger import getLogger
import http.client
import json

from ..config import *
from ..mockers import mockedAPIRequest

logger = getLogger()

class ApiError(Exception):
    """An error that is raised when a request succeeds, but is rejected by the API"""
    def __init__(self, code, channel):
        super().__init__()
        self.code = -1
        try:
            self.code = int(code)
        except:
            logger.warning("Code is not a number!")

        self.channel = channel

class ApiHandler:
    def __init__(self):
        self.con = http.client.HTTPSConnection(URL, 443)

    def reconnect(self):
        self.con.close()
        self.con = http.client.HTTPSConnection(URL, 443)

    @mockedAPIRequest
    def makeRequest(self, cmd, data=None):
        jsonData = json.dumps(data or {})
        try:
            self.con.request("POST", REQUEST_URL+cmd, jsonData, HEADERS)
        except:
            logger.error("An error occurred while carrying out the API request")
            raise

        response = self.con.getresponse()
        decodedResponse = json.loads(response.read().decode())
        if not decodedResponse.get("ok"):
            logger.error("The request succeeded, but there was a bad response: {}".format(decodedResponse))

            channel = 0
            if "chat_id" in data.keys():
                channel = data["chat_id"]

            raise ApiError(decodedResponse["error_code"], channel)
            return False

        return decodedResponse["result"]
