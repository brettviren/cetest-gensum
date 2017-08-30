#!/usr/bin/env python
'''
Summarize all results for one ADC ID
'''
import os
import sys
import json

from taxon.util import *

def summarize(adcid, infiles):
    outdat = dict(ident=adcid, adcasic=list(), femb=list())
    for infile in infiles:
        fname = os.path.basename(infile)
        restype = fname.split("_",1)[0]

        if restype == "adcasic":
            print infile
            dat = json.loads(open(infile).read())
            adcasic = dat["adcasic"] # get substructure
            timestamp = adcasic["timestamp"]
            bid = fix_board_id(adcasic['board_id'])
            thisdat = dict(timestamp=timestamp,
                           path="%s/%s"%(adcid,timestamp),
                           board_id=bid)

        if restype == "femb":
            ids = fname.split("_")[1].split("-",3)
            ident = '-'.join(ids[:3]) # box-fm-am
            timestamp = ids[3].split(".",1)[0]
            thisdat = dict(timestamp=timestamp,
                           path="femb-%s/%s"%(ident, timestamp),
                           board_id=ident)


        outdat[restype].append(thisdat)
    return outdat

if '__main__' == __name__:
    adcid = sys.argv[1]
    output = sys.argv[2]
    infiles = sys.argv[3:]
    outdat = summarize(adcid, infiles)
    open(output,'w').write(json.dumps(dict(adcid=outdat), indent=4))

