#!/bin/sh

path=$1
N=$2
awk -f ~/scripts/show-top-nth.awk -v N=$N $path
