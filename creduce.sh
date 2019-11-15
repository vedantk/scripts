#!/bin/bash

CXX=/Users/vsk/src/builds/llvm-project-master-RA/bin/clang
CFLAGS="-w -Wno-error -O2 -g -glldb -Xclang -femit-debug-entry-values -I $(echo /usr/local/include/csmith-*) -isysroot $(xcrun -sdk macosx -show-sdk-path)"

$CXX $CFLAGS unreduced.c 2>&1 | grep "Found a test case" && exit 0
exit 1
