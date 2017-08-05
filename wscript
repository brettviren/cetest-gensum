#!/usr/bin/env python

# virtualenv --system-site-packages -p python2 venv
# pip install -r requirements.txt 

# ln -s /dsk/1/data/sync-json $HOME/public_html/data
# ./waf configure --prefix=$HOME/public_html/summary

# Links in the HTML assume data/ and summary/ are siblings.

# Taxonomy

# - category :: the general test type, embodied as a femb_python main gui/cli program.
# - config :: the FEMB_CONFIG used by the daq software
# - sample :: one data acquisition with a summary JSON file and possible PNGs, category and possibly config specific
# - unit :: one physical ASIC for which a sample was aquired.  idientified by serial number

import os
from collections import defaultdict

def configure(cfg):
    cfg.find_program("jq",var="JQ",mandatory=True)
    cfg.find_program("yasha",var="YASHA",mandatory=True)

def adcasic_id(node):
    'Return the ADC ASIC ID based on the source JSON file'
    # cheat and use the file name
    return os.path.splitext(node.abspath())[0].split("_")[-1]

def build(bld):
    # The base directory where all the summary JSON/PNG gets synced.
    # This is assumed to be symlinked into the install directory as
    # "data/".
    basedir = bld.root.make_node("/dsk/1/data/sync-json")

    # Slurp in an ungodly amount of nodes.
    category_source = dict(
        adcasic = [adcasic_id, basedir.ant_glob("*/dsk/*/oper/adcasic/*/*/adcTest_*.json")],
    )

    # Do a JSON query with a jq file: src=[<jq>, <json>, ...], tgt=[<json>]
    jq = "${JQ} -s -f ${SRC} > ${TGT[0]}"
    # Do a render with a j2 file: src=[<j2>, <json>], tgt=[<html>]
    yasha = "${YASHA} -I.. -o ${TGT[0]} -V ${SRC[1]} ${SRC[0]}"

    def injest_sample(jqfile, srcnode, target):
        bld(rule="${SRC[2]} ${SRC[1]} | ${JQ} -s -f ${SRC[0]} > ${TGT[0]}",
            source=[jqfile, srcnode, "clean-json"], target=target)

    def generate_html(src, tgt):
        bld(rule=yasha, source=src, target=tgt)
        bld.install_files("${PREFIX}", tgt)

    # Run through the huge number of nodes producing a local summary
    # which is fodder for all the rest.
    for cat, (ider, src_nodes) in category_source.items():
        cat_samples = list()
        cat_id = defaultdict(list)

        sample_jq = cat+"-sample.jq"
        sample_html_j2 = cat+"-sample.html.j2"

        for src_node in src_nodes:
            name = os.path.basename(src_node.abspath()).replace(".json","")

            sample_id = ider(src_node)

            sample_json = name+"-sample.json"
            sample_html = name+"-sample.html"

            cat_samples.append(sample_json)
            cat_id[sample_id].append(sample_json)

            injest_sample(sample_jq, src_node, sample_json)
            generate_html([sample_html_j2, sample_json], sample_html)

        # summarize individual samples
        cat_summary_jq = cat +"-summary.jq"
        cat_summary_json = cat +"-summary.json"
        cat_summary_html_j2 = cat +"-summary.html.j2"
        cat_summary_html = cat +"-summary.html"

        bld(rule=jq, source=[cat_summary_jq]+cat_samples, target=cat_summary_json)
        generate_html([cat_summary_html_j2, cat_summary_json], cat_summary_html)


        # summarize per-unit
        cat_unit_jq = cat +"-unit.jq"
        cat_unit_html_j2 = cat +"-unit.html.j2"
        # process collated samples by unit ID
        for uid, samples in cat_id.items():
            cat_unit_json = cat + '-' + uid + '.json'
            cat_unit_html = cat + '-' + uid + '.html'
            bld(rule=jq, source=[cat_unit_jq]+samples, target=cat_unit_json)
            generate_html([cat_unit_html_j2, cat_unit_json], cat_unit_html)

