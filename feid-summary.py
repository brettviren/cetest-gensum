#!/usr/bin/env python
'''
Summarize all results for one FE ID
'''
import os
import sys
import json

feid = sys.argv[1]
output = sys.argv[2]
infiles = sys.argv[3:]

outdat = dict(ident=feid, feasic=list(), femb=list())
for infile in infiles:
    fname = os.path.basename(infile)
    restype = fname.split("_",1)[0]

    if restype == "feasic":
        dat = json.loads(open(infile).read())
        params = dat["feasic"]["check_setup"]["params"]
        boardid = params["boardid"]
        timestamp = params["session_start_time"]
        thisdat = dict(timestamp=timestamp,
                       path="board%s/%s"%(boardid,timestamp),
                       board_id=boardid)

    if restype == "femb":
        ids = fname.split("_")[1].split("-",3)
        ident = '-'.join(ids[:3]) # box-fm-am
        timestamp = ids[3].split(".",1)[0]
        thisdat = dict(timestamp=timestamp,
                       path="femb-%s/%s"%(ident, timestamp),
                       board_id=ident)


    outdat[restype].append(thisdat)

open(output,'w').write(json.dumps(dict(feid=outdat), indent=4))

