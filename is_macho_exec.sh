#!/bin/sh

file $1 | grep -q "Mach-O 64-bit executable" || exit 1
