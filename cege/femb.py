#!/usr/bin/env python
'''
The FEMB ASIC taxon
'''

import os
import sys
from glob import glob

from cege import defaults, io, raw, smtdb

#smt_labels = smtdb.slurp_fe_labels()


databasedir = defaults.databasedir
seed_glob = '*/dsk/?/oper/femb/*/*/fembTest_powercycle_test/params.json'

def seed_paths():
    'Return collection of seed paths'
    return glob(os.path.join(databasedir, seed_glob))

def summarize_femb_result(res):
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
    for one in results:         # count failures
        if one["fail"] != "1":
            continue
        if "asic" in one and one["fail"] == "1":
            asic_fail += 1
        if "ch" in one and one["fail"] == "1":
            chan_fail += 1
    ret.update(asic_fail = asic_fail, chan_fail=chan_fail)
    return ret

def summarize(seed_path):
    '''Return summary of data found at seed path as dictionary for
    use by summary.html.j2 and as one element in the index'''

    seed = io.load_path(seed_path)
    ret = raw.common_params('feasic', **seed)


    bid = list()
    ret['fe_ids'] = raw.fix_list(seed['fe_asics'][0], raw.fix_asic_id)
    ret['adc_ids'] = raw.fix_list(seed['adc_asics'][0], raw.fix_asic_id)
    for key in 'box_ids fm_ids am_ids'.split():
        ident = seed[key][0] #  just first entry
        if ident:
            ret[key] = ident
        else:
            ret[key] = "no_" + key
            continue
        bid.append(ident)
    if not bid:
        ret['serial'] = 'bogus'
    else:
        ret['serial'] = '-'.join(bid)
    
    ret['ident'] = ret['serial'] + '-' + ret['timestamp']


    #ret['label'] = smt_labels.get(ts, None)

    results = dict()
    parent = os.path.dirname(os.path.dirname(seed_path))
    ret['datadir'] = parent
    png_sources = list()
    pdf_sources = list()
    pngs = list()
    pdfs = list()
    for param_fname in glob(os.path.join(parent, "*/params.json")):
        datasubdir = os.path.basename(os.path.dirname(param_fname))

        resdat = dict()
        resfile = glob(param_fname.replace("params.json","*-results.json"))
        if resfile:
            one = io.load(open(resfile[0],'r'))
            resdat = summarize_femb_result(one)

        sd = os.path.dirname(param_fname)

        # full paths
        mypng = glob(os.path.join(sd, "*.png"))
        png_sources += mypng
        mypdf = glob(os.path.join(sd, "*.pdf"))
        pdf_sources += mypdf


        # installed paths.  Need to make unique by using subdir
        resdat['pngs'] = ['_'.join(p.split('/')[-2:]) for p in mypng]
        pngs += resdat['pngs']
        resdat['pdfs'] = ['_'.join(p.split('/')[-2:]) for p in mypdf]
        pdfs += resdat['pdfs']

        results[datasubdir] = resdat

    ret['pngs'] = pngs
    ret['pdfs'] = pdfs
    ret['png_sources'] = png_sources
    ret['pdf_sources'] = pdf_sources

    ret['results'] = results
    return ret


def unique(summary):
    'Return short string which should be unique and usable as file base name'
    return 'feasic-{ident}'.format(**summary)

def indexer(summary_fps):
    'Return index data structure from a sequence of file like things'
    ret = dict()
    for fp in summary_fps:
        summary = io.load(fp)
        ret[summary['ident']] = summary
    return ret
