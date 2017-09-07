#!/usr/bin/env python

import json

def serialize_date(dt):
    # ret = 'Date.UTC(%d,%d,%d)' % (dt.year, dt.month, dt.day)
    #ret = dt.isoformat()
    ret = int(dt.strftime("%s")) * 1000 # JS epoch time counts ms
    return ret


def load(fp):
    return json.loads(fp.read())

def dumps(dat):
    return json.dumps(dat, default=serialize_date, indent=4)
def save(dat, fp):
    fp.write(dumps(dat))

                

