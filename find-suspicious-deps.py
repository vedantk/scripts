#!/usr/bin/env python

'''Find suspicious dependencies in a ninja file.

Demo:

  $ cd llvm/DA
  $ ~/scripts/find-suspicious-deps.py build.ninja
  ...
  No symbols unique to lib/libLLVMVectorize.a were used by bin/llvm-extract
  No symbols unique to lib/libLLVMProfileData.a were used by bin/verify-uselistorder
  No symbols unique to tools/llvm-c-test/CMakeFiles/llvm-c-test.dir/include-all.c.o were used by bin/llvm-c-test
  ...
'''

from __future__ import print_function

import argparse
import functools
import re
import os
import subprocess
from collections import Counter

try:
    lru_cache = functools.lru_cache
except AttributeError as e:
    # Python 2 lacks lru_cache, so we fake it with a very basic memoize.
    def lru_cache(maxsize, typed):
        def memoize(f):
            class Memoizer(dict):
                def __missing__(self, key):
                    result = self[key] = f(key)
                    return result
            return Memoizer().__getitem__
        return memoize

@lru_cache(maxsize=4096, typed=True)
def symbols(path):
    # Get the symbols in the artifact.
    nm_out = subprocess.check_output(['nm', '-Uj', path])
    return set(nm_out.split(b'\n'))

@lru_cache(maxsize=4096, typed=True)
def is_build_artifact(path):
    # Make sure that the artifact exists.
    return os.access(path, os.F_OK)

interesting_dep = re.compile(r'.*\.(a|o|dylib)$')

def extract_build_edge(line):
    # Parse a build edge. Return (target, deps) if it's an interesting edge,
    # otherwise return None.
    deps = line.split()[1:]
    target = deps.pop(0)[:-1]
    rule = deps.pop(0)

    if 'EXECUTABLE_LINKER' not in rule and 'SHARED_LIBRARY_LINKER' not in rule:
        return None

    if not is_build_artifact(target):
        return None

    hard_deps = set()
    for dep in deps:
        if re.match(interesting_dep, dep):
            if not dep.startswith('|') and is_build_artifact(dep):
                hard_deps.add(dep)

    if not len(hard_deps):
        return None

    return (target, hard_deps)

def is_build_edge(line):
    return line.startswith('build ')

def build_hard_dep_graph(ninja_buffer):
    # Map: target -> [dep]
    build_graph = {}

    lines = ninja_buffer.split('\n')
    for line in lines:
        if not is_build_edge(line):
            continue

        edge = extract_build_edge(line)
        if not edge:
            continue

        target, hard_deps = edge
        build_graph[target] = hard_deps

    return build_graph

def find_suspicious_deps(ninja_buffer, targets):
    build_graph = build_hard_dep_graph(ninja_buffer)

    # Check if deps are actually used by their targets.
    for target, hard_deps in build_graph.items():
        if targets and not target in targets:
            continue
        target_syms = symbols(target)
        print("Analyzing target", target, "with", len(target_syms), "symbols")

        # If two deps provide the same symbol, don't count uses of that symbol
        # as uses of any deps.
        sym_counter = Counter()
        for dep in hard_deps:
            sym_counter.update(symbols(dep))
        common_syms = set([sym for sym, count in sym_counter.items() \
                               if count > 1])

        for dep in hard_deps:
            dep_syms = symbols(dep) - common_syms
            print("  -> Dep:", dep, "with", len(dep_syms), "unique symbols")
            if not len(target_syms.intersection(dep_syms)):
                yield target, dep

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('ninja_file', help='Path to the ninja file')
    parser.add_argument('targets', nargs='*',
                        help='Targets to consider')
    args = parser.parse_args()

    with open(args.ninja_file, 'r') as f:
        ninja_buffer = f.read()

    build_dir = os.path.dirname(args.ninja_file)
    if build_dir:
        os.chdir(build_dir)

    # Hack: Print debug messages before results.
    suspicious_deps = list(find_suspicious_deps(ninja_buffer, args.targets))

    for target, dep in suspicious_deps:
        print("No symbols unique to", dep, "were used by", target)
