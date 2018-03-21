#!/bin/bash

# Collate dwarfdump stats for all object files in a directory.

CONFIG_DIR=$1
DWARFDUMP=/Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bin/llvm-dwarfdump
OUTPUT=$CONFIG_DIR/dwarf_stats.json

rm $OUTPUT
echo "[" >> $OUTPUT
find $CONFIG_DIR -type f -name \*.o -exec $DWARFDUMP --statistics {} \; -exec echo "," \; >> $OUTPUT
sed -i '' -e '$ d' $OUTPUT # Delete the last comma :(.
echo "]" >> $OUTPUT
