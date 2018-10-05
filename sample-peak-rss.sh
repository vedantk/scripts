#!/bin/bash

# Every second, grep `ps` output for <command-string> and keep track
# of the peak resident set size (max memory utilization) in kilobytes.

# Usage: ./sample-peak-rss.sh <command-string>

cmd=$1

if [ -z "$cmd" ]; then
	echo "Specify command string to monitor."
	exit 1
fi

sample_nr=1
peak_mem=0
while [ 1 ]; do
	ps_output=$(ps x -o rss,command | grep "$cmd" | sort | tail -n1)
	echo $ps_output

	cur_mem=$(echo $ps_output | awk '{ print $1; }')

	if [ "$cur_mem" -gt "$peak_mem" ]; then
		peak_mem=$cur_mem
	fi

	echo "Sample $sample_nr: current-rss=$cur_mem, peak-rss=$peak_mem"

	sample_nr=$((sample_nr+1))
	sleep 1
done
