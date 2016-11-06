#!/bin/bash
set -e
PATH="$PATH:./"

if [ "$1" = "--multi" ]; then
    MULTI=1
    shift
fi

if [ $# -ne 2 ]; then
    echo "Usage: $0 [--multi] test.sh source-to-reduce.c"
    exit 1
fi

printf "Sanity check... "
if ./$1; then
    echo "passed."
else
    echo "failed."
    exit 2
fi

if [ $MULTI ]; then
    for i in $(seq 0 5); do
        multidelta -level=$i ./$1 $2
    done
fi

while true; do
    cp $2 $2.baseline || exit 3

    delta "-test=$1" -in_place "$2"

    baseline_size=$(wc -l $2.baseline | awk '{print $1}')
    new_size=$(wc -l $2 | awk '{print $1}')
    if [ $baseline_size -eq $new_size ]; then
        echo "** Reached fixpoint!"
        exit 0
    fi
done
