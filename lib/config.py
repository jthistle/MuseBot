#!/usr/bin/env python3

"""Non-environment-specific rules for MuseBot's behaviour"""

from .secrets import *

URL = "api.telegram.org"
REQUEST_URL = "/bot"+APIKEY+"/"
REQUEST_DELAY = 1	# second to wait between requests
HEADERS = {'Content-type': 'application/json'}
HTTP_ERRORS_FATAL = (409, 404)

# Grammar idents
PR_IDENT = "pr"
NODE_IDENT = "node"
CMD_IDENT = "cmd"

MUSESCORE_NODE_URL = "https://musescore.org/node/"
GITHUB_PULL_URL = "https://github.com/musescore/MuseScore/pull/"
GITHUB_COMMIT_URL = "https://github.com/musescore/MuseScore/commit/"

WEBHOOKS = ("push", "pull_request", "travis")
WEBHOOKS_DIR = "/home/james/MuseBot/queue/"     # this will almost certainly have to be changed

HELP_TEXT = "To use this bot, mention issues/nodes from musescore.org as #xxxxxx, and mention PRs as pr #xxxx. They will then be automatically linked."

ERRORS_FATAL = True
MAX_ACCEPTABLE_HOUR = 24
MAX_ACCEPTABLE_DAY  = 500	# After this many errors in 24 hours, stop trying to restart
RESTART_TIMEOUT = 5

FRIENDLY = True		# :)

DEBUG = True
DEBUG_TO_FILE = False
DEBUG_FILE = "log.txt"
DATA_FILE = "data.dat"
USERNAME = "musebotbot"

TESTING = False

# Import production config last to overwrite anything if needed
from .production import *
