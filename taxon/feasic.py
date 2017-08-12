from util import *

#
# The FE ASIC taxon
#
def seed_feasic(bld, **params):
    return dataroot(bld).ant_glob("*/dsk/*/oper/feasic/*/*/check_setup/params.json")

def build_feasic(bld, seed_node, **params):
    basedir=seed_node.parent.parent
    result_nodes = basedir.ant_glob("*/*-results.json")
    if not result_nodes:
        print "Got no results from %s" % basedir
        return
    png_nodes = basedir.ant_glob("*/*.png")
    if not png_nodes:
        print "Got no PNGs from %s" % basedir
        

    jparam = json.loads(seed_node.read())
    feids = [str(jparam["asic%did"%ind]) for ind in range(4)]
    bid = str(jparam["boardid"])
    ts = str(jparam["session_start_time"])
    ident = '-'.join([bid, ts])

    taxon = 'feasic'
    jq_node = jq_file(bld, taxon)
    j2_node = j2_file(bld, taxon)
    json_node = prod_file(bld, taxon, ident, format='json')
    html_node = prod_file(bld, taxon, ident, format='html')


    # got to do some data fixing.
    cleaner = bld.path.find_resource("clean-json")
    cleaned_results = list()
    for rn in result_nodes:
        tmprn = bld.path.find_or_declare("temp-"+rn.name)
        newrn = bld.path.find_or_declare(rn.name)
        rnpar = rn.parent.find_node("params.json")
        cleaned_results.append(newrn)
        bld(rule="${SRC[0]} ${SRC[1]} > ${TGT[0]}", source=[cleaner, rn], target=[tmprn])
        bld(rule="${JQ} -s '{params:.[0], feasic:.[1]}' ${SRC} > ${TGT}",
            source=[rnpar, tmprn], target=[newrn])

    bld(rule="${JQ} -s -f ${SRC} > ${TGT[0]}",
        source=[jq_node]+cleaned_results, target=[json_node])

    subdir = install_path(taxon, "board"+bid, ts)
    reltoroot = '/'.join(['..']*len(subdir.split('/')))

    extra = " ".join(["-v feasic%d %s" % (ind, feids[ind]) for ind in range(4)])
    extra += " -v board_id %s -v timestamp %s" % (bid, ts)
    bld(rule="${YASHA} -I.. -o ${TGT[0]} -v reltoroot %s %s -V ${SRC[1]} ${SRC[0]}" % (reltoroot, extra),
        source=[j2_node, json_node], target=[html_node])
        
    out = os.path.join("${PREFIX}", subdir)
    bld.install_as(os.path.join(out, "index.html"), html_node)
    if png_nodes:
        bld.install_files(out, png_nodes)

    return dict(ident=ident, serial=bid, feids=feids, timestamp=ts, board_id=bid, 
                json_node = json_node, html_node=html_node, png_nodes = png_nodes,
                html_subdir = subdir)


