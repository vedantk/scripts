#!/bin/bash -x

CXX=/Users/vsk/src/builds/llvm-project-master-RA/bin/clang
CFLAGS="-w -Wno-error -O2 -g -glldb -Xclang -femit-debug-entry-values -I $(echo /usr/local/include/csmith-*) -isysroot $(xcrun -sdk macosx -show-sdk-path)"

while [ 1 ]; do
	csmith -o test.c --concise --no-inline-function --quiet || exit 1

	$CXX $CFLAGS test.c -c -o test.o || exit 1
done
