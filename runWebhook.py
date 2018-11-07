#!/usr/bin/env python3

# Currently only dryruns

import traceback, sys

from functions import *

def main():
	debug("dryrun, webhook", 1)
	if "eventPush" in sys.argv:
		debug("dryrun, eventPush", 1)

try:
	main()
except Exception as e:
	debug(traceback.format_exc(), 3)