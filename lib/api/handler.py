#!/usr/bin/env python3

from ..getLogger import getLogger
import http.client
import json

from ..config import *

logger = getLogger()

class ApiError(Exception):
	def __init__(self, code, channel):
		super().__init__()
		self.code = -1
		try:
			self.code = int(code)
		except:
			logger.error("Code is not a number!")

		self.channel = channel

class ApiHandler:
	def __init__(self):
		self.con = http.client.HTTPSConnection(URL, 443)

	def reconnect(self):
		self.con.close()
		self.con = http.client.HTTPSConnection(URL, 443)

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
			logger.info("Reponse: {}".format(decodedResponse))

			channel = 0
			if "chat_id" in data.keys():
				channel = data["chat_id"]

			raise ApiError(decodedResponse["error_code"], channel)
			return False

		return decodedResponse["result"]
