#!/usr/bin/env python3
"""Refresh published ACS 5-year housing estimates; never replace good data on failure."""
import json, pathlib, urllib.parse, urllib.request, datetime
TOWNS={'Horseshoe Bay','Marble Falls','Burnet','Kingsland','Granite Shoals','Llano','Bertram','Cottonwood Shores','Meadowlakes'}
variables='NAME,B25077_001E,B25001_001E,B25003_002E,B25002_003E'
def valid(value):
    try:
        n=int(value)
        return n if n>=0 else None
    except (TypeError,ValueError):
        return None
for year in (2024,2023):
    query=urllib.parse.urlencode({'get':variables,'for':'place:*','in':'state:48'})
    url=f'https://api.census.gov/data/{year}/acs/acs5?{query}'
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'HighlandLakesLive/1.0 housing-data'})
        with urllib.request.urlopen(req,timeout=35) as resp: rows=json.load(resp)
        headers=rows.pop(0)
        found={}
        for row in rows:
            item=dict(zip(headers,row))
            name=item['NAME'].split(',')[0]
            for suffix in (' city',' town',' village',' CDP'):
                if name.endswith(suffix): name=name[:-len(suffix)]
            if name in TOWNS:
                found[name]={'value':valid(item['B25077_001E']),'units':valid(item['B25001_001E']),'owners':valid(item['B25003_002E']),'vacant':valid(item['B25002_003E'])}
        if len(found)<5: raise ValueError('Too few matching communities: '+str(len(found)))
        output={'source':'U.S. Census Bureau ACS 5-year estimates','year':year,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'communities':found}
        pathlib.Path('data').mkdir(exist_ok=True)
        pathlib.Path('data/housing-acs.json').write_text(json.dumps(output,indent=2)+'\n')
        print('Updated',len(found),'communities for',year)
        break
    except Exception as exc:
        print('Failed year',year,repr(exc))
else:
    raise SystemExit('No verified ACS data available; leaving prior snapshot untouched')
