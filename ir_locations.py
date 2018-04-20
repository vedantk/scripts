#!/usr/bin/env python

import re, sys

dbg_rx = re.compile(r'!dbg !(\d+)')
diloc_rx = re.compile(r'!(\d+) = !DILocation\(line: (\d+), column: (\d+)')
decl_rx = re.compile(r'define .* (@\w+)')

with open(sys.argv[1], 'r') as f:
    lines = f.readlines()

# Map metadata numbers to dilocations.
diloc_map = {}
for line in lines:
    m = re.search(diloc_rx, line)
    if not m:
        continue

    metadata_num, line, col = m.groups()
    diloc_map[metadata_num] = 'loc {0}:{1}'.format(line, col)

# Print out function declarations and dilocations sequentially.
for line in lines:
    m = re.search(decl_rx, line)
    if m:
        print m.group(1)
        continue

    m = re.search(dbg_rx, line)
    if m:
        metadata_num = m.group(1)
        if metadata_num not in diloc_map:
            continue
        print diloc_map[metadata_num]
        
