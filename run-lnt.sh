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

### # Baseline, -O0 -g.
### lnt runtest \
###         --submit $LNTSERVER/db_default/submitRun \
###         nt \
###         -j2 \
### 	--cc /Volumes/Builds/llvm.org-ubsan-alignment-R/bin/clang \
### 	--cxx /Volumes/Builds/llvm.org-ubsan-alignment-R/bin/clang++ \
###         --sandbox "$CLIENTSANDBOX" \
###         --test-suite $ROOTDIR/test-suite \
###         --test-externals $ROOTDIR/test-suite-externals \
###         --optimize-option -O0 \
###         --cflag -g \
###         --cflag -resource-dir --cflag /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/8.1.0 \
###         --cflag -isysroot --cflag /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk 
### 
### # UBSan, -O0 -g.
### lnt runtest \
###         --submit $LNTSERVER/db_default/submitRun \
###         nt \
###         -j2 \
### 	--cc /Volumes/Builds/llvm.org-ubsan-alignment-R/bin/clang \
### 	--cxx /Volumes/Builds/llvm.org-ubsan-alignment-R/bin/clang++ \
###         --sandbox "$CLIENTSANDBOX" \
###         --test-suite $ROOTDIR/test-suite \
###         --test-externals $ROOTDIR/test-suite-externals \
###         --optimize-option -O0 \
###         --cflag -g \
###         --cflag -fsanitize=undefined \
###         --cflag -fno-sanitize=bounds,enum,return \
###         --cflag -resource-dir --cflag /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/8.1.0 \
###         --cflag -isysroot --cflag /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk 

# Baseline
## lnt runtest \
##         --submit $LNTSERVER/db_default/submitRun \
##         nt \
##         -j4 \
## 	--cc $(xcrun -f clang) \
## 	--cxx $(xcrun -f clang++) \
##         --sandbox "$CLIENTSANDBOX" \
##         --test-suite $ROOTDIR/test-suite \
##         --optimize-option -O0 \
##         --cflag -resource-dir --cflag /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/9.0.0 \
##         --cflag -isysroot --cflag /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk 

## # Repeat baseline -O0
## lnt runtest \
##         --submit $LNTSERVER/db_default/submitRun \
##         nt \
##         -j4 \
## 	--cc /Volumes/Builds/llvm.org-master-R/bin/clang \
## 	--cxx /Volumes/Builds/llvm.org-master-R/bin/clang++ \
##         --sandbox "$CLIENTSANDBOX" \
##         --test-suite $ROOTDIR/test-suite \
##         --optimize-option -O0 \
##         --cflag -resource-dir --cflag /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/9.0.0 \
##         --cflag -isysroot --cflag /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk 

## # UBSan bare bones
## lnt runtest \
##         --submit $LNTSERVER/db_default/submitRun \
##         nt \
##         -j4 \
## 	--cc /Volumes/Builds/llvm.org-master-R/bin/clang \
## 	--cxx /Volumes/Builds/llvm.org-master-R/bin/clang++ \
##         --sandbox "$CLIENTSANDBOX" \
##         --test-suite $ROOTDIR/test-suite \
##         --optimize-option -O0 \
##         --cflag -static-libsan \
##         --cflag -fsanitize=returns-nonnull-attribute \
##         --cflag -resource-dir --cflag /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/9.0.0 \
##         --cflag -isysroot --cflag /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk 

# UBSan on by default, no signed overflow
lnt runtest \
        --submit $LNTSERVER/db_default/submitRun \
        nt \
        -j4 \
	--cc /Volumes/Builds/llvm.org-master-R/bin/clang \
	--cxx /Volumes/Builds/llvm.org-master-R/bin/clang++ \
        --sandbox "$CLIENTSANDBOX" \
        --test-suite $ROOTDIR/test-suite \
        --optimize-option -O0 \
        --cflag -static-libsan \
        --cflag -lc++abi \
        --cflag -fsanitize=builtin,float-cast-overflow,integer-divide-by-zero,nonnull-attribute,returns-nonnull-attribute,shift-exponent,vla-bound \
        --cflag -resource-dir --cflag /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/9.0.0 \
        --cflag -isysroot --cflag /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk 

# UBSan on by default
lnt runtest \
        --submit $LNTSERVER/db_default/submitRun \
        nt \
        -j4 \
	--cc /Volumes/Builds/llvm.org-master-R/bin/clang \
	--cxx /Volumes/Builds/llvm.org-master-R/bin/clang++ \
        --sandbox "$CLIENTSANDBOX" \
        --test-suite $ROOTDIR/test-suite \
        --optimize-option -O0 \
        --cflag -static-libsan \
        --cflag -lc++abi \
        --cflag -fsanitize=builtin,float-cast-overflow,integer-divide-by-zero,nonnull-attribute,returns-nonnull-attribute,shift-exponent,signed-integer-overflow,vla-bound \
        --cflag -resource-dir --cflag /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/9.0.0 \
        --cflag -isysroot --cflag /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk 
