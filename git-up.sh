#!/bin/bash -x

function cmd() {
  $@ || exit 1
}

function squeaky() {
  if [ -n "`git status -uno -s --porcelain`" ]; then
    echo "You have unstashed changes. Can not update repository..."
    git status -uno
    exit 1
  fi
}

cd ~/Desktop/llvm

squeaky
cmd git checkout master
cmd git fetch
cmd git svn rebase -l

cd tools/clang
squeaky
cmd git checkout master
cmd git fetch
cmd git svn rebase -l
cd -

if [ "$1" == "--retag" ]; then
	find lib include tools/clang/lib tools/clang/include | grep -E "\.(c|h)(pp)?$" > build/tags.lst
	cscope -i build/tags.lst -qb
	/usr/local/bin/ctags -L build/tags.lst
fi

exit 0
