import json, importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'scripts'/'update_stats.py'; spec=importlib.util.spec_from_file_location('u',p); u=importlib.util.module_from_spec(spec); spec.loader.exec_module(u)
def test_parse_table():
 html='''<div><h2>2027 Season Statistics</h2><table><thead><tr><th>Player</th><th>GP</th><th>GS</th><th>G</th><th>A</th><th>PTS</th><th>SH</th><th>SH%</th><th>SOG</th><th>SOG%</th><th>GB</th><th>CT</th><th>DC</th><th>TO</th></tr></thead><tbody><tr><td>Lola McConaghy</td><td>2</td><td>2</td><td>6</td><td>1</td><td>7</td><td>10</td><td>60.0</td><td>8</td><td>80.0</td><td>4</td><td>3</td><td>2</td><td>5</td></tr></tbody></table></div>'''
 seasons,_=u.parse(html,{'seasons':{},'games':[]}); assert seasons['2027']['pts']==7; assert seasons['2027']['ct']==3
def test_validation():
 u.validate({}, {'2027':{'gp':1,'g':2,'a':1,'pts':3}})
