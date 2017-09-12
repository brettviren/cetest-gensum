#!/usr/bin/env python
'''
Regularize the chaos of the various test results.
'''
import os
import sys
from glob import glob
from . import io

# globs that find all seeds of a given category relative to some root directory.
# Typically this locates a 'params.json' file which indicates that a
# test run was at least initiated.  First "*" is femb_config second is
# timestamp.
seed_globs = dict(

    adcasic = '*/dsk/?/oper/adcasic/*/*/params.json',
    feasic =  '*/dsk/?/oper/feasic/*/*/check_setup/params.json',
    femb =  '*/dsk/?/oper/femb/*/*/fembTest_powercycle_test/params.json',
    osc =  '*/dsk/?/oper/osc/osc/*/OscillatorTestingThermalCycle1/params.json',
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
    one = str(one).strip().lower()
    if not one or one[0] in '_*-':
        return 'bogus'
    return one
def fix_asic_ids(many):
    return [fix_asic_id[one] for one in many]

def fix_board_id(one):
    one = one.strip().upper()
    if not one or one[0] in '_*-':
        return 'BOGUS'
    return one

def fix_list(lst, fix_entry):
    if not lst:
        return lst
    if ' ' in lst[0]:
        lst = lst[0].split()
    if ',' in lst[0]:
        lst = lst[0].split(',')
    return [fix_entry(one) for one in lst]

def common_params(category, **params):
    '''
    Return a common subset data likely found in larger params.json structure.
    '''
    return dict(category = category,
                femb_config = get_femb_config(**params),
                timestamp = get_timestamp(**params),
                version = get_version(**params),
                hostname = params.get('hostname',"hothless"))

def summarize_params(cat, **params):
    '''
    Return a summary of the params from a params.json taking in to account category-specific values.
    '''

    # first common stuff
    summary = dict(category = cat,
                   femb_config = get_femb_config(**params),
                   timestamp = get_timestamp(**params),
                   version = get_version(**params),
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
        for key in 'box_ids fm_ids am_ids'.split():
            ident = params[key][0] #  just first entry
            if ident:
                summary[key] = ident
            else:
                summary[key] = "no_" + key
                continue
            bid.append(ident)
        if not bid:
            summary['serial'] = 'bogus'
        else:
            summary['serial'] = '-'.join(bid)

    return summary

def summarize_adcasic(seed_path):
    results = dict()

    full_params = io.load(open(seed_path, encoding='utf-8'))
    params = summarize_params('adcasic', **full_params)

    parent = os.path.dirname(seed_path)
    results['pngs'] = [os.path.basename(p) for p in glob(os.path.join(parent,'*.png'))]
    results['pdfs'] = [os.path.basename(p) for p in glob(os.path.join(parent,'*.pdf'))]
    res = glob(os.path.join(seed_path.replace("params.json",'adcTest_*.json')))
    if res:
        res = io.load(open(res[0], 'r'))
        results['passed'] = res['testResults']['pass']
    else:
        sys.stderr.write("No test results for ADC ASIC {adc_id} at {timestamp}\n".format(**params))
        results['passed'] = False

    return dict(adcasic=dict(results=results, params=params))

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


def summarize_femb(seed_path):
    full_params = io.load(open(seed_path,'r'))
    params = summarize_params('femb', **full_params)

    results = dict()
    parent = os.path.dirname(os.path.dirname(seed_path))
    for param_fname in glob(os.path.join(parent, "*/params.json")):
        datasubdir = os.path.basename(os.path.dirname(param_fname))

        resdat = dict()
        resfile = glob(param_fname.replace("params.json","*-results.json"))
        if resfile:
            one = io.load(open(resfile[0],'r'))
            resdat = summarize_femb_result(one)

        sd = os.path.dirname(param_fname)
        pngs = ['_'.join(p.split("/")[-2:]) for p in glob(os.path.join(sd, "*.png"))]
        pdfs = ['_'.join(p.split("/")[-2:]) for p in glob(os.path.join(sd, "*.pdf"))]

        results[datasubdir] = dict(pngs=pngs, pdfs=pdfs, **resdat)

    return dict(femb=dict(results=results, params=params))



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


def summarize_feasic(seed_path):
    full_params = io.load(open(seed_path,'r'))
    params = summarize_params('feasic', **full_params)

    results = dict()
    parent = os.path.dirname(os.path.dirname(seed_path))
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
        pngs = ['_'.join(p.split("/")[-2:]) for p in glob(os.path.join(sd, "*.png"))]
        pdfs = ['_'.join(p.split("/")[-2:]) for p in glob(os.path.join(sd, "*.pdf"))]

        results[datasubdir] = dict(pngs=pngs, pdfs=pdfs, **resdat)

    return dict(feasic=dict(results=results, params=params))


def summarize(seed_path, cat=None):
    '''
    Return a summary of test given seed file
    '''

    if not cat:
        cat = guess_category(seed_path)
    meth = eval("summarize_" + cat)
    return meth(seed_path)

            
