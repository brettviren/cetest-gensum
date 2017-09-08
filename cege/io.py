#!/usr/bin/env python

import json

def serialize_date(dt):
    # ret = 'Date.UTC(%d,%d,%d)' % (dt.year, dt.month, dt.day)
    #ret = dt.isoformat()
    ret = int(dt.strftime("%s")) * 1000 # JS epoch time counts ms
    return ret


def load(fp):
    '''
    Load JSON file.  Try hard even if it was written badly.
    '''
    dat = fp.read()
    for n in range(3):
        dat = json.loads(dat)
        if type(dat) == dict or type(dat) == list:
            return dat
    raise ValueError("Could not load result file")

def dumps(dat):
    return json.dumps(dat, default=serialize_date, indent=4) + '\n'

def save(dat, fp):
    fp.write(dumps(dat))

                

