#!/usr/bin/env python
'''This script produces a single JSON file from all those in one sample directory.

Seed it with the fembTest_powercycle_test/params.json file
'''

# /dsk/1/data/sync-json/hothdaq1/dsk/1/oper/femb/wib_sbnd_v109_femb_protodune_v308/20170803T171304/fembTest_powercycle_test/params.json

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

def fix_result(res):
    # $@#*!
    for maybe_garbage in ["adc_asics","fe_asics"]:
        try:
            val = res[maybe_garbage];
        except KeyError:
            return res

        if ',' in val[0][0]:
            val[0] = map(str, val[0][0].split(','))
    return res

def summarize_result(res):
    try:
        results = res["results"]
    except KeyError:
        return res
    asic_fail = 0
    chan_fail = 0
    for one in results:
        fail = one["fail"]=="1"
        if not fail:
            continue
        if one.has_key("asic"):
            asic_fail += 1
        if one.has_key("ch"):
            chan_fail += 1
    results_summary = dict(asic_fail = asic_fail, chan_fail=chan_fail)
    res["results_summary"] = results_summary
    return res

def slurp_from_seed(check_setup_params_json):
    '''Surp a result starting with the check_setup/params.json file.
    Return big dict keyed by data subdir name.

    '''
    seed = os.path.realpath(check_setup_params_json)
    resdir = os.path.dirname(os.path.dirname(seed))

    ret = dict()

    for parfile in glob(os.path.join(resdir, "*/params.json")):
        pardat = fix_result(load_maybe_broken_json(parfile))
        dsd = pardat['datasubdir']
        resdat = list()
        for resfile in glob(parfile.replace("params.json","*-results.json")):
            one = summarize_result(fix_result(load_maybe_broken_json(resfile)))
            resdat.append(one)
        sd = os.path.dirname(parfile)
        pngs = ['_'.join(p.split("/")[-2:]) for p in glob(os.path.join(sd, "*.png"))]
        pdfs = ['_'.join(p.split("/")[-2:]) for p in glob(os.path.join(sd, "*.pdf"))]
        #sys.stderr.write("%s: %s\n" % (dsd,len(resdat)))
        ret[dsd] = dict(params=pardat, results=resdat, pngs=pngs, pdfs=pdfs)

    return dict(femb=ret)

if '__main__' == __name__:
    dat = slurp_from_seed(sys.argv[1])
    sys.stdout.write(json.dumps(dat, indent=4))
    
