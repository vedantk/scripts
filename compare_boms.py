#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import pickle
import re

def pdump(message, path, val):
    print(message, path)
    with open(path, 'w') as f:
        pickle.dump(val, f)

def load_boms(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    bom = {}
    for line in lines:
        ent = line.split()
        if len(ent) != 2:
            continue

        filename = ent[0]
        size = int(ent[1])
        old_size = bom.get(filename, 0)
        bom[filename] = max(old_size, size)

    return bom

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('old_bom_path')
    parser.add_argument('new_bom_path')
    args = parser.parse_args()

    old_boms = load_boms(args.old_bom_path)
    new_boms = load_boms(args.new_bom_path)
    
    old_files = set(old_boms.keys())
    new_files = set(new_boms.keys())

    added_files = new_files - old_files
    pdump('Added in the new update:', 'added_files.pickle', added_files)

    removed_files = old_files - new_files
    pdump('Removed in the new update:', 'removed_files.pickle', removed_files)

    same_files = old_files.intersection(new_files)
    size_regressed_files = []
    for f in same_files:
        old_size = old_boms[f]
        new_size = new_boms[f]
        if new_size > 1.1*old_size:
            size_regressed_files.append((f, old_size, new_size, "{0:.2f}% regression".format((new_size/float(old_size) - 1.0) * 100.0)))

    size_regressed_files.sort(key=lambda ent: ent[2] - ent[1], reverse=True)

    pdump('Grew by 10% or more in the new update:', 'size_regressed_files.pickle', size_regressed_files)

    # Filter away some common kinds of items we don't really care about.
    filtered_regressions = []
    for ent in size_regressed_files:
        filename = ent[0]
        if 'DWARF' in filename:
            continue

        basename = os.path.basename(filename)
        if re.search('CodeResource|\.strings|\.plist|\.jpg|\.bom|\.h|\.png|\.car|\.a', basename):
            continue

        filtered_regressions.append(ent)

    pdump('Grew by 10% or more, and may be more interesting:', 'interesting_size_regressed_files.pickle', filtered_regressions)
