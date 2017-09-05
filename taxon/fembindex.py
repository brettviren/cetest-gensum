#
# This produces an index about all ADC ASIC summaries.
#

from util import *

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
            dat = dat["femb"]["fembTest_summary"]["params"]
        except KeyError:
            print "Skipping, missing FEMB data for %s" % node.name
            continue

        this = dict()
        this['pass'] = None
        this['hostname'] = dat['hostname']
        this['femb_config'] = dat['femb_config']
        bid = '-'.join([ str(dat["box_ids"][0]),
                         str(dat["fm_ids"][0]),
                         str(dat["am_ids"][0])])
        this['serial'] = this['board_id'] = bid
        this['version'] = dat['femb_python_location'].split('/')[-2][13:]
        this['timestamp'] =  dat['session_start_time']
        this['board_id'] = fix_board_id(this['board_id'])
        this['adc_asics'] = dat['adc_asics'][0] # warning, assumes just
        this['fe_asics'] = dat['fe_asics'][0]   # one set of asics
        index.append(this)

    out = tsk.outputs[0]
    out.write(json.dumps(dict(index=index), indent=4))

def builder(bld, node_list, **params):

    # output nodes
    json_node = prod_file(bld, taxon, 'index', schema='index', format='json')
    j2_node = j2_file(bld, taxon, schema="index")
    html_node = prod_file(bld, taxon, 'index', schema='index', format='html')

    # testing rate summary
    tr_j2_node = bld.path.find_resource('j2/testing-rate.html.j2')
    tr_cfg_node = bld.path.find_resource('femb-testing-rate-cfg.json')
    tr_json_node = prod_file(bld, taxon, 'testing-rate', schema='chart', format='json')
    tr_py_node = bld.path.find_resource('testing-rate.py')
    tr_html_node = prod_file(bld, taxon, 'testing-rate', schema='chart', format='html')

    bld(rule=indexer, source=node_list, target=[json_node])

    reltoroot = '..'

    # The index

    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[j2_node, json_node], target=[html_node])
    bld.install_as("${PREFIX}/femb/index.html", html_node)

    # The plot
    
    bld(rule='${SRC} ${TGT}',
        source=[tr_py_node, tr_cfg_node, json_node], target=[tr_json_node])

    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[tr_j2_node, tr_json_node], target=[tr_html_node])

    bld.install_as("${PREFIX}/femb/testing-rate.json", tr_json_node)
    bld.install_as("${PREFIX}/femb/testing-rate.html", tr_html_node)
