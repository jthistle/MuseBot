#!/usr/bin/env python3

import traceback
import time
from lib.musebot import MuseBot
from lib.getLogger import initLogger
from lib.api.handler import ApiError
from lib.config import *

if __name__ == "__main__":
    logger = None
    instance = None

    errorTimes = []

    while True:
        try:
            # Init if we haven't already
            logger = logger or initLogger()
            instance = instance or MuseBot()

            # Run MuseBot!
            instance.run()
        except ApiError as e:
            logger.error("An API error occurred: {}".format(e.code))
            logger.info(traceback.format_exc())
            if e.code in (400, 403) and e.channel != 0:
                logger.info("Forbidden or bad response - removing channel {} from integrations".format(e.channel))
                instance.unintegrate(e.channel)
            elif e.code in HTTP_ERRORS_FATAL:
                logger.info("Error code {} is fatal".format(e.code))
                break
            else:
                logger.info("Error code {} is NOT fatal".format(e.code))
        except Exception as e:
            logger.error("An error occurred: {}".format(e))
            logger.info(traceback.format_exc())

        # Check if we should end execution
        now = time.time()
        errorTimes.append(now)

        hourInSeconds = 60 * 60
        dayInSeconds = 24 * hourInSeconds

        lastHour = 0
        for i in range(len(errorTimes) - 1, -1, -1):
            t = errorTimes[i]
            if now - t < hourInSeconds:
                lastHour += 1
            elif now - t > dayInSeconds:
                del errorTimes[i]

        lastDay = len(errorTimes)

        if lastHour > MAX_ACCEPTABLE_HOUR:
            logger.info("Hit the maximum number of errors in an hour. Ending execution.")
            break
        elif lastDay > MAX_ACCEPTABLE_DAY:
            logger.info("Hit the maximum number of errors in a day. Ending execution.")
            break

        logger.info("Errors in the last hour (day): {} ({})".format(lastHour, lastDay))

        logger.info("Waiting before restarting MuseBot...")
        time.sleep(RESTART_TIMEOUT)

    logger.info("MuseBot ended execution.")
