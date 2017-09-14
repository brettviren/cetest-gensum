#!/usr/bin/env python
'''
The FE ASIC taxon
'''

import os
import sys
from glob import glob

from cege import defaults, io, raw, smtdb

smt_labels = smtdb.slurp_fe_labels()


databasedir = defaults.databasedir
seed_glob = '*/dsk/?/oper/feasic/*/*/check_setup/params.json'

def seed_paths():
    'Return collection of seed paths'
    return glob(os.path.join(databasedir, seed_glob))

def summarize_feasic_result(res):
    ret = dict()

    for var in "gain shape base".split():
        maybe = "config_"+var
        if maybe in res:
            ret[var] = res[maybe]

    # count failures
    try:
        results = res["results"]
    except KeyError:
        return dict()
    asic_fail = 0
    chan_fail = 0
    asic_passfail = list()
    for one in results:         # count failures
        if "asic" in one:
            if one["fail"] == "1":
                asic_fail += 1
                asic_passfail.append("failed")
            else:
                asic_passfail.append("passed")
        if "ch" in one and one["fail"] == "1":
            chan_fail += 1
    ret.update(asic_fail = asic_fail, chan_fail=chan_fail, asic_passfail=asic_passfail)
    return ret

def summarize(seed_path):
    '''Return summary of data found at seed path as dictionary for
    use by summary.html.j2 and as one element in the index'''

    seed = io.load_path(seed_path)
    ret = raw.common_params('feasic', **seed)

    ret['fe_ids'] = [raw.fix_asic_id(seed['asic%did'%n]) for n in range(4)]
    bid = ret['fe_testboard_id'] = raw.fix_board_id(seed['boardid'])
    ret['serial'] = "board%s" % bid
    
    ts = ret['timestamp']
    ident = bid + '-' + ts
    ret['ident'] = ident

    ret['label'] = smt_labels.get(ts, None)

    parent = os.path.dirname(os.path.dirname(seed_path))
    ret['datadir'] = parent

    results = dict()

    png_sources = list()
    pdf_sources = list()

    ret['install'] = list()
    for param_fname in glob(os.path.join(parent, "*/params.json")):
        # shunt a few job specific input parameters
        thisp = io.load(open(param_fname,'r'))
        datasubdir = thisp.get('datasubdir',None)
        if not datasubdir:
            continue            # power, check_setup

        resfile = glob(param_fname.replace("params.json","*-results.json"))
        resdat = dict()
        if resfile:
            one = io.load(open(resfile[0],'r'))
            resdat = summarize_feasic_result(one)

        sd = os.path.dirname(param_fname)

        for ext in ['png', 'pdf']:
            key = ext+'s'
            glb = '*.'+ext
            srcs = glob(os.path.join(sd, glb))
            ret['install'] += srcs
            resdat[key] = [os.path.basename(p) for p in srcs]

        results[datasubdir] = resdat

    ret['results'] = results
    ret['associations'] = dict(feid=ret['fe_ids']) # could add adc ids and fe board
    return ret


def unique(summary):
    'Return short string which should be unique and usable as file base name'
    return 'feasic-{ident}'.format(**summary)

def instdir(summary):
    'Return relative installation directory for one summary'
    return "feasic/{serial}/{timestamp}".format(**summary)

def indexer(summary_fps):
    'Index FE ASIC tests'
    ret = dict()
    for fp in summary_fps:
        summary = io.load(fp)
        ret[summary['ident']] = summary
    return ret


from . import rates
def testing_rates(cfg, index):
    return rates.feasic(cfg, dict(index=index.values()));
