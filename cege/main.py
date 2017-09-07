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
@click.option('-c','--category', type=click.Choice(['adcasic','feasic','femb']),
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

def main():
    cli(obj=dict())

    
