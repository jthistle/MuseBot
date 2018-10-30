#!/usr/bin/env python3

# This should be run on a crontab, preferably every hour, at least once a day

import traceback

from functions import *

try:
	updateLog()
except Exception as e:
	debug(traceback.format_exc(), 3)