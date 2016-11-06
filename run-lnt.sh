#!/bin/bash -x

ROOTDIR=$HOME
TMPDIR=/tmp/lnt
LNTHOST=localhost

# This apparently _has_ to be 8000.
# Don't ask why.
LNTPORT=8000

LNTSERVER=http://$LNTHOST:$LNTPORT

# Install lnt.
sudo python lnt/setup.py develop

# Setup client sandbox.
CLIENTSANDBOX="$TMPDIR/sandbox.client"
mkdir -p "$CLIENTSANDBOX"

# ONLY_TEST=SingleSource/Benchmarks/SmallPT

# # Baseline, no instr
## lnt runtest \
##         --submit $LNTSERVER/db_default/submitRun \
##         nt \
##         --sandbox "$CLIENTSANDBOX" \
##         --cc /Users/vk/Desktop/llvm/DA/bin/clang \
##         --cxx /Users/vk/Desktop/llvm/DA/bin/clang++ \
##         --test-suite $ROOTDIR/test-suite \
##         --test-externals $ROOTDIR/test-suite-externals \
##         --only-test $ONLY_TEST \
##         --optimize-option -O2
