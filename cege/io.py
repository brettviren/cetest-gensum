#!/usr/bin/env python

import os
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

def load_path(path):
    return load(open(path, encoding='utf-8'))

def dumps(dat):
    return json.dumps(dat, default=serialize_date, indent=4) + '\n'

def save(dat, fp):
    fp.write(dumps(dat).encode())


def render(out, template, **params):
    '''
    Render a Jinja2 against dict 'data' plus any extra.
    '''
    path = os.path.realpath(template)
    base = os.path.dirname(path)
    rel = os.path.basename(path)
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(base))
    env.globals.update(zip=zip)
    tmplobj = env.get_template(rel)
    text = tmplobj.render(**params)
    open(out,'w').write(text)
