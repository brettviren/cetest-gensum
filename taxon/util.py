import os
import json

# These are put together into a file naming convention:
product_name="{taxon}_{ident}.{schema}.{format}"


# Installed files are placed in a directory tree under ${PREFIX}.  The
# "serial" is either an ASIC, FEMB or test board serial number
# depending on the taxon.
def install_path(taxon, serial, timestamp):
    return "{taxon}/{serial}/{timestamp}".format(**locals())

def dataroot(bld):
    return bld.root.make_node(bld.options.data_root)

# enforce some naming conventions of our source files
def j2_file(bld, taxon, scheme='summary', format = "html.j2"):
    return bld.path.find_resource("j2/{taxon}-{scheme}.{format}".format(**locals()))
def jq_file(bld, taxon, scheme='summary', format = "jq"):
    return bld.path.find_resource("jq/{taxon}-{scheme}.{format}".format(**locals()))

# enforce naming convention for products
def prod_file(bld, taxon, ident, schema='summary', format='json'):
    return bld.path.find_or_declare(product_name.format(**locals()))
