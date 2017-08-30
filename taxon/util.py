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


def j2_file(bld, taxon, schema='summary', format = "html.j2"):
    'enforce some naming conventions for j2 files'
    name = "j2/{taxon}-{schema}.{format}".format(**locals())
    node = bld.path.find_resource(name)
    if not node:
        raise ValueError("Failed to find: %s" % name)
    return node
def jq_file(bld, taxon, schema='summary', format = "jq"):
    'enforce some naming conventions for jq files'
    return bld.path.find_resource("jq/{taxon}-{schema}.{format}".format(**locals()))


def prod_file(bld, taxon, ident, schema='summary', format='json'):
    'Enforce naming convention for products'
    return bld.path.find_or_declare(product_name.format(**locals()))


def fix_board_id(thing):
    'Try to unstupify board IDs'
    bogus = "bogus"
    thing = str(thing).strip().lower()
    if not thing:
        return bogus
    if thing[0] in "*_-":
        return bogus
    return thing

def fix_asic_id(thing):
    'Try to unstupify ASIC IDs'
    bogus = "BOGUS"
    thing = str(thing).strip().upper()
    if not thing:
        return bogus
    if thing[0] in "*_-":
        return bogus
    return thing
