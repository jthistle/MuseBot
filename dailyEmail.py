#!/usr/bin/env python3

# This should be run on a crontab, preferably every hour, at least once a day

import traceback

from functions import *

try:
	errors = getErrorCount()
	msg = """In the last 24 hours MuseBot errored {} times""".format(errors)
	sendEmail("Daily update", msg)
except Exception as e:
	debug(traceback.format_exc(), 3)
