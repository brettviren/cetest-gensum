#!/usr/bin/env python
'''
A CLI.
'''

import click

@click.group("cege")
@click.pass_context
def cli(ctx):
    '''
    Cold Electronics Generator CLI tool
    '''
    pass

@cli.command('rates-chart-data')
@click.option('-c','--category', type=click.Choice(['adcasic','feasic','femb','osc']),
              help='Testing category', required=True)
@click.option('-o','--output',type=click.File('wb'),
              help='Output JSON chart filename')
@click.option('-t','--template',type=click.File('rb'),
              help='Template file')
@click.option('-i','--input',type=click.File('rb'),
              help='Input JSON index file')
@click.pass_context
def rates_chart_data(ctx, category, output, template, input):
    '''
    Produce rates chart JSON data file from cfg and index JSON
    '''
    import io, rates
    meth = getattr(rates, category)
    outdat = meth(io.load(template), io.load(input))
    io.save(outdat, output)


@cli.command('board-usage')
@click.option('-o','--output',type=click.File('wb'),
              help='Output JSON chart filename')
@click.option('-t','--template',type=click.File('rb'),
              help='Template file')
@click.option('-i','--input',type=click.File('rb'),
              help='Input JSON index file')
@click.pass_context
def board_usage(ctx, output, template, input):
    '''
    Produce board usage JSON data file from cfg and index JSON.
    '''
    import io, rates
    outdat = rates.board_usage(io.load(template), io.load(input))
    io.save(outdat, output)

@cli.command('summarize-params')
@click.option('-c','--category',type=str, default="",
              help='Test category, if unset, guess based on file path')
@click.option('-o','--output',type=click.File('wb'), default='-',
              help='Output file for summary JSON')
@click.argument('paramsfile', type=click.Path())
@click.pass_context
def summarize_params(ctx, category, output, paramsfile):
    '''
    Produce a summary of a test params.json file.
    '''
    import io, raw
    if not category:
        category = raw.guess_category(paramsfile)
        print 'guessed',category

    params = io.load(open(paramsfile, 'r'))
    summary = raw.summarize_params(category, **params)
    io.save(summary, output)

@cli.command('summarize')
@click.option('-c','--category',type=str, default="",
              help='Test category, if unset, guess based on file path')
@click.option('-o','--output',type=click.File('wb'), default='-',
              help='Output file for summary JSON')
@click.argument('paramsfile', type=click.Path())
@click.pass_context
def summarize(ctx, category, output, paramsfile):
    '''
    Produce a summary of a test params.json file.
    '''
    import io, raw
    summary = raw.summarize(paramsfile, category)
    io.save(summary, output)



def main():
    cli(obj=dict())

    
