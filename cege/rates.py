#!/usr/bin/env python
'''
Do testing rates related processing.
'''


import histo

def adcasic(cfg, dat):
    'Make ADC ASIC test rates plot data'
    hist_byfembconfig = histo.byday(dat)
    hist_byhostwarm = histo.byday_byhost(dat, cold=False)
    hist_byhostcold = histo.byday_byhost(dat, cold=True)
    hist_byboardcold = histo.byday_byboard(dat, cold=True)

    bhc_series = histo.to_series(hist_byhostcold)
    #print 'byhostcold=\n%s\n' % str(bhc_series)

    bbc_series = histo.to_series(hist_byboardcold)
    #print 'byboardcold=\n%s\n' % str(bbc_series)

    return dict(warm = dict(cfg, series = histo.to_series(hist_byhostwarm)),
                cold = dict(cfg, series = bhc_series),
                board = dict(cfg, series = bbc_series),
                config = dict(cfg, series = histo.to_series(hist_byfembconfig)),
    )


def osc(cfg, dat):
    'Collect oscillator tested and passed rates data'
    hist_tested = histo.byday(dat)
    hist_passed = histo.byday_count(dat, key='passed')
    hist_failed = histo.byday_count(dat, key='failed')
    return dict(tested = dict(cfg, series = histo.to_series(hist_tested)),
                passed = dict(cfg, series = histo.to_series(hist_passed),
                              subtitle=dict(text="Oscillators passed per day")),
                failed = dict(cfg, series = histo.to_series(hist_failed),
                              subtitle=dict(text="Oscillators failed per day")))
    


def simple(cfg, dat):
    'Simple plots by femb_config'
    hist = histo.byday(dat)
    series = histo.to_series(hist)
    plot = dict(cfg, series=series)
    return plot

feasic = simple
femb = simple


def board_usage(cfg, dat):
    '''Return board usage data.  

    This returns a new dictionary build by replacing
    cfg.xAxis.categories and cfg.series.
    '''

    cs = histo.to_stack(dat)
    copy = dict(cfg, series = cs['series'])
    copy['xAxis']['categories'] = cs['categories']
    return copy
    
