#!/usr/bin/python

'''
Find this week's unloved patches
'''

from __future__ import print_function

import argparse
from collections import Counter
import re
import requests

thread_rx = re.compile(r'A href="(Week-of-[\w-]+/thread.html)"')
differential_rx = re.compile(r'\[PATCH\] D\d+: .*')
differential_title_rx = re.compile(r'\[PATCH\] (D\d+): (.*)')

def find_weekly_unloved_patches(index_url):
    # Grab the contents of the mailing list index.
    index_text = requests.get(index_url).text

    # Find the first (latest, presumably) link to a weekly thread listing.
    m = re.search(thread_rx, index_text)
    if not m:
        print('No weekly listing found :|')
        return

    # Piece together the full url of this week's thread listing.
    week_url = index_url + m.group(1)
    print('Looking at:', week_url)

    # Grab the weekly thread listing.
    week_text = requests.get(week_url).text

    # Count how many times we see each differential review.
    counts = Counter(re.findall(differential_rx, week_text))

    # Print out the lonely patches.
    for (patch, count) in counts.items():
        # This one's been commented on at least once. Skip it.
        if count > 1:
            continue
        
        m = re.match(differential_title_rx, patch)

        # This one's probably been committed. Skip it.
        title = m.group(2)
        if week_text.count(title) > 1:
            continue

        # Grab the contents of the review. This is a little expensive...
        DXXX = m.group(1)
        review = requests.get('http://reviews.llvm.org/{0}'.format(DXXX)).text

        # Skip the review if...
        if 'added inline comments' in review \
            or 'accepted this revision' in review \
            or 'abandoned this revision' in review \
            or 'added a comment' in review:
            continue

        print(patch)

if __name__ == '__main__':
    print("===== Clang =====")
    find_weekly_unloved_patches('http://lists.llvm.org/pipermail/cfe-commits/')

    print()

    print("===== LLVM =====")
    find_weekly_unloved_patches('http://lists.llvm.org/pipermail/llvm-commits/')
