#!/usr/bin/env python
'''
Do testing rates related processing.
'''


from cege import histo

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


def anonymous(cfg, dat):
    'Collect tested and passed rates data'
    hist_tested = histo.byday_if(dat, key='completed')
    hist_aborted = histo.byday_if(dat, key='aborted')
    hist_passed = histo.byday_count(dat, key='passed')
    hist_failed = histo.byday_count(dat, key='failed')

    return dict(tested = dict(cfg, series = histo.to_series(hist_tested),
                              subtitle=dict(text="Tests per day")),
                aborted = dict(cfg, series = histo.to_series(hist_aborted),
                               subtitle=dict(text="Tests aborted per day")),
                passed = dict(cfg, series = histo.to_series(hist_passed),
                              subtitle=dict(text="Units passed per day")),
                failed = dict(cfg, series = histo.to_series(hist_failed),
                              subtitle=dict(text="Units failed per day"))
    )
    
osc = anonymous
flash = anonymous



def feasic(cfg, dat):
    'Simple plots by femb_config'
    hist = histo.byday(dat)
    series = histo.to_series(hist)
    plot = dict(cfg, series=series)
    return plot

def femb(cfg, dat):
    'Simple plots by femb_config'
    hist_tested = histo.byday_count(dat, key='completed')
    hist_aborted = histo.byday_count(dat, key='aborted')
    return dict(tested = dict(cfg, series = histo.to_series(hist_tested),
                              subtitle=dict(text="Tests completed")),
                aborted = dict(cfg, series = histo.to_series(hist_aborted),
                              subtitle=dict(text="Tests aborted")))





def board_usage(cfg, dat):
    '''Return board usage data.  

    This returns a new dictionary build by replacing
    cfg.xAxis.categories and cfg.series.
    '''

    ret = dict()
    for name, tf in [('completed',True), ('aborted', False)]:
        cs = histo.to_stack(dat, completed=tf)
        copy = dict(cfg, series = cs['series'],
                    title=dict(text="ADC Test Board Usage: %s runs" % name.capitalize()))
                    
        copy['xAxis'] = dict(copy['xAxis'], categories = cs['categories'])
        ret[name] = copy

    return ret
    
