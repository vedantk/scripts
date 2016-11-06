#!/bin/bash

NINJA=$1

grep -E "build [^:]+:" $NINJA | cut -d':' -f1 | cut -d' ' -f2
