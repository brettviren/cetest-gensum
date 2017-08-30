#
# This collects info about the ADC ASIC test boards used.
#

from util import *
from collections import defaultdict

taxon = "adcboard"

def seeder(bld, **params):
    ret = defaultdict(list)
    for one in params["adcasic"]:
        bid = fix_board_id(one["board_id"])
        ret[bid].append(one["json_node"])
    return ret.items()


def make_indexer(bid):
    def indexer(tsk):
        index = list()
        for node in tsk.inputs:
            print node
            dat = json.loads(node.read())
            dat = dat["adcasic"]
            this = dict()
            for key in 'hostname timestamp version board_id serial femb_config pass'.split():
                this[key] = dat[key]
            this['board_id'] = fix_board_id(this['board_id'])
            this['serial'] = fix_asic_id(this['serial'])
            index.append(this)

        out = tsk.outputs[0]
        out.write(json.dumps(dict(index=index, boardid=bid), indent=4))
    return indexer

def builder(bld, seed, **params):
    bid,json_nodes = seed

    # output nodes
    json_node = prod_file(bld, taxon, bid, schema='summary', format='json')
    j2_node = j2_file(bld, taxon, schema="summary")
    html_node = prod_file(bld, taxon, bid, schema='summary', format='html')

    bld(rule=make_indexer(bid), source=json_nodes, target=[json_node])

    reltoroot = '../..'
    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[j2_node, json_node], target=[html_node])

    bld.install_as("${PREFIX}/adcboard/%s/index.html"%bid, html_node)
