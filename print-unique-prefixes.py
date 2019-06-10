#!/usr/bin/env python

import fileinput

lines = []
for line in fileinput.input():
    lines.append(line.strip())

lines.sort()

last = lines[0]
filtered = [lines[0]]

for i in range(1, len(lines)):
    if lines[i].startswith(last):
        continue

    last = lines[i]
    filtered.append(last)

for line in filtered:
    print line
