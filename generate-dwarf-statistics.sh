#!/bin/bash

# Collate dwarfdump stats for all object files in a directory.

CONFIG_DIR=$1
DWARFDUMP=/Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bin/llvm-dwarfdump
DSYMUTIL=/Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bin/dsymutil
OUTPUT=$CONFIG_DIR/dwarf_stats.json

rm -f $OUTPUT
echo "[" >> $OUTPUT

# This approach only works for .o files:
# find $CONFIG_DIR -type f -name \*.o -exec $DWARFDUMP --statistics {} \; -exec echo "," \; >> $OUTPUT

for F in $(find $CONFIG_DIR -type f); do
	file $F | grep -q "Mach-O 64-bit executable x86_64"
	if [[ "$?" != "0" ]]; then
		continue
	fi

	echo -n "."
	$DSYMUTIL $F
	$DWARFDUMP --statistics $F.dSYM >> $OUTPUT
	echo "," >> $OUTPUT
done

sed -i '' -e '$ d' $OUTPUT # Delete the last comma :(.
echo "]" >> $OUTPUT
