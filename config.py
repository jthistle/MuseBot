#!/usr/bin/env python3

from secrets import *

URL = "api.telegram.org"
REQUEST_URL = "/bot"+APIKEY+"/"
REQUEST_DELAY = 1	# second to wait between requests
HEADERS = {'Content-type': 'application/json'}
HTTP_ERRORS_FATAL = (409, 404)

DEBUG_LEVELS = ["debug", "notice", "warning", "error"]

COMMANDS = ["mute", "unmute", "delete"]

MUSESCORE_NODE_URL = "https://musescore.org/node/"
GITHUB_PULL_URL = "https://github.com/musescore/MuseScore/pull/"
