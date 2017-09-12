import cege.raw
import cege.io
from .util import *
import sys

taxon = 'femb'

def seeder(bld, **params):
    ret = dataroot(bld).ant_glob("*/dsk/*/oper/femb/*/*/fembTest_powercycle_test/params.json")
    print ("#femb:\t%d" % len(ret))
    return ret


def builder(bld, seed_node, **params):
    basedir = seed_node.parent.parent

    png_nodes = basedir.ant_glob("*/*.png")
    if not png_nodes:
        print ("Got no PNGs from %s" % basedir)
    pdf_nodes = basedir.ant_glob("*/*.pdf")
    if not pdf_nodes:
        print ("Got no PDFs from %s" % basedir)
        
    # turn some data into metadata
    jparams = cege.raw.summarize_params('femb', **cege.io.load(seed_node))
    ts = jparams["timestamp"]
    bid = jparams["serial"]
    ident = bid + '-' + ts
    adcids = jparams['adc_ids']
    feids =  jparams['fe_ids']

    json_node = prod_file(bld, taxon, ident, format='json')
    j2_node = j2_file(bld, taxon)
    html_node = prod_file(bld, taxon, ident, format='html')

    bld(rule='${CEGE} summarize -o ${TGT} ${SRC}',
        source=[seed_node], target=[json_node])

    subdir = install_path(taxon, "femb-"+bid, ts)
    reltoroot = '/'.join(['..']*len(subdir.split('/')))

    bld(rule="${YASHA} -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[j2_node, json_node], target=[html_node])

    out = os.path.join("${PREFIX}", subdir)
    bld.install_as(os.path.join(out, "index.html"), html_node)

    # PNG and PDF files are not uniquely named in FEMB results
    for node in png_nodes + pdf_nodes:
        path = node.abspath().split('/')
        name = '_'.join(path[-2:])
        bld.install_as(os.path.join(out, name), node);


    return dict(ident=ident, serial=bid, adcids=adcids, feids=feids, timestamp=ts, board_id=bid, 
                json_node = json_node, html_node=html_node, png_nodes = png_nodes,
                html_subdir = subdir)


