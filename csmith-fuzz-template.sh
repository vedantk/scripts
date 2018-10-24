#!/bin/bash -x

CXX=/Users/vsk/src/builds/hot-cold-splitting-RA/bin/clang
CFLAGS="-w -Wno-error -Os -I /usr/local/include/csmith-2.3.0 -isysroot /Applications/LatestEverglades.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.14.sdk"

while [ 1 ]; do
	csmith -o test.c --concise --no-inline-function --quiet || exit 1

	$CXX $CFLAGS test.c -o test.baseline || exit 1
	baseline_crc=$(gtimeout 15s ./test.baseline)
	if [ "$?" -eq "124" ]; then
		continue
	fi

	$CXX $CFLAGS -mllvm -hot-cold-split=true test.c -o test.target || exit 1
	target_crc=$(gtimeout 15s ./test.target)
	if [ "$?" -eq "124" ]; then
		continue
	fi

	if [ "$baseline_crc" != "$target_crc" ]; then
		echo "CRC mismatch! Expected $baseline_crc but got $target_crc."
		exit 1
	fi
done
