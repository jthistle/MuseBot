#!/usr/bin/env python3

from secrets import *
import http.client
import urllib.request
import json
import time
import datetime
import shelve

URL = "api.telegram.org"
REQUEST_URL = "/bot"+APIKEY+"/"
REQUEST_DELAY = 1	# second to wait between requests
HEADERS = {'Content-type': 'application/json'}
HTTP_ERRORS_FATAL = True
DEBUG = True
DEBUG_TO_FILE = True
DEBUG_FILE = "log.txt"
DEBUG_LEVELS = ["debug", "notice", "warning", "error"]

COMMANDS = ["mute", "unmute"]
DATA_FILE = "data.dat"

MUSESCORE_NODE_URL = "https://musescore.org/node/"
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
			debug("reponse: {}".format(decodedResponse), 3)
			raise Exception("Error: reponse: {}".format(decodedResponse))
		else:
			debug("reponse: {}".format(response), 3)
			return False

	return decodedResponse["result"]

def checkExists(url):
	try:
		response = urllib.request.urlopen(url)
	except urllib.error.URLError:
		return False

	return True

def sendMessage(text, channel):
	debug("Sending to {}: {}".format(channel, text))
	return makeApiRequest("sendMessage", {"chat_id": channel, "text": text})

def debug(text, level=0):
	if level >= len(DEBUG_LEVELS):
		# R e c u r s i o n
		debug("debug called with higher level than possible", 2)
		return False

	if not DEBUG and level == 0:
		return True

	timestamp = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
	msg = timestamp + ": " + DEBUG_LEVELS[level] + ": " + str(text)
	if DEBUG_TO_FILE:
		debugFile = open(DEBUG_FILE, "a")
		debugFile.write(msg+"\n")
		debugFile.close()
	else:
		print(msg)

def getMutedUsers():
	with shelve.open(DATA_FILE) as f:
		if "mutedUsers" in f.keys():
			return f["mutedUsers"]
		return []

def addMutedUser(userId):
	with shelve.open(DATA_FILE) as f:
		mutedUsers = []
		if "mutedUsers" in f.keys():
			mutedUsers = f["mutedUsers"]
		
		if userId not in mutedUsers:
			mutedUsers.append(userId)
		f["mutedUsers"] = mutedUsers

def removeMutedUser(userId):
	with shelve.open(DATA_FILE) as f:
		mutedUsers = []
		if "mutedUsers" in f.keys():
			mutedUsers = f["mutedUsers"]
		
		debug("muted users: {}".format(str(mutedUsers)))
		if userId in mutedUsers:
			mutedUsers.remove(userId)
		f["mutedUsers"] = mutedUsers

debug("Starting MuseBot...")
if DEBUG:
	debug(makeApiRequest("getMe"))

startingUpdates = [1]
startingUpdates = makeApiRequest("getUpdates", {"timeout": 0, "offset": -1})

lastOffset = 0
if len(startingUpdates) > 0:
	lastOffset = startingUpdates[-1]["update_id"] + 1

while True:
	updates = makeApiRequest("getUpdates", {"timeout": REQUEST_DELAY, "offset": lastOffset})
	for update in updates:
		lastOffset = update["update_id"] + 1
		if "message" in update.keys():
			if "text" not in update["message"].keys():
				continue
			text = update["message"]["text"] + " "	# add whitespace to force finishing parsing numbers
			channel = update["message"]["chat"]["id"]
			debug("New update: message in {}: {}".format(channel, text))

			if "from" not in update["message"]:
				debug("no sending user for message")
				userId = ""
			else:
				userId = update["message"]["from"]["id"]

			isMuted = False
			mutedUsers = getMutedUsers()
			if userId in mutedUsers:
				debug("user is muted, skipping")
				isMuted = True

			parseNumber = False
			parseCommand = False
			currentCmd = ""
			currentNum = ""
			for i in range(len(text)):
				char = text[i]
				if char == "#":
					if not isMuted:
						parseNumber = True
				elif char == "/":
					if i == 0:
						parseCommand = True
				elif parseCommand:
					if char == " ":
						# Handle command
						cmd = currentCmd.lower()
						if cmd in COMMANDS:
							
							if cmd == "mute":
								addMutedUser(userId)
								debug("added muted user")
							elif cmd == "unmute":
								removeMutedUser(userId)
								debug("removed muted user")
						else:
							debug("command {} not valid".format(cmd))
					else:
						currentCmd = currentCmd + char
				elif parseNumber:
					if char.isdigit():
						currentNum = currentNum+char
					else:
						if currentNum != "":
							finalNum = int(currentNum)
							debug("Looking for issue/node #{}".format(currentNum))

							if finalNum > MAX_PULL_ID:
								# Look for a MuseScore.org node
								urlToCheck = MUSESCORE_NODE_URL+currentNum
								if checkExists(urlToCheck):
									msg = "Node #{}: {}".format(finalNum, urlToCheck)
									sendMessage(msg, channel)
								else:
									debug("Couldn't find node #{}".format(finalNum))
							else:
								# Look for a github issue
								urlToCheck = GITHUB_PULL_URL+currentNum
								if checkExists(urlToCheck):
									msg = "PR #{}: {}".format(finalNum, urlToCheck)
									sendMessage(msg, channel)
								else:
									debug("Couldn't find PR #{}".format(finalNum))

						# Cleanup
						currentNum = ""
						parseNumber = False

	time.sleep(REQUEST_DELAY)
