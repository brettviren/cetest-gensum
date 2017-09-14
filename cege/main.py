#!/usr/bin/env python
'''
A CLI.
'''

import click
import cege.io
import cege.raw
import cege.rates

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
@click.option('-t','--template',type=click.File('r'),
              help='Template file')
@click.option('-i','--input',type=click.File('r'),
              help='Input JSON index file')
@click.pass_context
def rates_chart_data(ctx, category, output, template, input):
    '''
    Produce rates chart JSON data file from cfg and index JSON
    '''
    meth = getattr(cege.rates, category)
    outdat = meth(cege.io.load(template), cege.io.load(input))
    cege.io.save(outdat, output)


@cli.command('board-usage')
@click.option('-o','--output',type=click.File('wb'),
              help='Output JSON chart filename')
@click.option('-t','--template',type=click.File('r'),
              help='Template file')
@click.option('-i','--input',type=click.File('r'),
              help='Input JSON index file')
@click.pass_context
def board_usage(ctx, output, template, input):
    '''
    Produce board usage JSON data file from cfg and index JSON.
    '''
    outdat = cege.rates.board_usage(cege.io.load(template), cege.io.load(input))
    cege.io.save(outdat, output)

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
    if not category:
        category = cege.raw.guess_category(paramsfile)

    params = cege.io.load(open(paramsfile, 'r'))
    summary = cege.raw.summarize_params(category, **params)
    cege.io.save(summary, output)

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
    summary = cege.raw.summarize(paramsfile, category)
    cege.io.save(summary, output)

@cli.command('fix')
@click.option('-o','--output',type=click.File('wb'), default='-',
              help='Output file for summary JSON')
@click.argument('jsonfile', type=click.Path())
@click.pass_context
def fix(ctx, output, jsonfile):
    '''
    Fix known gross formatting errors in JSON files
    '''
    summary = cege.io.load(open(jsonfile,'r'))
    cege.io.save(summary, output)




def main():
    cli(obj=dict())

    
