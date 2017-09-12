from .util import *

import cege.adcasic

taxon = 'adcasic'


def seeder(bld, **params):
    paths = cege.adcasic.seed_paths()
    ret = [bld.path.make_node(p) for p in paths]
    assert(all(ret))
    print ("#adcasic:\t%d" % len(ret))
    return ret


def builder(bld, seed_node, **params):
    assert(seed_node)

    # sus out the seed to find what taxa instance products to build 
    pnode = seed_node.parent.find_node("params.json")
    jparam = json.loads(pnode.read())
    bid = fix_board_id(jparam['board_id'])
    sn = fix_asic_id(jparam['serials'][0])
    ts = str(jparam['timestamp'])

    label = smt_labels.get(ts, None)

    png_nodes = seed_node.parent.ant_glob("*.png")

    ident = '-'.join([sn,ts])


    jq_node = jq_file(bld, taxon)
    j2_node = j2_file(bld, taxon)
    json_node = prod_file(bld, taxon, ident, format='json')
    html_node = prod_file(bld, taxon, ident, format='html')

    subdir = install_path('adcasic', sn, ts)
    reltoroot = '/'.join(['..']*len(subdir.split('/')))

    bld(rule="${JQ} -s -f ${SRC} > ${TGT}",
        source=[jq_node, seed_node], target=[json_node])
    extra = " -v reltoroot %s " % reltoroot
    extra+= " -v label '%s'" % label
    bld(rule="${YASHA} --no-extensions -I.. -o ${TGT[0]} %s -V ${SRC[1]} ${SRC[0]}" % extra,
        source=[j2_node, json_node], target=[html_node])


    out = os.path.join("${PREFIX}", subdir)
    bld.install_as(os.path.join(out, "index.html"), html_node)
    bld.install_files(out, png_nodes)

    return dict(ident=ident, serial=sn, timestamp=ts, board_id=bid, 
                json_node = json_node, html_node=html_node, png_nodes = png_nodes,
                html_subdir = subdir)
