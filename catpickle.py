#!/usr/bin/env python

import pickle, sys, pprint

with open(sys.argv[1], 'rb') as f:
    pprint.pprint(pickle.load(f))
