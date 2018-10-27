#!/usr/bin/env python3

from secrets import *
import http.client
import urllib.request
import json
import time

URL = "api.telegram.org"
REQUEST_URL = "/bot"+APIKEY+"/"
REQUEST_DELAY = 1	# second to wait between requests
HEADERS = {'Content-type': 'application/json'}
HTTP_ERRORS_FATAL = True
DEBUG = True

MUSESCORE_NODE_URL = "https://musescore.org/en/node/"
GITHUB_PULL_URL = "https://github.com/musescore/MuseScore/pull/"
MAX_PULL_ID = 10000

con = http.client.HTTPSConnection(URL, 443)	# gives HTTPS

def makeApiRequest(cmd, data={}):
	jsonData = json.dumps(data)
	con.request("POST", REQUEST_URL+cmd, jsonData, HEADERS)

	response = con.getresponse()
	decodedResponse = json.loads(response.read().decode())
	if not decodedResponse["ok"]:
		if HTTP_ERRORS_FATAL:
			raise Exception("Error: reponse: {}".format(decodedResponse))
		else:
			print("Error: reponse: {}".format(response))
			return False

	return decodedResponse["result"]

def checkExists(url):
	try:
		response = urllib.request.urlopen(url)
	except urllib.error.URLError:
		return False

	return True

def sendMessage(text, channel):
	if DEBUG:
		print("Sending to {}: {}".format(channel, text))
	return makeApiRequest("sendMessage", {"chat_id": channel, "text": text})

if DEBUG:
	print(makeApiRequest("getMe"))

startingUpdates = [1]
startingUpdates = makeApiRequest("getUpdates", {"timeout": 0, "offset": -1})

lastOffset = 0
if len(startingUpdates) > 0:
	lastOffset = startingUpdates[-1]["update_id"] + 1

while True:
	updates = makeApiRequest("getUpdates", {"timeout": REQUEST_DELAY, "offset": lastOffset})
	for update in updates:
		if "message" in update.keys():
			text = update["message"]["text"] + " "	# add whitespace to force finishing parsing numbers
			channel = update["message"]["chat"]["id"]
			# channel = "@musebot"
			if DEBUG:
				print("New update: message in {}: {}".format(channel, text))

			parseNumber = False
			currentNum = ""
			for char in text:
				if char == "#":
					parseNumber = True
				elif parseNumber:
					if char.isdigit():
						currentNum = currentNum+char
					else:
						if currentNum != "":
							finalNum = int(currentNum)
							if DEBUG:
								print("Looking for issue/node #{}".format(currentNum))

							if finalNum > MAX_PULL_ID:
								# Look for a MuseScore.org node
								urlToCheck = MUSESCORE_NODE_URL+currentNum
								if checkExists(urlToCheck):
									msg = "Node #{}: {}".format(finalNum, urlToCheck)
									sendMessage(msg, channel)
								elif DEBUG:
									print("Couldn't find node #{}".format(finalNum))
							else:
								# Look for a github issue
								urlToCheck = GITHUB_PULL_URL+currentNum
								if checkExists(urlToCheck):
									msg = "PR #{}: {}".format(finalNum, urlToCheck)
									sendMessage(msg, channel)
								elif DEBUG:
									print("Couldn't find PR #{}".format(finalNum))

						# Cleanup
						currentNum = ""
						parseNumber = False

		lastOffset = update["update_id"] + 1

	time.sleep(REQUEST_DELAY)
