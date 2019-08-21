#!/usr/bin/env python3

"""Helper functions that don't need to be attached to the MuseBot object"""

import urllib.request
import re


def checkExists(url):
    try:
        urllib.request.urlopen(url)
    except urllib.error.URLError:
        return False
    return True


def inText(needles, haystack, separate = False, caseSensitive = False):
    if not separate:
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


def getRedirectedURL(url):
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
    request = opener.open(url)
    return request.url


def sanitizeText(text):
	# Remove any dodgy tags < >
	text = text.replace("<", "&lt;")
	text = text.replace(">", "&gt;")
	return text
