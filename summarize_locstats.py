#!/usr/bin/env python3

'''
Given a directory full of .dSYMs, extract the location statistics, e.g. with:

    for dsym in $(find . -type d -name \*.dSYM); do
      echo "On $dsym..."
      ~/src/builds/llvm-project-master-RA/bin/llvm-dwarfdump --statistics --arch arm64 $dsym > $dsym.locstats
    done

This script accepts a directory containing *.locstats files and prints out a
summary.
'''

import pathlib
import sys
import json

import numpy as np

def ratio(a, b):
    assert a >= 0 and b >= 0
    return float(a) / b if b != 0 else 0.0

def dirsize(path):
    return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())

class LocStats:
    statistics = (
        'dsym_size',
        'formal_param_coverage',
        'formal_param_coverage_no_entryvals',
        'all_var_coverage',
        'all_var_coverage_no_entryvals',
        'ratio_params_90pluspct_covered',
        'ratio_params_90pluspct_covered_no_entryvals',
    )

    def __init__(self, path):
        with path.open() as f:
            stats = json.loads(f.readline())
            self.name = path.name
            self.dsym_size = dirsize(path.with_suffix(''))
            self.formal_param_coverage = ratio(
                    stats['formal params scope bytes covered'],
                    stats['formal params scope bytes total'])
            self.formal_param_coverage_no_entryvals = ratio(
                    stats['formal params scope bytes covered'] - \
                         stats['formal params entry value scope bytes covered'],
                    stats['formal params scope bytes total'])
            self.all_var_coverage = ratio(
                    stats['vars scope bytes covered'],
                    stats['vars scope bytes total'])
            self.all_var_coverage_no_entryvals = ratio(
                    stats['vars scope bytes covered'] - \
                         stats['vars entry value scope bytes covered'],
                    stats['vars scope bytes total'])
            self.ratio_params_90pluspct_covered = ratio(
                    stats['params with [90%,100%) of its scope covered'] + \
                         stats['params with 100% of its scope covered'],
                    stats['total params procesed by location statistics'])
            self.ratio_params_90pluspct_covered_no_entryvals = ratio(
                    stats['params (excluding the debug entry values) with [90%,100%) of its scope covered'] + \
                         stats['params (excluding the debug entry values) with 100% of its scope covered'],
                    stats['total params procesed by location statistics'])

    def __str__(self):
        return '\n'.join(['name: ' + self.name] + \
                ['  - {0}: {1:.3f}'.format(field, getattr(self, field)) for field in self.statistics])

def param_coverage_for_dir(path):
    data = []
    for child in sorted(path.glob('*.locstats')):
        try:
            stats = LocStats(child)
        except:
            continue
        print(stats)
        data.append(stats)

    summary = []
    for field in LocStats.statistics:
        filtered_data = [getattr(stats, field) for stats in data]
        summary.append((field, np.mean(filtered_data), np.std(filtered_data)))

    print('=== Summary ===')
    print('{0} dSYMs processed.'.format(len(data)))
    for field, mean, std in summary:
        print('{0}: \t mean = {1:.3f} \t std = {2:.3f}'.format(field, mean, std))

    print('=== CSV Summary ===')
    for field, mean, std in summary:
        print('{0}, {1:.3f}, {2:.3f}'.format(field, mean, std))


if __name__ == '__main__':
    param_coverage_for_dir(pathlib.Path(sys.argv[1]))
