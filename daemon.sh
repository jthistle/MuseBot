#!/usr/bin/env bash

### BEGIN INIT INFO
# Provides:		    musebot
# Required-Start:	$remote_fs $syslog
# Required-Stop:	$remote_fs $syslog
# Default-Start:	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description:	Runs MuseBot
### END INIT INFO

# This script should be copied to /etc/init.d

SRC_LOCATION=/home/pi/MuseBot        # Change this to the absolute location of the musebot installation
PID_FILE=/tmp/musebot.pids

start() {
	echo "Starting..."
	if [ -f $PID_FILE ]; then
		echo "Service already started!"
	else
		"$SRC_LOCATION"/run.sh &
		echo $! >> $PID_FILE
	fi
}

stop() {
	echo "Stopping..."
	kill $(cat $PID_FILE)
	sudo rm $PID_FILE
	echo "Stopped."
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    status)
        ;;
    *)
	echo "Usage: $0 {start|stop|status|restart}"
	;;
esac

exit 0
