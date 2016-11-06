#!/usr/bin/python

import os
import hashlib
import argparse
from collections import defaultdict

description = '''
Approximate the amount of space which could be saved by running dedup on the
given directory. Optional: run the dedup.
'''

def dedup_savings(Directory):
    Savings = 0
    TotalBytesScanned = 0
    Hashes = defaultdict(list)
    for (CurrentDir, SubDirs, SubFiles) in os.walk(Directory):
        for File in SubFiles:
            Path = os.path.join(CurrentDir, File)

            # Wrap FS operations in try/catch to be safe.
            try:
                FileHash, FileSize = compute_hash(Path)
            except:
                continue

            if not FileHash:
                continue

            # Register the file hash and file name for later deduping.
            Hashes[FileHash].append(Path)
            if len(Hashes[FileHash]) > 1:
                Savings += FileSize
            TotalBytesScanned += FileSize

    return Savings, TotalBytesScanned, Hashes

def compute_hash(Path):
    Stat = os.stat(Path)

    # Don't dedup dedup'd files.
    if Stat.st_nlink > 1:
        return None, None

    # Python bug: open() on 0-sized files causes crashes. 
    FileSize = Stat.st_size
    if FileSize == 0:
        return None, None

    # Ok, get the file hash for this file.
    with open(Path, 'rb') as F:
        return hashlib.sha1(F.read()).digest(), FileSize

def show_interesting_hashes(Hashes):
    for Hash, Files in Hashes.iteritems():
        if len(Files) > 1:
            print Hash, Files

def do_dedup(Hashes):
    for Hash, Files in Hashes.iteritems():
        if len(Files) == 1:
            continue

        OriginalFile, DupFiles = Files[0], Files[1:]
        for DupFile in DupFiles:
            try:
                os.remove(DupFile)
                os.link(OriginalFile, DupFile)
            except os:
                print "Failed to link", DupFile, "to", OriginalFile
                continue

if __name__ == '__main__':
    Parser = argparse.ArgumentParser(description=description)
    Parser.add_argument('directory', help='Directory to scan')
    Parser.add_argument('--show-hashes', action='store_true', default=False)
    Parser.add_argument('--do-dedup', action='store_true', default=False)
    Args = Parser.parse_args()

    Savings, TotalBytesScanned, Hashes = dedup_savings(Args.directory)
    print "You would save at most {0} bytes by dedup'ing {1}".format(
            Savings, Args.directory)
    print "That amounts to {0}% of the space currently used.".format(
            100 * Savings / float(TotalBytesScanned + 1))
    if Args.show_hashes:
        show_interesting_hashes(Hashes)

    if Args.do_dedup:
        do_dedup(Hashes)
