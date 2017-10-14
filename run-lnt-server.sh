#!/bin/bash -x

ROOTDIR=$HOME
TMPDIR=/tmp/lnt
LNTHOST=localhost

rm -rf $TMPDIR

# This apparently _has_ to be 8000.
# Don't ask why.
# Just kill -9 the lnt server if you want to run this again.
LNTPORT=8000

mkdir -p $TMPDIR

# Install lnt.
sudo xcrun python lnt/setup.py develop

# Setup sandbox.
SERVERSANDBOX="$TMPDIR/sandbox.server"
lnt create "$SERVERSANDBOX"
lnt runserver "$SERVERSANDBOX" --hostname "$LNTHOST"
