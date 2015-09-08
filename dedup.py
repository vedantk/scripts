#!/usr/bin/python

description = '''
Scan a directory for duplicate files, removing all except the first duplicate.
'''

import os
import hashlib
import argparse
from collections import defaultdict

if __name__ == '__main__':
    args = argparse.ArgumentParser(description=description)
    args.add_argument('root')
    argv = args.parse_args()
    root = argv.root

    if not os.path.isdir(root):
        print('{0} must be a directory.'.format(root))

    hashes = defaultdict(list)
    for folder, subdirs, subfiles in os.walk(root):
        for entry in subfiles:
            full_path = os.path.join(folder, entry)
            print(':: {0}'.format(full_path))

            with open(full_path, 'rb') as f:
                h = hashlib.sha224(f.read()).hexdigest()
                if h in hashes[h]:
                    print('--> Found dup. Really delete? (Ctl-C to stop.)')
                    input()
                    os.remove(full_path)
                hashes[h].append(full_path)
