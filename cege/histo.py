#!/usr/bin/env python

from collections import defaultdict, Counter
import dateutil.parser

def byday(data):
    'Collate data into per day counts, return dictionary keyed by femb_config'
    ret = defaultdict(Counter)
    for one in data['index']:
        cfgname = one['femb_config']
        dt = dateutil.parser.parse(one['timestamp']) # eg "20170613T164258"
        date = dt.date()
        ret[cfgname][date] += 1
    return ret

def byday_byhost(data, cold):
    'Collate data into per day counts, return dictionary keyed by femb_config'
    ret = defaultdict(Counter)
    for one in data['index']:
        cfgname = one['femb_config']
        have_cold = "cold" in cfgname
        if cold != have_cold:
            continue
        hostname = one['hostname']
        dt = dateutil.parser.parse(one['timestamp']) # eg "20170613T164258"
        date = dt.date()
        ret[hostname][date] += 1
    return ret

def byday_byboard(data, cold):
    'Collate data by board version'
    ret = defaultdict(Counter)
    for one in data['index']:
        cfgname = one['femb_config']
        have_cold = "cold" in cfgname
        if cold != have_cold:
            continue

        board_id = 'board'+one['board_id']
        dt = dateutil.parser.parse(one['timestamp']) # eg "20170613T164258"
        date = dt.date()
        ret[board_id][date] += 1
    return ret

def byday_count(data, key='passed'):
    'Collate data into number of counts per day, return dictionary keyed by femb_config'
    ret = defaultdict(Counter)
    for one in data['index']:
        cfgname = one['femb_config']
        dt = dateutil.parser.parse(one['timestamp']) # eg "20170613T164258"
        date = dt.date()
        ret[cfgname][date] += one.get(key,0)
    return ret

def byday_if(data, key='passed'):
    'Collate data into number of true per, return dictionary keyed by femb_config'
    ret = defaultdict(Counter)
    for one in data['index']:
        if not one.get(key, False):
            continue
        cfgname = one['femb_config']
        dt = dateutil.parser.parse(one['timestamp']) # eg "20170613T164258"
        date = dt.date()
        ret[cfgname][date] += 1
    return ret
    

def to_series(hist):
    'Convert histograms to series data structure'
    ret = list()
    for cfgname, one in hist.items():
        data = [x for x in one.items()]
        data.sort()
        ret.append(dict(name=cfgname, data=data))
    return ret

def _board_sorter(x):
    try:
        v = int(x)
    except ValueError:
        return 99999
    return v


def divine_board_version(board_id):
    '''Shift workers are very creative in mispelling board IDs.  They are
    supposed to be either just an integer or two integers separated by
    "v".

    Some examples of broken board IDs are:

    d10v3
    vv7

    This function does not try to guess the intention of the shifter.

    It returns a pair of integers (bid,ver).  A negative bid means the
    expected spelling was violated.  Version is zero unless
    successfully determined.

    '''
    bid = -1
    ver = 0

    if not board_id:
        return bid,ver

    if board_id[0] not in "0123456789":
        return bid,ver

    # try as XX[vY]
    parts = board_id.lower().split("v")
    if 1 == len(parts):
        try:
            bid = int(parts[0])
        except ValueError:
            pass
        else:
            return bid,ver

    if 2 == len(parts):
        try:
            bid = int(parts[0])
            ver = int(parts[1])
        except ValueError:
            pass
        else:
            return bid,ver
    return bid,ver



def to_stack(data, cold=True, clickable = True, completed=True):
    assert(data)

    boards = set()
    versions = set()
    counts = Counter()

    for one in data['index']:
        have_cold = "cold" in one['femb_config']
        if cold != have_cold:
            continue
        have_completed = one["completed"]
        if have_completed != completed:
            continue

        board_id = one['board_id'].lower()

        bid,iver = divine_board_version(board_id)

        counts[(bid,iver)] += 1
        boards.add(bid)
        versions.add(iver)

    if not boards:
        return dict(categories=list(), series=list())

    boards = list(boards)
    boards.sort()
    sboards = list()
    for bid in boards:
        if bid<0: sboards.append("bogus")
        else: sboards.append(str(bid))


    versions = list(versions)
    versions.sort()
    versions.reverse()          # grow stack up starting from v0
    
    series = list()
    for iver in versions:
        sver = "v%d" % iver
        fver = ""               # preserve original dumbness
        if iver > 0:
            fver = "v%d" % iver

        point_data = list()
        for bid,sbid in zip(boards,sboards):
            usages = counts[(bid,iver)]
            d = dict(y=usages, url=sbid+fver)
            point_data.append(d)
        series.append(dict(name=sver, data=point_data))

    return dict(categories=sboards, series=series)

