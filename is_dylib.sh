#!/bin/sh

file $1 | grep -q "dynamically linked shared library" || exit 1
