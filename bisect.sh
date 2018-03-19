#!/bin/bash

C1=$TEST_PATH/usr/bin/clang
C2=$TEST_PATH/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang
C3=$TEST_PATH/bin/clang
STDERR=$TEST_PATH.0.stderr
if [ -e $C1 ]; then
	CLANG=$C1
elif [ -e $C2 ]; then
	CLANG=$C2
elif [ -e $C3 ]; then
	CLANG=$C3
else
	echo "Could not find clang in $TEST_PATH. Quitting."
	exit 1
fi

COV=$TEST_PATH/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/llvm-cov

echo "Clang = $CLANG"

if [ -e $COV ]; then
	echo "llvm-cov = $COV"
fi
