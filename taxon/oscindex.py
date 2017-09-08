#!/usr/bin/env python

from util import *

#import smtdb
#smt_labels = smtdb.slurp_osc_labels()

taxon = 'osc'

def seeder(bld, **params):


    # be sensitive to aborted runs, look for evidence that the first
    # cycle was started.
    ret = dataroot(bld).ant_glob("*/dsk/*/oper/osc/osc/*/OscillatorTestingThermalCycle1/params.json") 
    print "#osc:\t%d" % len(ret)
    return [ret]                # one big glob

def indexer(tsk):
    index = list()
    for c1node in tsk.inputs:
        params = json.load(c1node)
        this = dict(hostname = params['hostname'],
                    timestamp = params['session_start_time'],
                    version = params['femb_python_location'].split('/')[-2][12:],
                    femb_config = params['femb_config'])

        snode = c1node.parent.parent.find_node('OscillatorTestingSummary/Summary.txt')
        if snode:
            summary = json.load(snode)
            passed = 0
            for one in summary[1:]:
                if all([s == 'Passed' for s in one[1:]]):
                    passed += 1
            this['passed'] = passed
            this['failed'] = len(one)-passed
            this['completed'] = 4
            this['aborted'] = 0
        else:                   # looks like an aborted 
            this['passed'] = 0
            this['failed'] = 0
            this['completed'] = 0
            this['aborted'] = 4

        index.append(this)                    

    out = tsk.outputs[0]
    out.write(json.dumps(dict(index=index), indent=4))

def builder(bld, nodes, **params):

    json_node = prod_file(bld, taxon, 'index', schema='index', format='json')

    # testing rate plot
    tr_j2_node = bld.path.find_resource('j2/osc-testing-rate.html.j2')
    tr_cfg_node = bld.path.find_resource('osc-testing-rate-cfg.json')
    tr_json_node = prod_file(bld, taxon, 'testing-rate', schema='chart', format='json')
    tr_html_node = prod_file(bld, taxon, 'testing-rate', schema='chart', format='html')


    bld(rule=indexer, source=nodes, target=[json_node])

    reltoroot = '..'

    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[tr_j2_node, tr_json_node], target=[tr_html_node])

    # The plots
    
    bld(rule='${CEGE} rates-chart-data -c osc -t ${SRC[0]} -i ${SRC[1]} -o ${TGT[0]}',
        source=[tr_cfg_node, json_node], target=[tr_json_node])

    bld.install_as("${PREFIX}/osc/testing-rate.json", tr_json_node)
    bld.install_as("${PREFIX}/osc/index.html", tr_html_node)
    
