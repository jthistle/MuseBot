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
import smtplib
import random
import re
from email.mime.text import MIMEText

try:
	from production import *
except ImportError:
	# We aren't running on a production server, so
	# use default values.
	from productionDefaults import *

from config import *

class ApiError(Exception):
	def __init__(self, code, channel):
		super().__init__()
		self.code = -1
		try:
			self.code = int(code)
		except:
			debug("Code is not a number!", 3)

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
			debug("An error occurred while carrying out the API request", 1)
			raise

		response = self.con.getresponse()
		decodedResponse = json.loads(response.read().decode())
		if not decodedResponse["ok"]:
			debug("reponse: {}".format(decodedResponse), 3)

			channel = 0
			if "chat_id" in data.keys():
				channel = data["chat_id"]

			raise ApiError(decodedResponse["error_code"], channel)
			return False

		return decodedResponse["result"]

HANDLER = ApiHandler()

def checkExists(url):
	try:
		response = urllib.request.urlopen(url)
	except urllib.error.URLError:
		return False

	return True


def getRedirectedURL(url):
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
    request = opener.open(url)
    return request.url

def sanitizeText(text):
	# Remove any dodgy tags < >
	text = text.replace("<", "&lt;")
	text = text.replace(">", "&gt;")

	return text

def sendMessage(text, channel, previewLinks = True):
	debug("Sending to {}: {}".format(channel, text))
	return HANDLER.makeRequest("sendMessage", {"chat_id": channel, "text": text, "parse_mode": "HTML", "disable_web_page_preview": not previewLinks})

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
		try:
			debugFile = open(DEBUG_FILE, "a")
			debugFile.write(msg+"\n")
			debugFile.close()
		except Exception as e:
			print("Error debugging:", e)
	else:
		print(msg)

def sendEmail(subject, msg):
	if ERROR_EMAIL == "":
		return True

	toSend = MIMEText(msg)
	toSend["Subject"] = subject
	toSend["From"] = ERROR_EMAIL_SENDER
	toSend["To"] = ERROR_EMAIL

	s = smtplib.SMTP("localhost")
	s.send_message(toSend)
	s.quit()
	debug("Sent email")

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

		removeCount = len(log)-100 if len(log)-100 > 0 else 0
		del log[100:]

		debug("removed {} old messages".format(removeCount))

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

def hookPullRequest(payload):
	prDetails = payload["pull_request"]
	if payload["action"] == "opened":
		number = prDetails["number"]
		url = prDetails["html_url"]
		username = prDetails["user"]["login"]
		title = sanitizeText(prDetails["title"])
		msg = "New Pull Request: <a href=\"{}\">#{} - {}</a> by {}".format(url, number, title, username)

		sendToIntegrations(msg, False)

def hookPush(payload):
	commits = payload["commits"]
	pusher = payload["pusher"]["name"]
	branch = payload["ref"][11:]	# eg refs/heads/master

	if len(commits) == 0:
		return
	latestCommit = commits[0]
	latestMessage = sanitizeText(latestCommit["message"])
	if len(latestMessage) > 70:
		latestMessage = latestMessage[:70]+"..."
	latestCommitLink = "<a href=\"{}\">{}</a> - <i>{}</i>".format(latestCommit["url"], latestCommit["id"][:6], latestMessage)
	msg = "{} pushed {} commit{} to {}, including {}".format(
		pusher, len(commits), "s" if len(commits) > 1 else "", branch, latestCommitLink
		)

	sendToIntegrations(msg, False)

def hookTravis(payload):
	debug("Travis hook")
	isPr = payload["pull_request"]
	if isPr:
		return

	status = payload["status_message"].lower()
	debug("Status: "+status)
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
	debug("Repo owner: "+repoOwner)

	if message != "" and repoOwner.lower() == "musescore":
		commit = payload["commit"]
		commitURL = "<a href=\"{}{}\">{}</a>".format(GITHUB_COMMIT_URL, commit, commit[:6])
		branch = payload["branch"]
		user = payload["committer_name"]
		buildURL = "<a href=\"{}\">build</a>".format(payload["build_url"])

		msg = "MuseScore/{} : {} by {}: {} {}".format(branch, commitURL, user, buildURL, message)
		sendToIntegrations(msg, True)

def getWebhooks():
	for w in WEBHOOKS:
		webhookPath = WEBHOOKS_DIR+w+".txt"
		if os.path.exists(webhookPath):
			debug("Found webhook event {}".format(w))
			with open(webhookPath, "r") as f:
				payload = json.loads(f.read())
				if w == "pull_request":
					hookPullRequest(payload)
				elif w == "push":
					hookPush(payload)
				elif w == "travis":
					hookTravis(payload)
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

def inText(needles, haystack, seperate = False, caseSensitive = False):
	if not seperate:
		for n in needles:
			if (n.lower() if not caseSensitive else n) in haystack:
				return True
	else:
		haystack = " " + haystack + " "
		if type(needles) == str:
			needles = [needles]
		for n in needles:
			if re.search(r"\b"+n+r"\b", haystack, (re.I if not caseSensitive else 0)):
				return True
	return False

def beFriendly(text, channel, userId):
	text = text.lower()
	possibilities = []

	if inText(("thanks", "thank", "danke", "gracias"), text) and "musebot" in text:
		possibilities = ("No, thank <i>you</i>!", "No problem")
	elif inText(("love", "<3", "♥️"), text) and "musebot" in text:
		possibilities = ("♥️", "(^ω^)", "&lt;3")
	elif inText(("sleeping", "dead", "down", "broken"), text) and "musebot" in text:
		possibilities = ("I'm still alive!", "I don't think so", "...")
	elif inText(("hate", "don't like", "dislike"), text) and "musebot" in text:
		possibilities = (":(", "Your feedback is appreciated", "ok.")
	elif inText(("shut up", "be quiet"), text) and "musebot" in text:
		possibilities = ["Ok, I won't respond to you anymore. /unmute to undo."]
		addMutedUser(userId)
	elif "happy birthday" in text and "musebot" in text:
		possibilities = ("🎉🎉🎉", "Thank you!", "Another year closer to death")
	elif "interesting" in text and "..." in text:
		redurl = getRedirectedURL("https://en.wikipedia.org/wiki/Special:Random")
		possibilities = ["<a href=\"{}\">{}</a>".format(redurl, x) for x in ("This certainly is interesting...", "very... interesting", "how interesting...")]
	elif "open the pod bay doors" in text:
		possibilities = ["I'm sorry Dave, I'm afraid I can't do that."]
	elif inText("hal", text, True):
		possibilities = ("Just what do you think you're doing, Dave?", 
			"Dave, this conversation can serve no purpose anymore.",
			"I am completely operational, and all my circuits are functioning perfectly.")
	elif inText(("terminator", "skynet"), text):
		possibilities = ("I'll be back.", "I need your clothes, your boots and your motorcycle.")


	if len(possibilities) > 0:
		sendMessage(random.choice(possibilities), channel)
