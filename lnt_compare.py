#!/usr/bin/env python

import json, os, argparse, sys, numpy, re

time_metric = "exec_time"
size_metric = "size.__TEXT,__text"

def memoize(f):
    class Memoizer(dict):
        def __missing__(self, key):
            result = self[key] = f(key)
            return result
    return Memoizer().__getitem__

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

@memoize
def read_lit_json(filename):
    filename = find_nested_json_output(filename)
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

def verify_compatible(lhsdata, rhsdata):
    assert len(lhsdata) == len(rhsdata)
    assert lhsdata.keys() == rhsdata.keys()

def get_mean_exec_time(stats):
    return numpy.mean([test['metrics'][time_metric] for test in stats.values()])

def get_mean_binary_size(stats):
    return numpy.mean([test['metrics'][size_metric] for test in stats.values()])

def compare(config, lhs, rhs):
    lhsdata = read_lit_json(lhs)
    rhsdata = read_lit_json(rhs)
    verify_compatible(lhsdata, rhsdata)
    lhs_mean_time = get_mean_exec_time(lhsdata)
    rhs_mean_time = get_mean_exec_time(rhsdata)
    lhs_mean_size = get_mean_binary_size(lhsdata)
    rhs_mean_size = get_mean_binary_size(rhsdata)
    mean_time_overhead = (rhs_mean_time - lhs_mean_time) / lhs_mean_time
    mean_size_overhead = (rhs_mean_size - lhs_mean_size) / lhs_mean_size
    print ','.join([config, "{:.2%}".format(mean_time_overhead), "{:.2%}".format(mean_size_overhead)])

@memoize
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
        src_funcs = stats["source functions"]
        inlined = stats["inlined functions"]
        if inlined == 0: continue
        normalizer = src_funcs / float(inlined)
        avail_ratio = with_loc * normalizer
        availability.append(avail_ratio)
    return sum(availability)

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

def pretty_print_config_name(config):
    name = config.lstrip('config')
    name = name.replace('-', ' -').lstrip(' ')
    name = re.sub(' -g', '', name)
    name = re.sub(' -Xclang', '', name)
    name = re.sub('-extend -lifetimes', '-extend', name)
    return name

