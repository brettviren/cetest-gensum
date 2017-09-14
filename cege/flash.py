#!/usr/bin/env python
'''Info about flash test results.

These differ from ASIC related tests in that there are no identifiers.
Parts are prescreened anonymously, failures and
successes are kept in two separate sets.'''


import os
import sys
import json
from glob import glob

from cege import defaults, io, raw

databasedir = defaults.databasedir
seed_glob = '*/dsk/?/oper/FlashTesting/*/*/QuadEpcsTester/params.json'

def seed_paths():
    'Return collection of seed paths'
    return glob(os.path.join(databasedir, seed_glob))

def summarize(seed_path):
    'Return a summary of a test'
    seed = io.load_path(seed_path)
    ret = raw.common_params('flash', **seed)
    ret['ident'] = ret['timestamp'] # no other unique ID availble

    parent = os.path.dirname(seed_path)
    ret['datadir'] = parent

    resfile = os.path.join(parent,'QuadEpcsTester.json')
    if os.path.exists(resfile):

        # this is not even close to valid JSON so have to hack yet another workaround
        slurp = open(resfile).read()
        fix = "[" + slurp.replace("}{","},{") + "]"
        res = json.loads(fix)
        pass_fail = list(res[0].values())[0]
        passed = 0
        for one in pass_fail:
            if one:
                passed += 1

        ret['passed'] = passed
        ret['failed'] = len(pass_fail)-passed
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
    return 'flash_{ident}'.format(**summary)

def instdir(summary):
    'Return relative installation directory for one summary'
    return "flash/{timestamp}".format(**summary)

def indexer(summary_fps):
    'Return index data structure from a sequence of file like things'
    ret = dict()
    for fp in summary_fps:
        summary = io.load(fp)
        ret[summary['ident']] = summary
    return ret

from . import rates
def testing_rates(cfg, index):
    return rates.flash(cfg, dict(index=index.values()));
