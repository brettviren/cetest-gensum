#
# The ADC ID taxon collects info about each ADC ASIC ID.
#
def seed_adcid(bld, **params):
    ret = defaultdict(list)
    for one in params["adcasic"]:
        ret[one["serial"]].append(one)
    return ret.items()

def build_adcid(bld, seed, **params):
    sn,dats = seed
    print ("ADC %s" % sn)
    for dat in dats:
        print "\t%s %s" %(dat["ident"],dat["board_id"])

