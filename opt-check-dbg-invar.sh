#!/bin/bash

OPT=$1
shift 1

TEST_FILE=$1
shift 1

strip_cmd() {
	$OPT -disable-verify -strip -strip-dead-prototypes -strip-named-metadata -o - $* 
}

unstripped_log=$(mktemp)
strip_cmd $TEST_FILE | $OPT $* > $unstripped_log
result="$?"
if [[ $result != "0" ]]; then
	rm $unstripped_log
	echo ":: The baseline had errors ($result), skipping"
	exit 0
fi

baseline_log=$(mktemp)
cat $unstripped_log | strip_cmd -S > $baseline_log
rm $unstripped_log

with_di_log=$(mktemp)
strip_cmd $TEST_FILE | $OPT $* -disable-verify -debugify-quiet -debugify-each | strip_cmd -S > $with_di_log

echo "Comparing: $* $TEST_FILE"
echo "  Baseline: $baseline_log"
echo "  With DI : $with_di_log"

diff $baseline_log $with_di_log
result="$?"

if [[ $result == "0" ]]; then
	rm $baseline_log $with_di_log
	exit 0
else
	echo ":: Found a test case ^"
	exit $result
fi
