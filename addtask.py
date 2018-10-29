#!/usr/bin/env python3

import sys
import shelve
from secrets import *

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
from functions import *

if len(sys.argv) > 0:
	task = sys.argv[0]

	if task == "dailyReport":
		addTask("dailyReport")
