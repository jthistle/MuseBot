#!/usr/bin/env bash

SRC_LOCATION=/home/pi/MuseBot

end=false

trap end_exec SIGINT
trap end_exec SIGTERM

function end_exec {
	end=true
	kill $pid
	echo "run.sh: cleaned up, exiting..."
	exit 0
}

pid=-1

echo "run.sh: running..."

while [ ! $end = true ]; do
	"$SRC_LOCATION"/main.py &
	pid=$!
	wait $pid
done

exit 0
