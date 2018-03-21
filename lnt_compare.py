#!/usr/bin/env python

import json, os, argparse, sys, numpy

time_metric = "exec_time"
size_metric = "size.__TEXT,__text"

def read_lit_json(filename):
    jsondata = json.load(open(filename))
    names = set()
    if 'tests' not in jsondata:
        print "%s: Could not find toplevel 'tests' key" % filename
        sys.exit(1)

    tests = {}
    for test in jsondata['tests']:
        name = test.get("name")
        if name is None:
            print "Error: Found unnamed test"
            sys.exit(1)
        if name in names:
            sys.stderr.write("Error: Multiple tests with name '%s'\n" % name)
            sys.exit(1)
        names.add(name)
        if test.get('code') != "PASS":
            print "Error: '%s' did not pass" % name
            print test
            sys.exit(1)
        if "metrics" not in test:
            print "Error: '%s' has no metrics!" % name
            sys.exit(1)
        metrics = test["metrics"]
        for metric in (size_metric, time_metric):
            if metric not in metrics:
                print "Error: '%s' has no '%s' info" % (name, metric)
                sys.exit(1)
        tests[name] = test
    return tests

def find_nested_json_output(name):
    if os.path.isdir(name):
        files = os.listdir(name)
        for sub_file in files:
            fname = os.path.join(name, sub_file)
            if os.path.isdir(fname) and sub_file.startswith('test-'):
                nested_files = os.listdir(fname)
                for sub_sub_file in nested_files:
                    if sub_sub_file.startswith('output') and \
                            sub_sub_file.endswith('.json'):
                        return os.path.join(fname, sub_sub_file)
    return name

def verify_compatible(lhsdata, rhsdata):
    assert len(lhsdata) == len(rhsdata)
    assert lhsdata.keys() == rhsdata.keys()

def compare(config, lhs, rhs):
    lhs = find_nested_json_output(lhs)
    rhs = find_nested_json_output(rhs)

    lhsdata = read_lit_json(lhs)
    rhsdata = read_lit_json(rhs)
    verify_compatible(lhsdata, rhsdata)

    lhs_times = []
    time_overheads = []
    lhs_sizes = []
    size_overheads = []
    for name, lhs_test in lhsdata.items():
        lhs_test_m = lhs_test['metrics']
        rhs_test_m = rhsdata[name]['metrics']

        lhs_times.append(lhs_test_m[time_metric])
        time_overhead = rhs_test_m[time_metric] - lhs_test_m[time_metric]
        time_overheads.append(time_overhead)

        lhs_sizes.append(lhs_test_m[size_metric])
        size_overhead = rhs_test_m[size_metric] - lhs_test_m[size_metric]
        size_overheads.append(size_overhead)

    mean_time_overhead = numpy.mean(time_overheads) / numpy.mean(lhs_times)
    mean_size_overhead = numpy.mean(size_overheads) / numpy.mean(lhs_sizes)
    print ','.join([config, "{:.2%}".format(mean_time_overhead), "{:.2%}".format(mean_size_overhead)])

def read_dwarf_json(dirname):
    fname = os.path.join(dirname, 'dwarf_stats.json')
    return json.load(open(fname))

def get_mean_scope_coverage(dwarf_stats):
    coverage = []
    for stats in dwarf_stats:
        covered = stats["scope bytes covered"]
        total = stats["scope bytes total"]
        if total == 0: continue
        cov_ratio = covered / float(total)
        coverage.append(cov_ratio)
    return numpy.mean(coverage)

def get_var_availability(dwarf_stats):
    availability = []
    for stats in dwarf_stats:
        with_loc = stats["variables with location"]
        inlined = stats["inlined functions"]
        if inlined == 0: continue
        with_loc = float(with_loc) / inlined
        unique_vars = stats["unique source variables"]
        if unique_vars == 0: continue
        avail_ratio = with_loc / float(unique_vars)
        availability.append(avail_ratio)
    return numpy.mean(availability)

