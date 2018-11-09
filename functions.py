#!/usr/bin/env python3

from secrets import *
import http.client
import urllib.request
import json
import time
import datetime
import shelve
import traceback
import os

try:
	from production import *
except ImportError:
	# We aren't running on a production server, so
	# use default values.
	DEBUG = True
	DEBUG_TO_FILE = False
	DEBUG_FILE = "log.txt"
	DATA_FILE = "data.dat"

from config import *

class ApiError(Exception):
    pass

con = http.client.HTTPSConnection(URL, 443)	# gives HTTPS

def reconnect():
	con = http.client.HTTPSConnection(URL, 443)	# gives HTTPS

def makeApiRequest(cmd, data={}):
	jsonData = json.dumps(data)
	con.request("POST", REQUEST_URL+cmd, jsonData, HEADERS)

	response = con.getresponse()
	decodedResponse = json.loads(response.read().decode())
	if not decodedResponse["ok"]:
		debug("reponse: {}".format(decodedResponse), 3)
		raise ApiError(decodedResponse["error_code"])
		return False

	return decodedResponse["result"]

def checkExists(url):
	try:
		response = urllib.request.urlopen(url)
	except urllib.error.URLError:
		return False

	return True

def sendMessage(text, channel, previewLinks = True):
	debug("Sending to {}: {}".format(channel, text))
	return makeApiRequest("sendMessage", {"chat_id": channel, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": not previewLinks})

def sendToIntegrations(text, previewLinks = True):
	for ig in getIntegrations():
		sendMessage(text, ig, previewLinks)

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

def logMessage(msg):
	with shelve.open(DATA_FILE) as f:
		log = []
		if "messageLog" in f.keys():
			log = f["messageLog"]
		
		debug("logging message")
		log.append(msg)
		f["messageLog"] = log

def updateLog():
	debug("updating log")
	with shelve.open(DATA_FILE) as f:
		log = []
		if "messageLog" in f.keys():
			log = f["messageLog"]
		
		currentTime = time.time()
		toRemove = []
		for i in range(len(log)):
			if currentTime - log[i]["date"] > 60*60*24:
				toRemove.append(i)

		for i in range(len(toRemove)-1, -1, -1):
			del log[i]
		debug("removed {} old messages".format(len(toRemove)))

		f["messageLog"] = log
	debug("completed log update")

def getMessages(i, chatId, limit=1):
	# Gets the message with index i in log, starting from the _lastest_ one
	with shelve.open(DATA_FILE) as f:
		log = []
		if "messageLog" in f.keys():
			log = f["messageLog"]
		
		toReturn = []
		for j in range(limit):
			while len(log)-i-1 >= 0:
				thisMsg = log[len(log)-i-1]
				if thisMsg["chat"]["id"] == chatId:
					toReturn.append(log[len(log)-i-1])
					i += 1
					break
				i += 1

		if len(toReturn) > 0:
			return toReturn
	return False

def getWebhooks():
	for w in WEBHOOKS:
		webhookPath = WEBHOOKS_DIR+w+".txt"
		if os.path.exists(webhookPath):
			debug("Found webhook event {}".format(w))
			with open(webhookPath, "r") as f:
				payload = json.loads(f.read())
				if w == "pull_request":
					prDetails = payload["pull_request"]
					if payload["action"] == "opened":
						number = prDetails["number"]
						url = prDetails["html_url"]
						username = prDetails["user"]["login"]
						title = prDetails["title"]
						msg = "New Pull Request: [#{} - {}]({}) by {}".format(number, title, url, username)

						sendToIntegrations(msg, False)
				elif w == "push":
					commits = payload["commits"]
					pusher = payload["pusher"]["name"]
					branch = payload["ref"][11:]	# eg refs/heads/master
					latestCommit = commits[0]
					latestMessage = latestCommit["message"]
					if len(latestMessage) > 70:
						latestMessage = latestMessage[:70]+"..."
					latestCommitLink = "[{}]({}) - _{}_".format(latestCommit["id"][:6], latestCommit["url"], latestMessage)
					msg = "{} pushed {} commit{} to {}, including {}".format(
						pusher, len(commits), "s" if len(commits) > 1 else "", branch, latestCommitLink
						)

					sendToIntegrations(msg, False)
				else:
					debug("Unhandled webhook {}".format(w), 1)
			debug("Removing {}".format(webhookPath))
			os.remove(webhookPath)

def integrate(channel):
	with shelve.open(DATA_FILE) as f:
		integrations = []
		if "integrations" in f.keys():
			integrations = f["integrations"]

		if channel not in integrations:
			integrations.append(channel)
		f["integrations"] = integrations

def unintegrate(channel):
	with shelve.open(DATA_FILE) as f:
		integrations = []
		if "integrations" in f.keys():
			integrations = f["integrations"]

		if channel in integrations:
			integrations.remove(channel)

		f["integrations"] = integrations

def getIntegrations():
	with shelve.open(DATA_FILE) as f:
		integrations = []
		if "integrations" in f.keys():
			integrations = f["integrations"]

		return integrations
