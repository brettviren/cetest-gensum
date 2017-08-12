from util import *

#
# The FEMB taxon
#
def seeder(bld, **params):
    return dataroot(bld).ant_glob("*/dsk/*/oper/femb/*/*/fembTest_powercycle_test/params.json")


def builder(bld, seed_node, **params):
    basedir = seed_node.parent.parent

    result_nodes = basedir.ant_glob("*/*-results.json")
    if not result_nodes:
        print "Got no results from %s" % basedir
        return
    png_nodes = basedir.ant_glob("*/*.png")
    if not png_nodes:
        print "Got no PNGs from %s" % basedir
        

    jparam = json.loads(seed_node.read())
    adcids = [str(jparam["adc_asics"][0][ind]) for ind in range(8)]
    feids =  [str(jparam[ "fe_asics"][0][ind]) for ind in range(8)]
    fmid = jparam["fm_ids"][0]
    ts = jparam["session_start_time"]

    taxon = 'femb'
    jq_node = jq_file(bld, taxon)
    j2_node = j2_file(bld, taxon)
    json_node = prod_file(bld, taxon, ident, format='json')
    html_node = prod_file(bld, taxon, ident, format='html')

    png_nodes = basedir.ant_glob("*/*.png")
    

    print seed_node
    pass

