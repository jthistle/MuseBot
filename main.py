#!/usr/bin/env python3

import traceback
from lib.musebot import MuseBot
from lib.getLogger import initLogger

if __name__ == "__main__":
    logger = initLogger()
    instance = MuseBot()

    try:
        instance.run()
    except Exception as e:
        logger.error("An error occurred: {}".format(e))
        logger.info(traceback.format_exc())

    # TODO: retry running
