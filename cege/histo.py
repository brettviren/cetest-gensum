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

        bid=None
        iver=0
        try:
            bid = int(board_id)
        except ValueError:
            if 'v' in board_id:          # 10v2
                bid,iver = map(int, board_id.split('v'))
            else:               # probably "bogus"
                bid = -1

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

