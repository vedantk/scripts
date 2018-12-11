#!/bin/sh

file $1 | grep -q Mach-O || exit 1
file $1 | grep -qv "archive"
