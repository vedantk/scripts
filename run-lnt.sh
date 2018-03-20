#!/bin/bash

source bin/activate

runtest() {
  flags=$1
  name="config$(echo $1 | sed 's/ //g')"
  sandbox_dir=~/src/builds/llvm.org-extend-lifetimes-R/bench/$name
  mkdir $sandbox_dir
  lnt runtest test-suite \
  	  --sandbox $sandbox_dir \
  	  --cc ~/src/builds/llvm.org-extend-lifetimes-R/bin/clang \
  	  --test-suite ~/llvm-test-suite \
  	  --test-externals ~/llvm-test-suite-externals \
  	  --use-cmake="$(xcrun -f cmake)" \
  	  --use-lit=/Users/vsk/src/builds/llvm.org-extend-lifetimes-RA/bin/llvm-lit \
  	  --threads 10 \
  	  --build-threads 20 \
  	  --benchmarking-only \
  	  --cppflags="$flags" 2>&1 | tee $sandbox_dir/log
}

LEXT_THIS="-Xclang -extend-lifetimes=this"
LEXT_ARGS="-Xclang -extend-lifetimes=arguments"
LEXT_FULL="-Xclang -extend-lifetimes=all"

OPT_LEVELS=("-O1" "-Os" "-O2")

runtest "-O0 -g"

for opt_lvl in ${OPT_LEVELS[@]}; do
  runtest "$opt_lvl -g"
  runtest "$opt_lvl -flto -g"

  runtest "$opt_lvl $LEXT_THIS -g"
  runtest "$opt_lvl $LEXT_THIS -flto -g"

  runtest "$opt_lvl $LEXT_ARGS -g"
  runtest "$opt_lvl $LEXT_ARGS -flto -g"

  runtest "$opt_lvl $LEXT_FULL -g"
  runtest "$opt_lvl $LEXT_FULL -flto -g"
done
