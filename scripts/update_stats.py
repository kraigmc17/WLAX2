#!/usr/bin/env python3
import json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'stats.json'
URL=os.getenv('PLAYER_URL','https://whitmanblues.com/sports/womens-lacrosse/roster/lola-mcconaghy/6312')
ALIASES={'gp':['GP','GAMES','GAMES PLAYED'],'gs':['GS','GAMES STARTED'],'g':['G','GOALS'],'a':['A','ASSISTS'],'pts':['PTS','POINTS'],'sh':['SH','SHOTS'],'shp':['SH%','SHOT%','SHOOTING %'],'sog':['SOG','SHOTS ON GOAL'],'sogp':['SOG%','SHOTS ON GOAL %'],'gb':['GB','GROUND BALLS'],'ct':['CT','CAUSED TURNOVERS'],'dc':['DC','DRAW CONTROLS'],'to':['TO','TURNOVERS']}

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def num(v):
    v=clean(v).replace('%','').replace(',','')
    if not v or v in {'-','--'}: return 0
    try: return float(v) if '.' in v else int(v)
    except ValueError: return 0

def semantic_tables(soup):
    out=[]
    for table in soup.select('table'):
        headers=[clean(x.get_text(' ',strip=True)).upper() for x in table.select('thead th')]
        if not headers:
            first=table.select_one('tr'); headers=[clean(x.get_text(' ',strip=True)).upper() for x in first.select('th,td')] if first else []
        rows=[]
        for tr in table.select('tbody tr') or table.select('tr')[1:]:
            cells=[clean(x.get_text(' ',strip=True)) for x in tr.select('th,td')]
            if cells: rows.append(cells)
        if headers and rows: out.append((headers,rows))
    return out

def row_to_stats(headers,row):
    hmap={h:i for i,h in enumerate(headers)}; result={}
    for key,names in ALIASES.items():
        idx=next((hmap[n] for n in names if n in hmap),None)
        if idx is not None and idx<len(row): result[key]=num(row[idx])
    return result

def season_from_context(table):
    txt=clean(table.parent.get_text(' ',strip=True))[:700]
    m=re.search(r'20\d{2}',txt); return m.group(0) if m else None

def parse(html, prior):
    soup=BeautifulSoup(html,'html.parser'); seasons={}; games=[]
    # Sidearm pages expose accessible tables. Find rows containing a season or player name.
    for table in soup.select('table'):
        headers=[clean(x.get_text(' ',strip=True)).upper() for x in table.select('thead th')]
        if not headers: continue
        for tr in table.select('tbody tr'):
            row=[clean(x.get_text(' ',strip=True)) for x in tr.select('th,td')]
            if not row: continue
            joined=' '.join(row)
            year=next(iter(re.findall(r'20\d{2}',joined)),None) or season_from_context(table)
            stats=row_to_stats(headers,row)
            if year and len(stats)>=4 and ('Lola' in joined or year in joined or len(table.select('tbody tr'))==1): seasons[year]=stats
            # Game log rows normally include a date/opponent and numeric stat columns.
            date=next(iter(re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun)\.?\s+\d{1,2},?\s+20\d{2}|\d{1,2}/\d{1,2}/20\d{2}',joined,re.I)),None)
            if date and len(stats)>=3:
                opponent=row[1] if len(row)>1 else 'Opponent'; games.append({'date':date,'opponent':opponent,**stats})
    # Conservative merge: never erase a completed season when the source is temporarily blank.
    merged=dict(prior.get('seasons',{}))
    for year,stats in seasons.items():
        base=dict(merged.get(year,{})); base.update(stats); merged[year]=base
    return merged, games or prior.get('games',[])

def validate(old,new):
    for year,stats in new.items():
        for k in ('gp','g','a','pts'):
            if stats.get(k,0)<0: raise ValueError(f'negative {year} {k}')
        if stats.get('pts',0) != stats.get('g',0)+stats.get('a',0): raise ValueError(f'points mismatch in {year}')
        # Published cumulative totals should not move backwards during an active season.
        if year in old and stats.get('gp',0)<old[year].get('gp',0): raise ValueError(f'games decreased in {year}')

def main():
    prior=json.loads(DATA.read_text())
    r=requests.get(URL,timeout=30,headers={'User-Agent':'LolaStatsDashboard/1.0 (+family personal dashboard)'})
    r.raise_for_status()
    seasons,games=parse(r.text,prior); validate(prior.get('seasons',{}),seasons)
    changed=seasons!=prior.get('seasons',{}) or games!=prior.get('games',[])
    prior.update({'source':URL,'lastUpdated':datetime.now(timezone.utc).isoformat(),'status':'updated' if changed else 'checked-no-change','seasons':seasons,'games':games})
    DATA.write_text(json.dumps(prior,indent=2,sort_keys=True)+'\n')
    print(f"{prior['status']}: {len(seasons)} seasons, {len(games)} games")
if __name__=='__main__': main()
