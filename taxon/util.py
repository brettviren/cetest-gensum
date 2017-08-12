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
