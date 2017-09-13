#!/usr/bin/env python

# prepare installation area:
# $ ln -s /dsk/1/data/sync-json $HOME/public_html/data

# prepare dev area
# $ virtualenv --system-site-packages -p python2 venv
# $ source venv/bin/activate
# $ pip install -r requirements.txt 
# $ ./waf configure --prefix=$HOME/public_html/summary
# $ ./waf build install


limit_count = None
#limit_count = 100

# Categories of tests to process
categories = [
    "adcasic",
    "feasic",
    "femb",
    "osc",
#    "flash",
]

taxa = [
#    "adcasic",                  # a sample result of the ADC ASIC test
#    "adcasicindex",             # make index of all adcasic results

#    "feasic",                   # a sample result of the FE ASIC test
#    "femb",                     # a sample result of the FEMB test

    #"adcid",                    # collect on ADC ASIC ident
    #"feid",                     # collect on FE ASIC ident
    #"feasicindex",              # make index of all feasic results
    #"fembindex",                # make index of all FEMB results
    # "adcboard",                 # collect ADC ASIC test board ident
    #"oscindex",                      # oscillator tests indices
]



import os
import time
import cege
from collections import defaultdict

def options(opt):
    opt.add_option('--data-root', action='store', default="/dsk/1/data/sync-json",
                   help='Point to the root directory holding the data')
    pass

def configure(cfg):
    #cfg.find_program("jq",var="JQ",mandatory=True)
    #cfg.find_program("yasha",var="YASHA",mandatory=True)
    #cfg.find_program("cege",var="CEGE",mandatory=True)
    pass

import importlib

def render_summary(**params):   
    'Render a summary'
    def task(tsk):
        cege.io.render(tsk.outputs[0].abspath(),
                       tsk.inputs[0].abspath(),
                       **params)
        tsk.outputs[1].write(cege.io.dumps(params))
    return task

def compile_index(mod):
    'Compile an index'
    def task(tsk):
        index = mod.indexer(tsk.inputs)
        tsk.outputs[0].write(cege.io.dumps(index))
    return task

def render_index(tsk):
    'Render an index'
    index = cege.io.load(tsk.inputs[1])
    cege.io.render(tsk.outputs[0].abspath(), tsk.inputs[0].abspath(), index=index)

def compile_testing_rates(mod):
    'Compile testing rates JSON file'
    def task(tsk):
        cfg_node, index_node = tsk.inputs
        json_node = tsk.outputs[0]
        rates = mod.testing_rates(cege.io.load(cfg_node),
                                  cege.io.load(index_node))
        json_node.write(cege.io.dumps(rates))
    return task

def compile_cfg_index(meth):
    'Compile cfg+index to JSON file'
    def task(tsk):
        cfg_node, index_node = tsk.inputs
        json_node = tsk.outputs[0]
        rates = meth(cege.io.load(cfg_node), cege.io.load(index_node))
        json_node.write(cege.io.dumps(rates))
    return task


def render_generic(**params):
    'Render a template against the params'
    def task(tsk):
        'Generic render'
        tmpl = tsk.inputs[0]
        html = tsk.outputs[0]
        cege.io.render(html.abspath(), tmpl.abspath(), **params)
    return task

def render_association(categ, serial):
    def task(tsk):
        tmpl = tsk.inputs[0]
        assert categ in os.path.basename(tmpl.abspath())
        html = tsk.outputs[0]
        summaries = [cege.io.load(node) for node in tsk.inputs[1:]]
        cege.io.render(html.abspath(), tmpl.abspath(),
                       category=categ, serial=serial, index=summaries)
    return task


def build_testing_rates(bld, mod, categ, index_json_node):
    'Do build stuff for testing rates plots'
    if not hasattr(mod, "testing_rates"):
        print("No testing_rates for %s" % categ)
        return
    plot_cfg_node = bld.path.find_resource("cfg/%s-testing-rate.json"%categ)
    plot_json_node = bld.path.find_or_declare("%s-testing-rate.json"%categ)
    plot_tmpl_node = bld.path.find_resource("j2/%s-testing-rate.html.j2"%categ)
    plot_html_node = bld.path.find_or_declare("%s-testing-rate.html"%categ)
    bld(rule=compile_cfg_index(mod.testing_rates),
        source=[plot_cfg_node, index_json_node],
        target=[plot_json_node])
    bld(rule=render_generic(), source=[plot_tmpl_node], target=[plot_html_node])
    bld.install_as("${PREFIX}/%s/testing-rate.html"%categ, plot_html_node)
    bld.install_as("${PREFIX}/%s/testing-rate.json"%categ, plot_json_node)


