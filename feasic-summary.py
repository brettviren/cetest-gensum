#!/usr/bin/env python
'''Feasic tests have two problems w.r.t. simply making a summary.

1) they have no summary JSON
2) their JSON is not JSON

This script produces the missing summary 
'''

# /dsk/1/data/sync-json/hothdaq2/dsk/1/oper/feasic/quadFeAsic/20170804T224053/check_setup/params.json

import os
import sys
import json
from glob import glob
from collections import Counter

def load_maybe_broken_json(filename):
    '''Load result file, possibly as fscked up JSON.
    '''
    dat = open(filename).read()
    for n in range(3):
        dat = json.loads(dat)
        if type(dat) == dict:
            return dat
    raise ValueError("Could not load result file %s" % resultfile)

def slurp_from_seed(check_setup_params_json):
    '''Surp a result starting with the check_setup/params.json file.
    Return big dict keyed by data subdir name.

    '''
    seed = os.path.realpath(check_setup_params_json)
    resdir = os.path.dirname(os.path.dirname(seed))

    ret = dict()

    for parfile in glob(os.path.join(resdir, "*/params.json")):
        pardat = json.load(open(parfile))
        dsd = pardat['datasubdir']
        resdat = dict()
        for resfile in glob(parfile.replace("params.json","*-results.json")):
            resdat = load_maybe_broken_json(resfile)
            break;              # should only be one....
        ret[dsd] = dict(params=pardat, results=resdat)

    return dict(feasic=ret)

if '__main__' == __name__:
    dat = slurp_from_seed(sys.argv[1])
    out = sys.argv[2]
    open(out,'w').write(json.dumps(dat, indent=4))
    
