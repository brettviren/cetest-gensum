from . import rates
def usage(cfg, index):
    '''
    Produce a plot data structure.
    '''
    return rates.board_usage(cfg, dict(index=index.values()))
        
