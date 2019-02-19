#!/usr/bin/env python3

from secrets import *
import time
import traceback

try:
	from production import *
	ERRORS_FATAL = False
except ImportError:
	# We aren't running on a production server, so
	# use default values.
	from productionDefaults import *

from config import *
from functions import *

errorLogThisSession = []
lastEmail = 0

def main():
	debug("Starting MuseBot...", 1)
	metaData = HANDLER.makeRequest("getMe")

	startingUpdates = [1]
	startingUpdates = HANDLER.makeRequest("getUpdates", {"timeout": 0, "offset": -1})

	lastOffset = 0
	if len(startingUpdates) > 0:
		lastOffset = startingUpdates[-1]["update_id"] + 1


	while True:
		updates = HANDLER.makeRequest("getUpdates", {"timeout": REQUEST_DELAY, "offset": lastOffset})
		for update in updates:
			lastOffset = update["update_id"] + 1
			if "message" in update.keys():
				logMessage(update["message"])
				if "text" not in update["message"].keys():
					continue
				text = update["message"]["text"] + " "	# add whitespace to force finishing parsing numbers
				channel = int(update["message"]["chat"]["id"])
				messageId = int(update["message"]["message_id"])
				debug("New update: message ({}) in {}: {}".format(messageId, channel, text))

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
				forcePr = False
				currentCmd = ""
				currentNum = ""
				for i in range(len(text)):
					char = text[i]
					if char == "#":
						if not isMuted:
							parseNumber = True

							# Found a #, go back and check if pr was mentioned
							# allow whitespace between pr and #
							checkEndChar = i-1
							for j in range(i-1, -1, -1):
								if text[j] == " ":
									checkEndChar -= 1
								else:
									break

							if checkEndChar-1 >= 0:
								if text[checkEndChar-1:checkEndChar+1].lower() == "pr":
									forcePr = True
					elif char == "/":
						if i == 0:
							parseCommand = True
					elif parseCommand:
						# Both a space and an @ delimit the end of a cmd
						if char in (" ", "@"):
							# Handle command
							cmd = currentCmd.lower()
							if cmd in COMMANDS:
								if cmd == "mute":
									addMutedUser(userId)
									debug("added muted user")
								elif cmd == "unmute":
									removeMutedUser(userId)
									debug("removed muted user")
								elif cmd == "delete":
									lastMsgs = getMessages(1, channel, limit=1)
									if lastMsgs:
										if int(lastMsgs[0]["message_id"]) < messageId - 1:
											# Last message is from bot, delete
											debug("deleting message at {}".format(messageId-1))
											HANDLER.makeRequest("deleteMessage", {"chat_id": channel, "message_id": messageId-1})
								elif cmd == "integrate":
									integrate(channel)
									sendMessage("Integrated MuseBot!", channel)
								elif cmd == "unintegrate":
									unintegrate(channel)
								elif cmd == "help":
									sendMessage(HELP_TEXT, channel, False)
							else:
								debug("command {} not valid".format(cmd))

							# Cleanup
							parseCommand = False
							currentCmd = ""
						else:
							currentCmd = currentCmd + char
					elif parseNumber:
						if char.isdigit():
							currentNum = currentNum+char
						else:
							if currentNum != "":
								finalNum = int(currentNum)
								debug("Looking for issue/node #{}".format(currentNum))
								found = False

								# First, look for a MuseScore.org node
								if not forcePr:
									urlToCheck = MUSESCORE_NODE_URL+currentNum
									if checkExists(urlToCheck):
										msg = "<a href='{}'>Node #{}</a>".format(urlToCheck, finalNum)
										sendMessage(msg, channel)
										found = True
									else:
										debug("Couldn't find node #{}, will look for PR".format(finalNum))

								if not found:
									# Look for a github issue
									urlToCheck = GITHUB_PULL_URL+currentNum
									if checkExists(urlToCheck):
										msg = "<a href='{}'>PR #{}</a>".format(urlToCheck, finalNum)
										sendMessage(msg, channel)
									else:
										debug("Couldn't find PR #{}".format(finalNum))

							# Cleanup
							currentNum = ""
							parseNumber = False
							forcePr = False

				if not isMuted and FRIENDLY:
					beFriendly(text, channel, userId)

		# Handle webhooks
		getWebhooks()

		time.sleep(REQUEST_DELAY)

if __name__ == "__main__":
	while True:
		try:
			main()
		except ApiError as e:
			debug(traceback.format_exc(), 3)
			debug("=== {}".format(str(e)))
			if int(str(e)) in HTTP_ERRORS_FATAL:
				debug("error code {} is fatal".format(str(e)), 1)
				break
			else:
				debug("error code {} is NOT fatal".format(str(e)), 1)
		except Exception as e:
			debug(traceback.format_exc(), 3)

		currentTime = time.time()
		errorLogThisSession.append(currentTime)

		# Remove errors older than 24 hours
		toDelete = []
		for i in range(len(errorLogThisSession)):
			if currentTime-errorLogThisSession[i] >= 24*60*60:
				toDelete.append(i)

		for i in range(len(toDelete)-1, -1, -1):
			del errorLogThisSession[i]

		errorNumber = len(errorLogThisSession)
		debug("Errors in last 24 hours: {}".format(errorNumber), 1)

		if errorNumber >= ABNORMAL_ERRORS and time.time()-lastEmail >= 60*60:
			msg = """MuseBot is experiencing elevated error rates. In the last 24 hours it has
errored {} times. Action must be taken to resolve this.

This is an automated message.""".format(errorNumber)
			sendEmail("MuseBot is experiencing elevated error rates", msg)
			lastEmail = time.time()
		else:
			debug("Last email sent: {} seconds ago".format(time.time()-lastEmail))

		if ERRORS_FATAL:
			break
		elif errorNumber >= FATAL_ERROR_COUNT:
			debug("too many errors in the last 24 hours! Ending execution.", 2)
			break
		else:
			debug("waiting before restart")
			time.sleep(RESTART_TIMEOUT)
			debug("automatically restarting MuseBot", 1)
			try:
				HANDLER.reconnect()
			except Exception as e:
				debug("Error reconnecting: ")
				debug(traceback.format_exc(), 3)
				break

sendEmail("MuseBot finished execution", "MuseBot finished execution. This is an automated message.")
debug("finished execution successfully(?)", 1)