def compare_dwarf(config, lhs, rhs):
    lhsdata = read_dwarf_json(lhs)
    rhsdata = read_dwarf_json(rhs)

    lhs_scope_cov = get_mean_scope_coverage(lhsdata)
    rhs_scope_cov = get_mean_scope_coverage(rhsdata)

    lhs_var_avail = get_var_availability(lhsdata)
    rhs_var_avail = get_var_availability(rhsdata)

    scope_cov_incr = (rhs_scope_cov / lhs_scope_cov) - 1.0
    var_avail_incr = (rhs_var_avail / lhs_var_avail) - 1.0
    print ','.join([config, "{:.2%}".format(scope_cov_incr), "{:.2%}".format(var_avail_incr)])

if __name__ == '__main__':
    # Missing data:
    # stepanov_v1p2: {u'output': u"\n/Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/tools/timeit --limit-core 0 --limit-cpu 7200 --timeout 7200 --limit-file-size 104857600 --limit-rss-size 838860800 --append-exitstatus --redirect-output /Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/SingleSource/Benchmarks/Misc-C++/Output/stepanov_v1p2.test.out --redirect-input /dev/null --summary /Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/SingleSource/Benchmarks/Misc-C++/Output/stepanov_v1p2.test.time /Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/SingleSource/Benchmarks/Misc-C++/stepanov_v1p2\n/Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/tools/fpcmp -a 0.01 /Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/SingleSource/Benchmarks/Misc-C++/Output/stepanov_v1p2.test.out /Users/vsk/llvm-test-suite/SingleSource/Benchmarks/Misc-C++/stepanov_v1p2.reference_output\n\n/Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/tools/fpcmp: FP Comparison failed, not a numeric difference between 't' and '\n'\n", u'code': u'FAIL', u'name': u'test-suite :: SingleSource/Benchmarks/Misc-C++/stepanov_v1p2.test', u'elapsed': 6.98985481262207}

    # Baseline

    print "-O0"
    print "Configuration,Time Overhead,Size Overhead"
    compare("-O1", 'config-O1-g', 'config-O0-g')
    # compare("-O1 -flto", 'config-O1-flto-g', 'config-O0-g') # (Missing data: stepanov_v1p2)
    compare("-Os", 'config-Os-g', 'config-O0-g')
    compare("-Os -flto", 'config-Os-flto-g', 'config-O0-g')
    compare("-O2", 'config-O2-g', 'config-O0-g')
    compare("-O2 -flto", 'config-O2-flto-g', 'config-O0-g')

    print

    # Performance comparison

    print "-extend-lifetimes=this"
    print "Configuration,Time Overhead,Size Overhead"
    compare("-O1", 'config-O1-g', 'config-O1-Xclang-extend-lifetimes=this-g')
    # compare("-O1 -flto", 'config-O1-flto-g', 'config-O1-Xclang-extend-lifetimes=this-flto-g') # (Missing data: stepanov_v1p2)
    compare("-Os", 'config-Os-g', 'config-Os-Xclang-extend-lifetimes=this-g')
    compare("-Os -flto", 'config-Os-flto-g', 'config-Os-Xclang-extend-lifetimes=this-flto-g')
    compare("-O2", 'config-O2-g', 'config-O2-Xclang-extend-lifetimes=this-g')
    compare("-O2 -flto", 'config-O2-flto-g', 'config-O2-Xclang-extend-lifetimes=this-flto-g')

    print

    print "-extend-lifetimes=arguments"
    print "Configuration,Time Overhead,Size Overhead"
    compare("-O1", 'config-O1-g', 'config-O1-Xclang-extend-lifetimes=arguments-g')
    # compare("-O1 -flto", 'config-O1-flto-g', 'config-O1-Xclang-extend-lifetimes=arguments-flto-g') # (Missing data: stepanov_v1p2)
    compare("-Os", 'config-Os-g', 'config-Os-Xclang-extend-lifetimes=arguments-g')
    compare("-Os -flto", 'config-Os-flto-g', 'config-Os-Xclang-extend-lifetimes=arguments-flto-g')
    compare("-O2", 'config-O2-g', 'config-O2-Xclang-extend-lifetimes=arguments-g')
    compare("-O2 -flto", 'config-O2-flto-g', 'config-O2-Xclang-extend-lifetimes=arguments-flto-g')

    print

    print "-extend-lifetimes=all"
    print "Configuration,Time Overhead,Size Overhead"
    compare("-O1", 'config-O1-g', 'config-O1-Xclang-extend-lifetimes=all-g')
    # compare("-O1 -flto", 'config-O1-flto-g', 'config-O1-Xclang-extend-lifetimes=all-flto-g') # (Missing data: stepanov_v1p2)
    compare("-Os", 'config-Os-g', 'config-Os-Xclang-extend-lifetimes=all-g')
    compare("-Os -flto", 'config-Os-flto-g', 'config-Os-Xclang-extend-lifetimes=all-flto-g')
    compare("-O2", 'config-O2-g', 'config-O2-Xclang-extend-lifetimes=all-g')
    compare("-O2 -flto", 'config-O2-flto-g', 'config-O2-Xclang-extend-lifetimes=all-flto-g')

    print

    # DWARF statistics comparison

    print "-extend-lifetimes=this"
    print "Configuration,Scope Coverage Increase,Variable Availability Increase"
    compare_dwarf("-O1", 'config-O1-g', 'config-O1-Xclang-extend-lifetimes=this-g')
    compare_dwarf(" vs. -O0", 'config-O0-g', 'config-O1-Xclang-extend-lifetimes=this-g')
    compare_dwarf("-Os", 'config-Os-g', 'config-Os-Xclang-extend-lifetimes=this-g')
    compare_dwarf(" vs. -O0", 'config-O0-g', 'config-Os-Xclang-extend-lifetimes=this-g')
    compare_dwarf("-O2", 'config-O2-g', 'config-O2-Xclang-extend-lifetimes=this-g')
    compare_dwarf(" vs. -O0", 'config-O0-g', 'config-O2-Xclang-extend-lifetimes=this-g')

    print

    print "-extend-lifetimes=arguments"
    print "Configuration,Scope Coverage Increase,Variable Availability Increase"
    compare_dwarf("-O1", 'config-O1-g', 'config-O1-Xclang-extend-lifetimes=arguments-g')
    compare_dwarf(" vs. -O0", 'config-O0-g', 'config-O1-Xclang-extend-lifetimes=arguments-g')
    compare_dwarf("-Os", 'config-Os-g', 'config-Os-Xclang-extend-lifetimes=arguments-g')
    compare_dwarf(" vs. -O0", 'config-O0-g', 'config-Os-Xclang-extend-lifetimes=arguments-g')
    compare_dwarf("-O2", 'config-O2-g', 'config-O2-Xclang-extend-lifetimes=arguments-g')
    compare_dwarf(" vs. -O0", 'config-O0-g', 'config-O2-Xclang-extend-lifetimes=arguments-g')

    print

    print "-extend-lifetimes=all"
    print "Configuration,Scope Coverage Increase,Variable Availability Increase"
    compare_dwarf("-O1", 'config-O1-g', 'config-O1-Xclang-extend-lifetimes=all-g')
    compare_dwarf(" vs. -O0", 'config-O0-g', 'config-O1-Xclang-extend-lifetimes=all-g')
    compare_dwarf("-Os", 'config-Os-g', 'config-Os-Xclang-extend-lifetimes=all-g')
    compare_dwarf(" vs. -O0", 'config-O0-g', 'config-Os-Xclang-extend-lifetimes=all-g')
    compare_dwarf("-O2", 'config-O2-g', 'config-O2-Xclang-extend-lifetimes=all-g')
    compare_dwarf(" vs. -O0", 'config-O0-g', 'config-O2-Xclang-extend-lifetimes=all-g')
