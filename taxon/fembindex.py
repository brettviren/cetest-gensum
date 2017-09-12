#
# This produces an index about all ADC ASIC summaries.
#

from .util import *

taxon = "femb"

def seeder(bld, **params):
    node_list = list()
    for one in params["femb"]:
        node = one["json_node"]
        node_list.append(node)
    return [node_list]          # one big seed holding list of all JSON nodes

def indexer(tsk):
    index = list()
    for node in tsk.inputs:
        dat = json.loads(node.read())
        try:
            params = dat["femb"]["params"]
            results = dat["femb"]["results"]
        except KeyError:
            print ("Skipping, missing FEMB data for %s" % node.name)
            continue

        completed = 0
        aborted = 1
        if "fembTest_summary" in results:
            completed = 1
            aborted = 0
        
        index.append(dict(params, completed=completed, aborted=aborted, ntests=len(results)))

    out = tsk.outputs[0]
    out.write(json.dumps(dict(index=index), indent=4))

def builder(bld, node_list, **params):

    # output nodes
    json_node = prod_file(bld, taxon, 'index', schema='index', format='json')
    j2_node = j2_file(bld, taxon, schema="index")
    html_node = prod_file(bld, taxon, 'index', schema='index', format='html')

    # testing rate summary
    tr_j2_node = bld.path.find_resource('j2/femb-testing-rate.html.j2')
    tr_cfg_node = bld.path.find_resource('femb-testing-rate-cfg.json')
    tr_json_node = prod_file(bld, taxon, 'testing-rate', schema='chart', format='json')
    tr_html_node = prod_file(bld, taxon, 'testing-rate', schema='chart', format='html')

    bld(rule=indexer, source=node_list, target=[json_node])

    reltoroot = '..'

    # The index

    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[j2_node, json_node], target=[html_node])
    bld.install_as("${PREFIX}/femb/index.html", html_node)

    # The plot
    
    bld(rule='${CEGE} rates-chart-data -c femb -t ${SRC[0]} -i ${SRC[1]} -o ${TGT[0]}',
        source=[tr_cfg_node, json_node], target=[tr_json_node])

    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[tr_j2_node, tr_json_node], target=[tr_html_node])

    bld.install_as("${PREFIX}/femb/testing-rate.json", tr_json_node)
    bld.install_as("${PREFIX}/femb/testing-rate.html", tr_html_node)
