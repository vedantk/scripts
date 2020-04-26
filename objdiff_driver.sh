#!/bin/bash

for LHS in $(find $1 -name \*.o); do
	RHS=$(echo $LHS | sed "s/$1/$2/")
	if [ ! -f "$RHS" ]; then
		echo "Skipping $LHS, no '$RHS'"
		continue
	fi
	echo "Comparing: $LHS to $RHS"
	~/scripts/objdiff.sh $LHS $RHS || exit 1
done
