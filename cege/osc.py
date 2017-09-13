#!/usr/bin/env python
'''Info about osc test results.

These differ from ASIC related tests in that there are no identifiers.
Parts are prescreened anonymously, failures and
successes are kept in two separate sets.'''


import os
import sys
from glob import glob

from cege import defaults, io, raw

databasedir = defaults.databasedir
seed_glob = '*/dsk/?/oper/osc/osc/*/OscillatorTestingThermalCycle1/params.json'

def seed_paths():
    'Return collection of seed paths'
    return glob(os.path.join(databasedir, seed_glob))

def summarize(seed_path):
    'Return a summary of a test'
    seed = io.load_path(seed_path)
    ret = raw.common_params('osc', **seed)
    ret['ident'] = ret['timestamp'] # no other unique ID availble

    parent = os.path.dirname(os.path.dirname(seed_path))
    ret['datadir'] = parent

    resfile = os.path.join(parent,'OscillatorTestingSummary/Summary.txt')
    if os.path.exists(resfile):
        res = io.load_path(resfile)

        passed = 0
        for onech in res[1:]:
            if all([s == 'Passed' for s in onech[1:]]):
                passed += 1

        ret['passed'] = passed
        ret['failed'] = len(res[1:])-passed
        ret['completed'] = True
        ret['aborted'] = False
    else:                   # looks like an aborted 
        ret['passed'] = 0
        ret['failed'] = 0
        ret['completed'] = False
        ret['aborted'] = True
        
    return ret

def unique(summary):
    'Return short string which should be unique and usable as file base name'
    return 'osc_{ident}'.format(**summary)

def instdir(summary):
    'Return relative installation directory for one summary'
    return "osc/{timestamp}".format(**summary)

def indexer(summary_fps):
    'Return index data structure from a sequence of file like things'
    ret = dict()
    for fp in summary_fps:
        summary = io.load(fp)
        ret[summary['ident']] = summary
    return ret

from . import rates
def testing_rates(cfg, index):
    return rates.osc(cfg, dict(index=index.values()));
