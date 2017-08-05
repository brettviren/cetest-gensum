#!/usr/bin/env python
'''Feasic tests have two problems w.r.t. simply making a summary.

1) they have no summary JSON
2) their JSON is not JSON

This script produces the missing summary 
'''

# /dsk/1/data/sync-json/hothdaq2/dsk/1/oper/feasic/quadFeAsic/20170804T224053

import os
import sys
import json
from glob import glob
from collections import Counter

def loads_result(resultfile):
    '''Load result file, possibly as fscked up JSON.
    '''
    dat = open(resultfile).read()
    for n in range(3):
        dat = json.loads(dat)
        if type(dat) == dict:
            return dat
    raise ValueError("Could not load result file %s" % resultfile)

def results_summary(par, res):
    '''
    Return dictionary of ASIC SN -> pass
    '''
    asic_ok = dict()
    for r in res['results']:
        try:
            asicn = int(r['asic'])
        except KeyError:
            continue
        sn = par["asic%did"%asicn]
        fail = int(r["fail"])
        asic_ok[sn] = not fail
    return asic_ok
        
def slurp_directory(dirname):
    '''Surp in a directory looking for result files.  Return dict mapping
    sub dir to a pair of (parameters, results).
    '''
    dirname = os.path.realpath(dirname)

    ret = dict()

    # use the check_setup params to snarf some general info
    cspar = json.loads(open(os.path.join(dirname, "check_setup", "params.json")).read())
    ret["datadir"] = os.path.dirname(cspar["datadir"])
    ret["femb_config"] = cspar["femb_config"]
    ret["femb_version"] = cspar["femb_python_location"][29:].split("/")[0]
    ret["hostname"] = cspar['hostname']
    ret["timestmp"] = cspar['session_start_time']

    asic_pass = Counter();
    asic_fail = Counter()
    # now go after per test summaries
    for resfile in glob("%s/*/*-results.json" % dirname):
        resdir = os.path.dirname(resfile)
        subdir = os.path.basename(resdir)

        resdat = loads_result(resfile)
        pardat = json.loads(open(os.path.join(resdir,"params.json")).read())
        
        pf = results_summary(pardat, resdat)
        for aid,res in pf.items():
            if res:
                asic_pass[aid] += 1
            else:
                asic_fail[aid] += 1

        thisres = dict (
            png = os.path.basename(resfile).replace("-results.json","summaryPlot.png"),
            result = pf,
            subdir = subdir,
            test_type = resdat["type"],
            config_base = resdat["config_base"],
            config_gain = resdat['config_gain'],
            config_shape = resdat['config_shape'] 
        )
        ret[subdir] = thisres
    ret["passing"] = asic_pass
    ret["failing"] = asic_fail

    return ret

if '__main__' == __name__:
    dat = slurp_directory(sys.argv[1])
    sys.stdout.write(json.dumps(dat))
    