def build_plot(bld, categ, methname, index_json_node):
    'Build generic plot via category module and method name'
    try:
        mod = importlib.import_module("cege.%s" % categ)
    except ImportError:
        return

    meth = getattr(mod, methname, None)
    if not meth:
        return

    dashname = methname.replace('_','-')
    fullname = categ + '-' + dashname

    plot_cfg_node = bld.path.find_resource("cfg/%s.json"%fullname)
    if not plot_cfg_node:
        print ("No such file: cfg/%s.json"%fullname)
    plot_json_node = bld.path.find_or_declare("%s.json"%fullname)
    plot_tmpl_node = bld.path.find_resource("j2/%s.html.j2"%fullname)
    plot_html_node = bld.path.find_or_declare("%s.html"%fullname)
    bld(rule=compile_cfg_index(meth),
        source=[plot_cfg_node, index_json_node],
        target=[plot_json_node])
    bld(rule=render_generic(), source=[plot_tmpl_node], target=[plot_html_node])
    bld.install_as("${PREFIX}/%s/%s.html"%(categ, dashname), plot_html_node)
    bld.install_as("${PREFIX}/%s/%s.json"%(categ, dashname), plot_json_node)


def build_assoc_html(bld, categ, sersum):
    'Build HTML for associated tests'
    tmpl_node = bld.srcnode.find_resource("j2/assoc-%s.html.j2"%categ)
    assert(tmpl_node)
    for serial, sum_nodes in sersum.items():
        html_node = bld.path.find_or_declare("assoc-{}-{}.html".format(categ,serial))
        bld(rule=render_association(categ, serial),
            source=[tmpl_node]+sum_nodes, target=[html_node])
        bld.install_as('${PREFIX}/%s/%s/index.html' % (categ, serial), html_node)


def build(bld):
    
    # assoc[thing][serial] -> list of summaries
    associations = defaultdict(lambda: defaultdict(list))

    for categ in categories:
        mod = importlib.import_module("cege.%s" % categ)



        # define tasks to build individual summaries
        seed_nodes = list()
        json_nodes = list()
        summary_tmpl_node = bld.srcnode.find_resource("j2/%s-summary.html.j2"%categ)


        seed_paths = mod.seed_paths()
        print ("#%s: %d"%(categ, len(seed_paths)))

        for seed in seed_paths:
            summary = mod.summarize(seed)
            unique = mod.unique(summary)
            instdir = mod.instdir(summary)

            seed_node = bld.root.find_node(seed)
            seed_nodes.append(seed_nodes)

            html_node = bld.path.find_or_declare(unique + ".html")
            json_node = bld.path.find_or_declare(unique + ".json")
            json_nodes.append(json_node)

            bld(rule=render_summary(**summary),
                source=[summary_tmpl_node, seed_node],
                target=[html_node, json_node])

            instdir = "${PREFIX}/" + instdir
            bld.install_as(instdir+"/index.html", html_node)

            # handle installation of any extra files
            installs = summary.get('install', list())
            for src in installs:
                if type(src) == tuple:
                    src,dst = src
                else:
                    dst = os.path.basename(src)
                src_node = bld.root.find_node(src)
                assert(src_node)
                bld.install_as(instdir+"/"+dst, src_node)
            

            if limit_count and len(seed_nodes) > limit_count:
                break           # short-circuit seeds for faster testing

            assoc = summary.get("associations", dict())
            for thing, ids in assoc.items():
                for one_id in ids:
                    associations[thing][one_id].append(json_node)
            continue

        index_json_node = bld.path.find_or_declare("%s.index.json"%categ)
        bld(rule=compile_index(mod), source=json_nodes, target=[index_json_node])

        index_tmpl_node = bld.srcnode.find_resource("j2/%s-index.html.j2"%categ)
        index_html_node = bld.path.find_or_declare("%s-index.html"%categ)
        bld(rule=render_index,
            source=[index_tmpl_node, index_json_node],
            target=[index_html_node])
        bld.install_as("${PREFIX}/%s/index.html"%categ, index_html_node)

        build_plot(bld, categ, 'testing_rates', index_json_node)
        if categ == 'adcasic':
            build_plot(bld, 'adcboard', 'usage', index_json_node)

        continue                # end testing summarizing categories

    print ("Association caegories: %s" % str(associations.keys()))
    for categ, sersum in associations.items():
        build_assoc_html(bld, categ, sersum)


    # Top level page
    j2_node = bld.path.find_resource("j2/top.html.j2")
    html_node = bld.path.find_or_declare("top.html")
    bld(rule=render_generic(date_generated=time.asctime()),
        source=[j2_node], target=[html_node])
    bld.install_as('${PREFIX}/index.html', html_node)

