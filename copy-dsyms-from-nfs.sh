#!/bin/bash

TRAIN=$1
UPDATE=$2

if [ -z "$TRAIN" ] || [ -z "$UPDATE" ]; then
	echo "Usage: <train> <update>"
	exit 1
fi

COPYDIR="$HOME/Desktop/$TRAIN-$UPDATE-dSYMs"
mkdir -p $COPYDIR || exit 1

cd ~rc/Software/$TRAIN/Updates/$UPDATE/Symbols

echo "Copying dSYMs into $COPYDIR..."

copy_dsym() {
	PROJECT=$1
	COPY_NR=$2
	echo "Visiting $PROJECT (copy number $COPY_NR)..."
	for ARCHIVE in $(ls $PROJECT | grep .dSYM.yaa | head -n1); do
		PROJ_ARCHIVE="$PROJECT/$ARCHIVE"

  		DEST="$COPYDIR/$(basename $ARCHIVE .yaa)"
  		if [ -d "$DEST" ]; then
  			echo "Copy of $PROJ_ARCHIVE exists, skipping..."
  			continue
		fi

  		echo "Copying $PROJ_ARCHIVE..."
		yaa extract -t 1 -i $PROJ_ARCHIVE -d $DEST || rm -rf $DEST
	done
}

COPIES=0
for PROJECT in $(ls); do
	grep -q "$PROJECT" ~/Desktop/SharedCacheDylibPaths.txt
	if [[ "$?" -ne "0" ]]; then
		continue
	fi

	copy_dsym $PROJECT $COPIES &

	# Launching > 600 processes to copy files over NFS results
	# in many of those files being corrupted. Work around the problem
	# by rate-limiting ourselves.
	COPIES=$((COPIES+1))
	if [ "$COPIES" -eq "100" ]; then
		wait
		COPIES=0
	fi
done

wait
