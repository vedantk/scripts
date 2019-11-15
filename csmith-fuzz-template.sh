#!/bin/bash -x

CXX=/Users/vsk/src/builds/llvm-project-master-RA/bin/clang
CFLAGS="-w -Wno-error -O2 -g -glldb -Xclang -femit-debug-entry-values -I $(echo /usr/local/include/csmith-*) -isysroot $(xcrun -sdk macosx -show-sdk-path)"

while [ 1 ]; do
	csmith -o test.c --concise --no-inline-function --quiet || exit 1

	$CXX $CFLAGS test.c -o test.baseline || exit 1
	baseline_crc=$(gtimeout 3s ./test.baseline)
	if [ "$?" -eq "124" ]; then
		echo "Killing test.baseline (timeout)"
		continue
	fi

	$CXX $CFLAGS -mllvm -hot-cold-split=true test.c -o test.target || exit 1

	diff test.baseline test.target
	if [ "$?" -eq "0" ]; then
		echo "Skipping input; baseline and target do not differ"
		continue
	fi

	target_crc=$(gtimeout 3s ./test.target)
	if [ "$?" -eq "124" ]; then
		echo "Killing test.target (timeout)"
		continue
	fi

	if [ "$baseline_crc" != "$target_crc" ]; then
		echo "CRC mismatch! Expected $baseline_crc but got $target_crc."
		exit 1
	fi
done
