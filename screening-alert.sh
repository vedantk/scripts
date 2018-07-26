#!/bin/bash

NAME=vsk
EMAIL=vsk@apple.com
LLVMREVF=build/last-rev-llvm
CLANGREVF=build/last-rev-clang
COMPILER_RT_REVF=build/last-rev-compiler-rt
SWIFT_REVF=build/last-rev-swift
BASEDIR=/Users/vk/Desktop/screener-llvm

WATCHING="prof|lib/Bitcode|tools/verify-uselistorder|docs/LangRef|lib/MC|llvm/MC|Function|LLVMContext|PGO|ProfileData|Instrumentation|SourceManager|FileManager|llvm-cov|llvm-as|clang/Basic|clang/Frontend|lib/Basic|lib/Frontend|clang/Driver|lib/Driver|tools/driver|profile|Coverage|c-index|libclang"

cd $BASEDIR

[ -e $LLVMREVF ] || echo HEAD > $LLVMREVF
[ -e $CLANGREVF ] || echo HEAD > $CLANGREVF
[ -e $COMPILER_RT_REVF ] || echo HEAD > $COMPILER_RT_REVF
[ -e $SWIFT_REVF ] || echo HEAD > $SWIFT_REVF

could_not_update() {
	mail -s "[CommitScreener] Could not update llvm" $EMAIL <<EOF
your robot overlords are displeased
EOF
	exit 1
}

~/scripts/git-lmap checkout master || could_not_update
~/scripts/git-lmap pull origin master || could_not_update

alert_about() {
	COMMIT=$1
	PROJECT=$2
	if [ $(git show $COMMIT | wc -l | xargs) -le 1000 ]; then
		SUMMARY=$(git show $COMMIT)
	else
		SUMMARY="Sorry! The summary is too large to display here."
	fi
	mail -s "[CommitScreener] Please review $PROJECT/$COMMIT" $EMAIL <<EOF
Hello $NAME,

You should take a close look at $PROJECT/$COMMIT.

$(git show $COMMIT --stat)

================================================================================

$SUMMARY

thanks,
your robot overlords
EOF
}

screen_project() {
	PROJECT=$1
	REVFILE=$2
	LASTREV=$(cat $REVFILE)
	for COMMIT in $(git log $LASTREV..HEAD --oneline | cut -d' ' -f1); do
		git show $COMMIT --oneline --stat | grep -E $WATCHING && alert_about $COMMIT $PROJECT
	done
	echo $(git show HEAD --oneline | head -n1 | cut -d' ' -f1) > $REVFILE
}

screen_project llvm $BASEDIR/$LLVMREVF

cd tools/clang
screen_project clang $BASEDIR/$CLANGREVF
cd -

cd projects/compiler-rt
screen_project compiler-rt $BASEDIR/$COMPILER_RT_REVF
cd -

cd tools/swift
screen_project swift $BASEDIR/$SWIFT_REVF
cd -
