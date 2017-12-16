#!/bin/sh

grep -E "build [^: ]+: " $1 | cut -d':' -f1 | cut -d' ' -f2
