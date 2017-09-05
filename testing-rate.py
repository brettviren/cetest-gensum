#!/usr/bin/env python

import sys
import json
from collections import defaultdict, Counter
import dateutil.parser

from dateutil.tz import tzutc


def serialize_date(dt):
    # ret = 'Date.UTC(%d,%d,%d)' % (dt.year, dt.month, dt.day)
    #ret = dt.isoformat()
    ret = int(dt.strftime("%s")) * 1000 # JS epoch time counts ms
    return ret

def histogram_byday(data):
    'Collate data into per day counts, return dictionary keyed by femb_config'
    ret = defaultdict(Counter)
    for one in data['index']:
        cfgname = one['femb_config']
        dt = dateutil.parser.parse(one['timestamp']) # eg "20170613T164258"
        date = dt.date()
        ret[cfgname][date] += 1
    return ret

def hist2series(hist):
    'Convert to series data structure'
    ret = list()
    for cfgname, one in hist.items():
        data = one.items()
        data.sort()
        ret.append(dict(name=cfgname, data=data))
    return ret

def load(fp):
    return json.loads(fp.read())

def dumps(dat):
    return json.dumps(dat, default=serialize_date, indent=4)

def main(cfgfile, datfile, outfile=None):
    '''
    Read cfg and dat JSON files, write to outfile or stdout
    '''
    cfg = load(open(cfgfile))
    dat = load(open(datfile))
    hist = histogram_byday(dat)
    series = hist2series(hist)
    plot = dict(cfg, series=series)
    outstr = dumps(plot)
    if outfile:
        open(outfile, 'w').write(outstr)
    else:
        print outstr

if '__main__' == __name__:

    cfg = sys.argv[1]
    dat = sys.argv[2]
    try:
        out = sys.argv[3]
    except IndexError:
        out = "/dev/stdout"
    main(cfg,dat,out)
