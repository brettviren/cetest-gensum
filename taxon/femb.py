from util import *
import sys

#
# The FEMB taxon
#
def seeder(bld, **params):
    ret = dataroot(bld).ant_glob("*/dsk/*/oper/femb/*/*/fembTest_powercycle_test/params.json")
    print "#femb:\t%d" % len(ret)
    return ret


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

    # Some entries have garbage JSON
    for maybe_garbage in ["adc_asics","fe_asics"]:
        val = jparam[maybe_garbage];
        if ',' in val[0][0]:
            val[0] = map(str, split(val[0][0],','))

    ts = str(jparam["session_start_time"])

    # make up a "board" ID
    bid = '-'.join([ str(jparam["box_ids"][0]),
                     str(jparam["fm_ids"][0]),
                     str(jparam["am_ids"][0])])
    ident = '-'.join([bid, ts])

    try:
        adcids = [str(jparam["adc_asics"][0][ind]) for ind in range(8)]
        feids =  [str(jparam[ "fe_asics"][0][ind]) for ind in range(8)]
    except IndexError:
        sys.stderr.write("Failed to get expected asics for %s:\nadc:%s\nfe:%s\n"% (seed_node.abspath(), jparam["adc_asics"], jparam["fe_asics"]))
        return


    taxon = 'femb'
    jq_node = jq_file(bld, taxon)
    j2_node = j2_file(bld, taxon)
    json_node = prod_file(bld, taxon, ident, format='json')
    html_node = prod_file(bld, taxon, ident, format='html')

    png_nodes = basedir.ant_glob("*/*.png")
    
    injester = bld.path.find_resource("femb-summary.py")
    bld(rule="${SRC[0]} ${SRC[1]} > ${TGT}",
        source=[injester, seed_node], target=[json_node])

    subdir = install_path(taxon, "femb-"+bid, ts)
    reltoroot = '/'.join(['..']*len(subdir.split('/')))

    bld(rule="${YASHA} -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[j2_node, json_node], target=[html_node])

    out = os.path.join("${PREFIX}", subdir)
    bld.install_as(os.path.join(out, "index.html"), html_node)

    png_nodes = basedir.ant_glob("*/*.png")
    if png_nodes:
        bld.install_files(out, png_nodes)

    return dict(ident=ident, serial=bid, adcids=adcids, feids=feids, timestamp=ts, board_id=bid, 
                json_node = json_node, html_node=html_node, png_nodes = png_nodes,
                html_subdir = subdir)


