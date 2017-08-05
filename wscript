#!/usr/bin/env python

import os

def configure(cfg):
    cfg.find_program("jq",var="JQ",mandatory=True)
    cfg.find_program("j2",var="J2",mandatory=True)
    cfg.find_program("yasha",var="YASHA",mandatory=True)

def build(bld):
    basedir = bld.root.make_node("/dsk/1/data/sync-json")
    adcasic_json = basedir.ant_glob("*/dsk/*/oper/adcasic/*/*/adcTest_*.json")

    yasha = "${YASHA} -I.. -o ${TGT[0]} -V ${SRC[1]} ${SRC[0]}"

    summary_jsons = list()
    for one in adcasic_json:
        basejson = os.path.basename(one.abspath())
        base = basejson.replace(".json","")

        one_json = bld.path.find_or_declare("summary-"+basejson)
        summary_jsons.append(one_json)
        bld(rule="${JQ} -s -f ${SRC[0].abspath()} ${SRC[1].abspath()} > ${TGT[0].abspath()}",
            source=["adcasic.jq", one], target=one_json)
        bld(rule=yasha, source=["adcasic-display.html.j2", one_json], target="adcasic-display-"+base+".html")
    bld(rule="""${JQ} -s '{"adcasic":[.[] | .adcasic[0]]}' ${SRC} > ${TGT[0].abspath()}""",
        source=summary_jsons, target="adcasic-summary.json")
    bld(rule=yasha,
        source=["adcasic.html.j2", "adcasic-summary.json"], target="adcasic-summary-all.html")
