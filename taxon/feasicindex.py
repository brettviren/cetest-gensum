#
# This produces an index about all FE ASIC summaries.
#

from util import *

taxon = "feasic"

def seeder(bld, **params):
    node_list = list()
    for one in params["feasic"]:
        node = one["json_node"]
        node_list.append(node)
    return [node_list]          # one big seed holding list of all JSON nodes

def indexer(tsk):
    index = list()
    for node in tsk.inputs:
        print node
        dat = json.loads(node.read())
        dat = dat["feasic"]["check_setup"]["params"]
        
        base = dict(femb_config=dat["femb_config"],
                    timestamp=dat["session_start_time"],
                    board_id=fix_board_id(dat["boardid"]))
        asic_pass = dat["asic_pass"]
        for ind,apass in enumerate(asic_pass):
            ident = fix_asic_id(dat["asic%did"%ind])
            one = dict({'pass':apass, 'serial':ident}, **base)
            index.append(one)

    out = tsk.outputs[0]
    out.write(json.dumps(dict(index=index), indent=4))
    

def builder(bld, node_list, **params):

    # output nodes
    json_node = prod_file(bld, taxon, 'index', schema='index', format='json')
    j2_node = j2_file(bld, taxon, schema="index")
    html_node = prod_file(bld, taxon, 'index', schema='index', format='html')

    bld(rule=indexer, source=node_list, target=[json_node])

    reltoroot = '..'
    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[j2_node, json_node], target=[html_node])

    bld.install_as("${PREFIX}/feasic/index.html", html_node)
    bld.install_as("${PREFIX}/feasic/index.json", json_node)


    # The plot
    
    # testing rate summary
    tr_j2_node = bld.path.find_resource('j2/testing-rate.html.j2')
    tr_cfg_node = bld.path.find_resource('fe-testing-rate-cfg.json')
    tr_json_node = prod_file(bld, taxon, 'testing-rate', schema='chart', format='json')
    tr_py_node = bld.path.find_resource('testing-rate.py')
    tr_html_node = prod_file(bld, taxon, 'testing-rate', schema='chart', format='html')

    bld(rule='${SRC} ${TGT}',
        source=[tr_py_node, tr_cfg_node, json_node], target=[tr_json_node])

    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[tr_j2_node, tr_json_node], target=[tr_html_node])

    bld.install_as("${PREFIX}/feasic/testing-rate.json", tr_json_node)
    bld.install_as("${PREFIX}/feasic/testing-rate.html", tr_html_node)
    
