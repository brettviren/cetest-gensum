#!/usr/bin/env python
'''
Regularize the chaos of the various test results.
'''
import os
from glob import glob
from . import io

datadir='/dsk/1/data/sync-json'

# globs that find all seeds of a given category.  Typically this
# locates a 'params.json' file which indicates that a test run was at
# least initiated.
# Frist "*" is femb_config second is timestamp.
seed_globs = dict(

    adcasic = os.path.join(datadir, 'hothdaq?/dsk/?/oper/adcasic/*/*/params.json'),
    feasic = os.path.join(datadir, 'hothdaq?/dsk/?/oper/feasic/*/*/check_setup/params.json'),
    femb = os.path.join(datadir, 'hothdaq?/dsk/?/oper/femb/*/*/fembTest_powercycle_test/params.json'),
    osc = os.path.join(datadir, 'hothdaq?/dsk/?/oper/osc/osc/*/OscillatorTestingThermalCycle1/params.json'),
)


def fix_board_id(thing):
    'Try to unstupify board IDs'
    bogus = "bogus"
    thing = str(thing).strip().lower()
    if not thing:
        return bogus
    if thing[0] in "*_-":
        return bogus
    return thing

def fix_asic_id(thing):
    'Try to unstupify ASIC IDs'
    bogus = "BOGUS"
    thing = str(thing).strip().upper()
    if not thing:
        return bogus
    if thing[0] in "*_-":
        return bogus
    return thing


def guess_category(params_path):
    '''
    Guess the category
    '''
    chunks = params_path.split('/')
    for ind in range(1, len(chunks)):
        if chunks[ind-1] == 'oper':
            return chunks[ind]
    return 

def get_version(**params):
    fpl = params.get('femb_python_location',None)
    if fpl:
        return fpl.split('/')[-2][12:]
    return ""

def get_timestamp(**params):
    for maybe in ['session_start_time', 'timestamp']:
        ts = params.get(maybe, None)
        if ts: return ts
    return ""

def get_femb_config(**params):
    for maybe in ['femb_config', 'femb_config_name']:
        fc = params.get(maybe, None)
        if fc: return fc
    return ""

def fix_asic_id(one):
    one = one.strip().lower()
    if not one or one[0] in '_*-':
        return 'bogus'
    return one
def fix_board_id(one):
    one = one.strip().upper()
    if not one or one[0] in '_*-':
        return 'BOGUS'
    return one

def fix_list(lst, fix_entry):
    if ' ' in lst[0]:
        lst = lst[0].split()
    if ',' in lst[0]:
        lst = lst[0].split(',')
    return [fix_entry(one) for one in lst]

def summarize_params(cat, **params):
    '''
    Return a summary of the params from a params.json taking in to account category-specific values.
    '''

    # first common stuff
    summary = dict(category = cat,
                   femb_config = get_femb_config(**params),
                   timestamp = get_timestamp(**params),
                   version = get_version(**params),
                   datadir = params['datadir'],
                   hostname = params.get('hostname',"hothless"))

    # deal with category specific stuff.

    if cat == 'adcasic':
        summary['adc_id'] = fix_asic_id(str(params['serials'][0]))
        summary['adc_testboard_id'] = fix_board_id(params['board_id'])

    if cat == 'feasic':
        summary['fe_ids'] = [fix_asic_id(params['asic%did'%n]) for n in range(4)]
        summary['fe_testboard_id'] = fix_board_id(params['boardid'])
        summary['datasubdir'] = params['datasubdir']

    if cat == 'femb':
        bid = list()
        summary['fe_ids'] = fix_list(params['fe_asics'][0], fix_asic_id)
        summary['adc_ids'] = fix_list(params['adc_asics'][0], fix_asic_id)
        summary['datasubdir'] = params['datasubdir']
        for key in 'box_ids fm_ids am_ids'.split():
            ident = params[key][0] #  just first entry
            summary[key] = ident
            bid.append(ident)
        summary['serial'] = '-'.join(bid)

    return summary

def summarize_adcasic(seed_path):
    results = dict()

    full_params = io.load(open(seed_path,'r'))
    params = summarize_params(cat, **full_params)

    parent = os.path.dirname(seed_path)
    results['pngs'] = [os.path.basename(p) for p in glob(os.path.join(parent,'*.png'))]
    results['pdfs'] = [os.path.basename(p) for p in glob(os.path.join(parent,'*.pdf'))]
    res = glob(os.path.join(datadir,'adcTest_*.json'))
    if res:
        res = io.load(open(res[0], 'r'))
        results['passed'] = res['testResults']['pass']
    else:
        results['passed'] = False

    return dict(adcasic=results)

def summarize_feasic(seed_path):

    parent = os.path.dirname(os.path.dirname(seed_path))

    # fixme: this is a big slurp, could be reduced.
    for param_fname in glob(os.path.join(parent,'*/params.json')):
        full_params = io.load(open(param_fname,'r'))
        params = summarize_params('feasic', **full_params)
        results_fname = glob(param_fname.replace("params.json","*-results.json"))
        if results_fname:
            resdat = io.load(open(results_fname[0], 'r'))
        else:
            resdat = None
        dsd = params['datasubdir']
        results[dsd] = dict(results=resdat, params=params)
    return dict(feasic=results)

def summarize_femb_result(res):
    try:
        results = res["results"]
    except KeyError:
        return res
    asic_fail = 0
    chan_fail = 0
    for one in results:         # count failures
        if one["fail"] != "1":
            continue
        if one.has_key("asic"):
            asic_fail += 1
        if one.has_key("ch"):
            chan_fail += 1
    results_summary = dict(asic_fail = asic_fail, chan_fail=chan_fail)
    res["results_summary"] = results_summary
    return res


def summarize_femb(seed_path):

    parent = os.path.dirname(os.path.dirname(seed_path))

    results = dict()

    for param_fname in glob(os.path.join(parent, "*/params.json")):
        full_params = io.load(open(param_fname,'r'))
        params = summarize_params('femb', **full_params)
        resdat = list()
        for resfile in glob(param_fname.replace("params.json","*-results.json")):
            one = io.load(open(resfile,'r'))
            one = summarize_femb_result(one)
            resdat.append(one)
        sd = os.path.dirname(param_fname)
        pngs = ['_'.join(p.split("/")[-2:]) for p in glob(os.path.join(sd, "*.png"))]
        pdfs = ['_'.join(p.split("/")[-2:]) for p in glob(os.path.join(sd, "*.pdf"))]
        dsd = params['datasubdir']
        results[dsd] = dict(params=params, results=resdat, pngs=pngs, pdfs=pdfs)

    return dict(femb=results)


def summarize(seed_path, cat=None):
    '''
    Return a summary of test given seed file
    '''

    if not cat:
        cat = guess_category(seed_path)
    meth = eval("summarize_" + cat)
    return meth(seed_path)

            
