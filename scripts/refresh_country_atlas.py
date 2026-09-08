#!/usr/bin/env python3
"""Refresh canonical country records from authoritative international data.

The website reads data/countries/<country-id>.json directly through the unified
index. External APIs are acquisition inputs only; a failed or incomplete refresh
never replaces a usable country record with an empty snapshot.
"""
from __future__ import annotations
import json, os, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX=os.path.join(ROOT,'data','countries','index.json')
OUT=os.path.join(ROOT,'data','countries')
EXPECTED=195
INDICATORS={
 'population':'SP.POP.TOTL','gdp':'NY.GDP.MKTP.CD','gdp_per_capita':'NY.GDP.PCAP.CD',
 'gdp_per_capita_ppp':'NY.GDP.PCAP.PP.CD','real_growth':'NY.GDP.MKTP.KD.ZG',
 'inflation':'FP.CPI.TOTL.ZG','unemployment':'SL.UEM.TOTL.ZS',
 'labour_force_participation':'SL.TLF.CACT.ZS','life_expectancy':'SP.DYN.LE00.IN',
 'fertility':'SP.DYN.TFRT.IN','urbanization':'SP.URB.TOTL.IN.ZS','poverty':'SI.POV.NAHC',
 'co2_emissions':'EN.ATM.CO2E.PC','internet_penetration':'IT.NET.USER.ZS'}
GROUPS=[['population','gdp','gdp_per_capita','gdp_per_capita_ppp','real_growth'],['inflation','unemployment','labour_force_participation','life_expectancy','fertility'],['urbanization','poverty','co2_emissions','internet_penetration']]

def get_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'ThePotatoOfLife-country-atlas/3.0'})
    with urllib.request.urlopen(req,timeout=180) as response:return json.load(response)

def world_bank(fields):
    result={f:{} for f in fields}
    for field in fields:
        indicator=INDICATORS[field]; page=1
        while True:
            query=urllib.parse.urlencode({'format':'json','per_page':1000,'mrv':5,'page':page})
            payload=get_json(f'https://api.worldbank.org/v2/country/all/indicator/{urllib.parse.quote(indicator,safe="")}?{query}')
            if not isinstance(payload,list) or len(payload)<2 or not isinstance(payload[1],list):raise RuntimeError(f'World Bank returned malformed payload for {indicator}')
            if isinstance(payload[0],dict) and payload[0].get('message'):raise RuntimeError(f'World Bank rejected {indicator}: {payload[0]["message"]}')
            for row in payload[1]:
                iso=str(row.get('countryiso3code') or '').upper(); value=row.get('value'); year=str(row.get('date') or '')
                if not iso or value is None:continue
                old=result[field].get(iso)
                if old is None or year>str(old.get('year') or ''):result[field][iso]={'value':value,'year':int(year) if year.isdigit() else year,'source':'world-bank','indicator':indicator}
            pages=int(payload[0].get('pages') or 1)
            if page>=pages:break
            page+=1
    return result

def load(path):
    with open(path,encoding='utf-8') as f:return json.load(f)

def main():
    index=load(INDEX); countries=index.get('countries',[])
    if len(countries)!=EXPECTED:raise RuntimeError(f'Canonical country index must contain {EXPECTED} records; found {len(countries)}')
    ids=[c.get('id') for c in countries]; iso=[str(c.get('iso3') or '').upper() for c in countries]
    if len(set(ids))!=EXPECTED or len(set(iso))!=EXPECTED or '' in iso:raise RuntimeError('Canonical country index has duplicate or missing identities')
    by_field={f:{} for f in INDICATORS}
    requests=0
    for group in GROUPS:
        result=world_bank(group)
        for field,values in result.items():by_field[field].update(values)
        requests+=len(group)
    coverage={f:len(by_field[f]) for f in INDICATORS}
    minimum=max(150,int(EXPECTED*0.75))
    if coverage['population']<minimum or coverage['gdp']<minimum:raise RuntimeError(f'Refusing incomplete refresh: population={coverage["population"]}, gdp={coverage["gdp"]}, required_each>={minimum}')
    now=datetime.now(timezone.utc).isoformat(); observations_written=0; countries_written=0
    for country in countries:
        path=os.path.join(OUT,f'{country["id"]}.json')
        if not os.path.exists(path):raise RuntimeError(f'Missing canonical country record: {path}')
        record=load(path); record.setdefault('record_type','country'); record.setdefault('identity',{}); record['identity'].update({'id':country['id'],'name':country['name'],'iso2':country['iso2'],'iso3':country['iso3']})
        record.setdefault('observations',{}); record.setdefault('history',[]); record.setdefault('coverage',{}); record.setdefault('provenance',{})
        for field in INDICATORS:
            value=by_field[field].get(str(country['iso3']).upper())
            if not value:continue
            value=dict(value); value['retrieved_at']=now; value['confidence']='international-official'
            old=record['observations'].get(field)
            if isinstance(old,dict) and old.get('value')!=value.get('value'):record['history'].append({'field':field,'previous':old,'replaced_at':now,'reason':'new source observation'})
            record['observations'][field]=value; observations_written+=1
        record['coverage']['observations']=len(record['observations']); record['coverage']['sources']=max(record['coverage'].get('sources',0),1 if record['observations'] else 0)
        record['provenance']['last_refresh']=now; record['provenance']['source_priority']='international-official'; record['provenance']['historical_observations_preserved']=True
        with open(path,'w',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2); f.write('\n')
        countries_written+=1
    print(json.dumps({'updated_at':now,'countries_written':countries_written,'observations_written':observations_written,'bulk_indicator_requests':requests,'coverage':coverage,'source':'world-bank'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
