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
	"$SRC_LOCATION"/main.py >> "$SRC_LOCATION"/output.txt &
	pid=$!
	wait $pid
  echo "run.sh: error encountered or closing"
done

exit 0
