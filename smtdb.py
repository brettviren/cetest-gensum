#!/usr/bin/env python
'''
export PGSSLCERT=~/.postgresql/${hostname}_${user}.crt
export PGSSLKEY=~/.postgresql/${hostname}_${user}.key
export PGSSLMODE=require
export PGUSER=cetester_${user}
export PGDATABASE=cetest_oper
export PGHOST=hothstor2.phy.bnl.gov
'''

import os
import psycopg2
from collections import defaultdict

connstr = "dbname='{PGDATABASE}' user='{PGUSER}' host='{PGHOST}' "
connstr+= "sslcert='{PGSSLCERT}' sslkey='{PGSSLKEY}'"
connstr = connstr.format(**os.environ)
conn = psycopg2.connect(connstr)

def slurp_adc_labels():
    select="""
SELECT
django_store_record.label,
(django_store_parameterset.content::json)->'timestamp'
FROM
django_store_parameterset, django_store_record
WHERE
(django_store_parameterset.content::json)->'timestamp' is not null 
AND 
(django_store_parameterset.content::json)->'smtname' is not null 
AND
django_store_parameterset.id = django_store_record.parameters_id 
AND
CAST(django_store_parameterset.content AS JSON)->>'smtname' = 'adc';
"""
    cur = conn.cursor()    
    cur.execute(select)
    rows = cur.fetchall()
    ret = dict()
    for lab,ts in rows:
        ret[ts] = lab
    return ret

def slurp_fe_labels():
    select="""
SELECT
django_store_record.label,
(django_store_parameterset.content::json)->'session_start_time'
FROM
django_store_parameterset, django_store_record
WHERE
(django_store_parameterset.content::json)->'session_start_time' is not null 
AND 
(django_store_parameterset.content::json)->'smtname' is not null 
AND
django_store_parameterset.id = django_store_record.parameters_id 
AND
CAST(django_store_parameterset.content AS JSON)->>'smtname' = 'feasic';
"""
    cur = conn.cursor()    
    cur.execute(select)
    rows = cur.fetchall()
    ret = dict()
    for lab,ts in rows:
        ret[ts] = lab
    return ret

def slurp_labels():
    '''
    Return a lookup from  Sumatra labels for data sets with matching params
    '''
    cur = conn.cursor()
    select = """
SELECT
django_store_record.label,
(django_store_parameterset.content::json)->'session_start_time',
(django_store_parameterset.content::json)->'test_category',
(django_store_parameterset.content::json)->'datasubdir'
FROM
django_store_parameterset, django_store_record
WHERE 
(django_store_parameterset.content::json)->'session_start_time' is not null 
AND 
(django_store_parameterset.content::json->'test_category') is not null 
AND
django_store_parameterset.id = django_store_record.parameters_id
;"""
    cur.execute(select)
    rows = cur.fetchall()
    ret = defaultdict(lambda : defaultdict(dict))
    for lab,ts,cat,dsd in rows:
        ret[cat][ts][dsd] = lab
    return ret


slurp_labels()
# get_labels(session_start_time="20170602T173309", test_category="feasic")

# id from django_store_parameterset where content::jsonb @> '{"session_start_time":"%s"}'""" % "20170602T173309"
#django_store_parameterset.content,
#django_store_parameterset.id,
