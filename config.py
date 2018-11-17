#!/usr/bin/env python3

from secrets import *

URL = "api.telegram.org"
REQUEST_URL = "/bot"+APIKEY+"/"
REQUEST_DELAY = 1	# second to wait between requests
RESTART_TIMEOUT = 5
HEADERS = {'Content-type': 'application/json'}
HTTP_ERRORS_FATAL = (409, 404)

DEBUG_LEVELS = ["debug", "notice", "warning", "error"]

COMMANDS = ["mute", "unmute", "delete", "integrate", "unintegrate", "help"]

MUSESCORE_NODE_URL = "https://musescore.org/node/"
GITHUB_PULL_URL = "https://github.com/musescore/MuseScore/pull/"

WEBHOOKS = ["push", "pull_request"]
WEBHOOKS_DIR = "/var/www/html/queue/"

HELP_TEXT = "To use this bot, mention issues/nodes from musescore.org as #xxxxxx, and mention PRs as pr #xxxx. They will then be automatically linked."

MARKDOWN_ESCAPE = ["_", "*", "`", "[", "]"]
