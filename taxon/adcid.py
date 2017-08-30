#
# The ADC ID taxon collects info about each ADC ASIC ID.
#

from util import *
from collections import defaultdict

taxon = "adcid"

def seeder(bld, **params):
    ret = defaultdict(list)
    for one in params["adcasic"]:
        serial = fix_asic_id(one["serial"])
        ret[serial].append(one["json_node"])
    for one in params["femb"]:
        for serial in one["adcids"]:
            serial = fix_asic_id(serial)
            ret[serial].append(one["json_node"])
    return ret.items()

def builder(bld, seed, **params):
    sn,json_nodes = seed

    # output nodes
    json_node = prod_file(bld, taxon, sn, format='json')
    html_node = prod_file(bld, taxon, sn, format='html')
    j2_node = j2_file(bld, taxon, schema="summary")

    def runner(tsk):
        cmd = tsk.inputs[0].abspath() # the script
        cmd += " %s %s " % (sn, tsk.outputs[0])
        for f in tsk.inputs[1:]:
            cmd += " %s " % f
        return tsk.exec_command(cmd)

    injester = bld.path.find_resource("adcid-summary.py")
    bld(rule=runner, source=[injester]+json_nodes, target=[json_node])

    reltoroot = '../..'
    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[j2_node, json_node], target=[html_node])

    bld.install_as("${PREFIX}/adcid/%s/index.html"%sn, html_node)
