#
# This produces an index about all ADC ASIC summaries.
#

from .util import *

taxon = "adcasic"

def seeder(bld, **params):
    node_list = list()
    for one in params["adcasic"]:
        node = one["json_node"]
        node_list.append(node)
    return [node_list]          # one big seed holding list of all JSON nodes

def indexer(tsk):
    index = list()
    for node in tsk.inputs:
        dat = json.loads(node.read())
        dat = dat["adcasic"]
        this = dict()
        for key in 'hostname timestamp version board_id serial femb_config pass'.split():
            this[key] = dat[key]
        this['board_id'] = fix_board_id(this['board_id'])
        this['serial'] = fix_asic_id(this['serial'])
        index.append(this)

    out = tsk.outputs[0]
    out.write(json.dumps(dict(index=index), indent=4))
    

def builder(bld, node_list, **params):

    # output nodes
    json_node = prod_file(bld, taxon, 'index', schema='index', format='json')
    j2_node = j2_file(bld, taxon, schema="index")
    html_node = prod_file(bld, taxon, 'index', schema='index', format='html')

    # testing rate plot
    tr_j2_node = bld.path.find_resource('j2/adc-testing-rate.html.j2')
    tr_cfg_node = bld.path.find_resource('adc-testing-rate-cfg.json')
    tr_json_node = prod_file(bld, taxon, 'testing-rate', schema='chart', format='json')
    tr_html_node = prod_file(bld, taxon, 'testing-rate', schema='chart', format='html')

    # board usage plot
    bu_j2_node = bld.path.find_resource('j2/adc-board-usage.html.j2') 
    bu_cfg_node = bld.path.find_resource('adc-board-rates.json')
    bu_json_node = prod_file(bld, taxon, 'board-usage', schema='chart', format='json')
    bu_html_node = prod_file(bld, taxon, 'board-usage', schema='chart', format='html')

    bld(rule=indexer, source=node_list, target=[json_node])

    reltoroot = '..'

    # The index

    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[j2_node, json_node], target=[html_node])
    bld.install_as("${PREFIX}/adcasic/index.html", html_node)

    # The plot
    
    bld(rule='${CEGE} rates-chart-data -c adcasic -t ${SRC[0]} -i ${SRC[1]} -o ${TGT[0]}',
        source=[tr_cfg_node, json_node], target=[tr_json_node])

    bld(rule='${CEGE} board-usage -t ${SRC[0]} -i ${SRC[1]} -o ${TGT[0]}',
        source=[bu_cfg_node, json_node], target=[bu_json_node])

    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[tr_j2_node, tr_json_node], target=[tr_html_node])

    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[bu_j2_node, bu_json_node], target=[bu_html_node])

    bld.install_as("${PREFIX}/adcasic/testing-rate.json", tr_json_node)
    bld.install_as("${PREFIX}/adcasic/testing-rate.html", tr_html_node)
    bld.install_as("${PREFIX}/adcboard/usage.json", bu_json_node)
    bld.install_as("${PREFIX}/adcboard/usage.html", bu_html_node)
