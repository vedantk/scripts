from __future__ import print_function

import argparse
from collections import Counter
import optrecord
import pickle
import pprint

def get_callee_inlined_counts(remark_file, cost_mapping = dict(), update_cost_mapping = False):
    remarks = optrecord.get_remark_generator(remark_file, dict())

    inlinedCallees = []
    for remark in remarks:
        if remark.PassWithDiffPrefix != 'inline':
            continue

        if remark.Name == 'Inlined':
            callee = remark.Args[0][1][1]
            inlinedCallees.append(callee)
        elif update_cost_mapping and remark.Name == 'TooCostly':
            callee = remark.Args[0][1][1]
            cost = remark.Args[4][0][1]
            cost_mapping[callee] = int(cost)

    return Counter(inlinedCallees)

def dump(counts, filename):
    with open(filename, 'w') as f:
        pickle.dump(counts, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('baseline_yaml')
    parser.add_argument('new_yaml')
    args = parser.parse_args()

    cost_mapping = dict()
    baseline_counts = get_callee_inlined_counts(args.baseline_yaml, cost_mapping, True)
    new_counts = get_callee_inlined_counts(args.new_yaml, dict())

    print("Baseline inline counts:", args.baseline_yaml)
    pprint.pprint(baseline_counts.most_common(15))
    dump(baseline_counts, 'baseline_counts.pickle')

    print("New inline counts:", args.new_yaml)
    pprint.pprint(new_counts.most_common(15))
    dump(new_counts, 'new_counts.pickle')

    print("Callees which are inlined more aggressively (compared to the baseline):")
    diff_counts = new_counts - baseline_counts
    pprint.pprint(diff_counts.most_common(30))
    dump(diff_counts, 'diff_counts.pickle')

    cost_of_diff_counts = []
    for callee, increased_count in diff_counts.iteritems():
        cost = cost_mapping.get(callee, 0)
        if cost > 0:
            cost_of_diff_counts.append((callee, increased_count * cost))

    print("Most expensive inlining mistakes in the new binary:")
    cost_of_diff_counts.sort(key=lambda mistake: mistake[1])
    pprint.pprint(cost_of_diff_counts)


