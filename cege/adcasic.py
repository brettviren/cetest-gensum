#!/usr/bin/env python
'''
The ADC ASIC taxon
'''

import os
import sys
from glob import glob

from cege import defaults, io, raw, smtdb

smt_labels = smtdb.slurp_adc_labels()


databasedir = defaults.databasedir
seed_glob = '*/dsk/?/oper/adcasic/*/*/params.json'

def seed_paths():
    'Return collection of seed paths'
    return glob(os.path.join(databasedir, seed_glob))

def summarize(seed_path):
    '''Return summary of data found at seed path as dictionary for
    use by summary.html.j2 and as one element in the index'''

    seed = io.load_path(seed_path)
    ret = raw.common_params('adcasic', **seed)
    ts = ret['timestamp']
    serial = ret['serial'] = raw.fix_asic_id(seed['serials'][0]) # fixme: just assuming one
    ident = serial + '-' + ts
    ret['ident'] = ident

    ret['label'] = smt_labels.get(ts, None)

    ret['board_id'] = raw.fix_board_id(seed['board_id'])
    assert "V" not in ret['board_id'], ret['board_id'] # should be lower case

    parent = os.path.dirname(seed_path)
    ret['datadir'] = parent

    ret['install'] = list()
    for ext in ['png', 'pdf']:
        key = ext+'s'
        glb = '*.'+ext
        srcs = glob(os.path.join(parent, glb))
        ret['install'] += srcs
        ret[key] = [os.path.basename(p) for p in srcs]

    res = glob(os.path.join(seed_path.replace("params.json",'adcTest_*.json')))
    if res:
        res = io.load_path(res[0])
        ret['passed'] = res['testResults']['pass']
        ret['completed'] = True
    else:
        #sys.stderr.write("No test results for ADC ASIC {}\n".format(seed_path))
        ret['passed'] = False
        ret['completed'] = False

    # record what other things this summary is associated with
    ret['associations'] = dict(adcid=[serial], adcboard=[ret['board_id']])

    return ret

def unique(summary):
    'Return short string which should be unique and usable as file base name'
    return 'adcasic_{serial}_{timestamp}'.format(**summary)

def instdir(summary):
    'Return relative installation directory for one summary'
    return "adcasic/{serial}/{timestamp}".format(**summary)


def indexer(summary_fps):
    'Return index data structure from a sequence of file like things'
    ret = dict()
    for fp in summary_fps:
        summary = io.load(fp)
        ret[summary['ident']] = summary
    return ret

from . import rates
def testing_rates(cfg, index):
    return rates.adcasic(cfg, dict(index=index.values()));
