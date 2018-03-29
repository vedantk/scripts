#!/usr/bin/env python

'''
Find binaries which contain trap instructions
'''

from __future__ import print_function

import argparse
import os
import re
import subprocess

def is_macho(path):
    try:
        test = subprocess.check_output('file "{0}"'.format(path), shell=True)
        return ': Mach-O' in test
    except:
        pass
    return False

def is_trapping_binary(path):
    if not is_macho(path):
        return False
    try:
        disasm = subprocess.check_output('otool -tv "{0}"'.format(path), shell=True)
        lines = disasm.split('\n')
        for i, line in enumerate(lines[1:]):
            prev_line = lines[i]
            if 'ud2' in line and 'call' not in prev_line:
                print("\n", end='')
                print(prev_line)
                print(line)
                return True
    except:
        pass
    return False

def find_trapping_binaries(path, excludes):
    for dirpath, dirnames, filenames in os.walk(path, followlinks=True):
        print(".", end='', sep='')

        if excludes:
            excluded_indices = [idx for idx, path in enumerate(dirnames)
                                if re.search(excludes, path)]
            for idx in reversed(excluded_indices):
                del dirnames[idx]
            
        for filename in filenames:
            if excludes and re.search(excludes, filename):
                continue
            fpath = os.path.join(dirpath, filename)
            if is_trapping_binary(fpath):
                print(" - Found trapping binary: {0}".format(fpath))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('--exclude', default='')
    args = parser.parse_args()

    excludes = None
    if args.exclude:
        excludes = re.compile(args.exclude)
    find_trapping_binaries(args.path, excludes)
