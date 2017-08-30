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
    pdf_nodes = basedir.ant_glob("*/*.pdf")
    if not pdf_nodes:
        print "Got no PDFs from %s" % basedir
        
    jparam = json.loads(seed_node.read())

    # Some entries have garbage JSON
    for maybe_garbage in ["adc_asics","fe_asics"]:
        val = jparam[maybe_garbage];
        try:
            stuff = val[0][0]
        except IndexError:
            return
        if ',' in val[0][0]:
            val[0] = val[0][0].split(',')
        val[0] = [fix_asic_id(a) for a in val[0]]

    ts = str(jparam["session_start_time"])

    # make up a "board" ID
    bid = '-'.join([ str(jparam["box_ids"][0]),
                     str(jparam["fm_ids"][0]),
                     str(jparam["am_ids"][0])])
    ident = '-'.join([bid, ts])

    try:
        adcids = [fix_asic_id(jparam["adc_asics"][0][ind]) for ind in range(8)]
        feids =  [fix_asic_id(jparam[ "fe_asics"][0][ind]) for ind in range(8)]
    except IndexError:
        sys.stderr.write("Failed to get expected asics for %s:\nadc:%s\nfe:%s\n"% (seed_node.abspath(), jparam["adc_asics"], jparam["fe_asics"]))
        return


    taxon = 'femb'
    jq_node = jq_file(bld, taxon)
    j2_node = j2_file(bld, taxon)
    json_node = prod_file(bld, taxon, ident, format='json')
    html_node = prod_file(bld, taxon, ident, format='html')

    injester = bld.path.find_resource("femb-summary.py")
    bld(rule="${SRC[0]} ${SRC[1]} ${TGT}",
        source=[injester, seed_node], target=[json_node])

    subdir = install_path(taxon, "femb-"+bid, ts)
    reltoroot = '/'.join(['..']*len(subdir.split('/')))

    bld(rule="${YASHA} -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[j2_node, json_node], target=[html_node])

    out = os.path.join("${PREFIX}", subdir)
    bld.install_as(os.path.join(out, "index.html"), html_node)

    # PNG and PDF files are not uniquely named.  This code coludes with femb-summary.py
    for node in png_nodes + pdf_nodes:
        path = node.abspath().split('/')
        name = '_'.join(path[-2:])
        bld.install_as(os.path.join(out, name), node);


    return dict(ident=ident, serial=bid, adcids=adcids, feids=feids, timestamp=ts, board_id=bid, 
                json_node = json_node, html_node=html_node, png_nodes = png_nodes,
                html_subdir = subdir)