if __name__ == '__main__':
    # Missing data:
    # stepanov_v1p2: {u'output': u"\n/Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/tools/timeit --limit-core 0 --limit-cpu 7200 --timeout 7200 --limit-file-size 104857600 --limit-rss-size 838860800 --append-exitstatus --redirect-output /Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/SingleSource/Benchmarks/Misc-C++/Output/stepanov_v1p2.test.out --redirect-input /dev/null --summary /Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/SingleSource/Benchmarks/Misc-C++/Output/stepanov_v1p2.test.time /Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/SingleSource/Benchmarks/Misc-C++/stepanov_v1p2\n/Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/tools/fpcmp -a 0.01 /Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/SingleSource/Benchmarks/Misc-C++/Output/stepanov_v1p2.test.out /Users/vsk/llvm-test-suite/SingleSource/Benchmarks/Misc-C++/stepanov_v1p2.reference_output\n\n/Users/vsk/src/builds/llvm.org-extend-lifetimes-R/bench/config-O1-flto-g/test-2018-03-20_04-03-09/tools/fpcmp: FP Comparison failed, not a numeric difference between 't' and '\n'\n", u'code': u'FAIL', u'name': u'test-suite :: SingleSource/Benchmarks/Misc-C++/stepanov_v1p2.test', u'elapsed': 6.98985481262207}

    ### Chart generation ###

    opt_levels = ['O0', 'O1', 'Os', 'O2']
    base_configs = []
    for opt_lvl in opt_levels:
        base_configs.append('config-' + opt_lvl + '-g')
        if opt_lvl in ('O0', 'O1'):
            continue

        base_configs.append('config-' + opt_lvl + '-flto-g')
    base_data = [read_lit_json(config) for config in base_configs]

    base_dwarf_configs = []
    for config in base_configs:
        if 'flto' in config:
            continue
        base_dwarf_configs.append(config)
    base_dwarf_data = [read_dwarf_json(config) for config in base_dwarf_configs]


    # -O0 performance comparison
    print "Configuration, Binary Size (bytes), Execution Time (seconds)"
    for config, data in zip(base_configs, base_data):
        name = pretty_print_config_name(config)
        bsize = get_mean_binary_size(data)
        exec_time = get_mean_exec_time(data)
        print ', '.join([name, '{:.2f}'.format(bsize), '{:.2f}'.format(exec_time)])

    print

    # Scope Coverage comparison
    print "Configuration, Scope Coverage (%), Scope Coverage (%) (-extend=this), " \
            "Scope Coverage (%) (-extend=arguments), Scope Coverage (%) (-extend=all)"
    for config, data in zip(base_dwarf_configs, base_dwarf_data):
        name = pretty_print_config_name(config)
        cov = get_mean_scope_coverage(data)
        if 'O0' in config:
            print ', '.join([name, '{:.2%}'.format(cov), '0', '0', '0'])
            continue

        ext_this_config = re.sub('-g', '-Xclang-extend-lifetimes=this-g', config)
        ext_args_config = re.sub('-g', '-Xclang-extend-lifetimes=arguments-g', config)
        ext_all_config = re.sub('-g', '-Xclang-extend-lifetimes=all-g', config)
        ext_this_cov = get_mean_scope_coverage(read_dwarf_json(ext_this_config))
        ext_args_cov = get_mean_scope_coverage(read_dwarf_json(ext_args_config))
        ext_all_cov = get_mean_scope_coverage(read_dwarf_json(ext_all_config))

        print ', '.join([name, '{:.2%}'.format(cov), '{:.2%}'.format(ext_this_cov),
                '{:.2%}'.format(ext_args_cov), '{:.2%}'.format(ext_all_cov)])

    print

    # Variable availability comparison
    print "Configuration, Variable Availability (%), Variable Availability (%) (-extend=this), " \
            "Variable Availability (%) (-extend=arguments), Variable Availability (%) (-extend=all)"

    O0_var_avail = get_var_availability(base_dwarf_data[0])
    for config, data in zip(base_dwarf_configs, base_dwarf_data):
        name = pretty_print_config_name(config)
        if 'O0' in config:
            print ', '.join([name, '1', '0', '0', '0'])
            continue

        avail = get_var_availability(data) / O0_var_avail
        ext_this_config = re.sub('-g', '-Xclang-extend-lifetimes=this-g', config)
        ext_args_config = re.sub('-g', '-Xclang-extend-lifetimes=arguments-g', config)
        ext_all_config = re.sub('-g', '-Xclang-extend-lifetimes=all-g', config)
        ext_this = get_var_availability(read_dwarf_json(ext_this_config)) / O0_var_avail
        ext_args = get_var_availability(read_dwarf_json(ext_args_config)) / O0_var_avail
        ext_all = get_var_availability(read_dwarf_json(ext_all_config)) / O0_var_avail

        print ', '.join([name, '{:.2%}'.format(avail), '{:.2%}'.format(ext_this),
                '{:.2%}'.format(ext_args), '{:.2%}'.format(ext_all)])

    print

    # Size comparison for -extend=...

    print "Configuration, Binary Size (bytes), Binary Size (bytes) (-extend=this), Binary Size (bytes) (-extend=arguments), Binary Size (bytes) (-extend=all)"
    for config, data in zip(base_configs, base_data):
        name = pretty_print_config_name(config)
        bsize = get_mean_binary_size(data)
        if 'O0' in config:
            print ', '.join([name, '{:.2f}'.format(bsize), '0', '0', '0'])
            continue

        if 'flto' in config:
            ext_this_config = re.sub('-flto-g', '-Xclang-extend-lifetimes=this-flto-g', config)
            ext_args_config = re.sub('-flto-g', '-Xclang-extend-lifetimes=arguments-flto-g', config)
            ext_all_config = re.sub('-flto-g', '-Xclang-extend-lifetimes=all-flto-g', config)
        else:
            ext_this_config = re.sub('-g', '-Xclang-extend-lifetimes=this-g', config)
            ext_args_config = re.sub('-g', '-Xclang-extend-lifetimes=arguments-g', config)
            ext_all_config = re.sub('-g', '-Xclang-extend-lifetimes=all-g', config)
        this_bsize = get_mean_binary_size(read_lit_json(ext_this_config))
        args_bsize = get_mean_binary_size(read_lit_json(ext_args_config))
        all_bsize = get_mean_binary_size(read_lit_json(ext_all_config))
        print ', '.join([name, '{:.2f}'.format(bsize), '{:.2f}'.format(this_bsize),
           '{:.2f}'.format(args_bsize), '{:.2f}'.format(all_bsize) ])

    print

    # Performance comparison for -extend=...

    print "Configuration, Execution Time (seconds), Execution Time (seconds) (-extend=this), Execution Time (seconds) (-extend=arguments), Execution Time (seconds) (-extend=all)"
    for config, data in zip(base_configs, base_data):
        name = pretty_print_config_name(config)
        exec_time = get_mean_exec_time(data)
        if 'O0' in config:
            print ', '.join([name, '{:.2f}'.format(exec_time), '0', '0', '0'])
            continue

        if 'flto' in config:
            ext_this_config = re.sub('-flto-g', '-Xclang-extend-lifetimes=this-flto-g', config)
            ext_args_config = re.sub('-flto-g', '-Xclang-extend-lifetimes=arguments-flto-g', config)
            ext_all_config = re.sub('-flto-g', '-Xclang-extend-lifetimes=all-flto-g', config)
        else:
            ext_this_config = re.sub('-g', '-Xclang-extend-lifetimes=this-g', config)
            ext_args_config = re.sub('-g', '-Xclang-extend-lifetimes=arguments-g', config)
            ext_all_config = re.sub('-g', '-Xclang-extend-lifetimes=all-g', config)
        this_exec_time = get_mean_exec_time(read_lit_json(ext_this_config))
        args_exec_time = get_mean_exec_time(read_lit_json(ext_args_config))
        all_exec_time =  get_mean_exec_time(read_lit_json(ext_all_config))
        print ', '.join([name, '{:.2f}'.format(exec_time), '{:.2f}'.format(this_exec_time),
           '{:.2f}'.format(args_exec_time), '{:.2f}'.format(all_exec_time) ])


    # exit(0)

    ###

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

    print "-O0 var availability:", get_var_availability(read_dwarf_json('config-O0-g'))
    print "-O1 var availability:", get_var_availability(read_dwarf_json('config-O1-g'))
    print "-O2 var availability:", get_var_availability(read_dwarf_json('config-O2-g'))
