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


def load(fp):
    return json.loads(fp.read())

def dumps(dat):
    return json.dumps(dat, default=serialize_date, indent=4)

                


def generic_plot(cfg, dat):
    'A single plot data with series spanning raw femb_config strings'
    hist = histogram_byday(dat)
    series = hist2series(hist)
    plot = dict(cfg, series=series)
    return plot

def main(cfgfile, datfile, outfile=None):
    '''
    Read cfg and dat JSON files, write to outfile or stdout
    '''
    cfg = load(open(cfgfile))
    dat = load(open(datfile))

    if "adc-" in cfgfile:       # kludge!
        plot = adc_plots(cfg, dat)
    else:
        plot = generic_plot(cfg, dat)

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

