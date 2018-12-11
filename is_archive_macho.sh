#!/bin/sh

file $1 | grep -q Mach-O | grep -q "archive" || exit 1
exit 0
