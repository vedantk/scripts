#!/bin/bash

~/src/builds/llvm-project-master-RA/bin/llc -O2 -debug-entry-values $1 -filetype=obj -o /dev/null 2>&1 | grep "Found a test case" && exit 0
exit 1
