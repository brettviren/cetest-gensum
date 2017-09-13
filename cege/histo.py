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
        v = int(x[0])
    except ValueError:
        return 9999999999
    return v


def to_stack(data, cold=True, clickable = True):
    assert(data)
    boards = set()
    counts = Counter()
    for one in data['index']:
        bid = one['board_id'].lower()
        have_cold = "cold" in one['femb_config']
        if cold != have_cold:
            continue
        if 'v' not in bid:
            bid += 'v0'
        counts[bid] += 1
        sbid = bid.split('v')[0]
        boards.add(sbid)
    if not counts.values():
        return dict(categories=list(), series=list())
    maxver = max(counts.values())
    boards = list(boards)
    boards.sort()
    nboards = len(boards)

    # must invert the counts.
    matrix = defaultdict(lambda: [0]*nboards)
    for bidver, count in counts.items():
        bid,ver = bidver.split('v')
        bind = boards.index(bid)
        sver = 'v%s'%ver
        matrix[sver][bind] = count

    if clickable:
        series = list()
        for ver, data in matrix.items():
            data_with_url = list()
            for b,y in zip(boards,data):
                if ver != "v0":
                    b += ver
                d = dict(y=y, url=b)
                data_with_url.append(d)
            series.append(dict(name=ver, data=data_with_url))
           
    else:
        series = [dict(name=k, data=v) for k,v in matrix.items()]

    return dict(categories=boards, series=series)

