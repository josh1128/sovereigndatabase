from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# 1) Replace regional extents and heights.
old = '''    REGION_BOUNDS = {\n        'World': None,\n        'Africa': dict(lon=(-20,55),lat=(-36,38)),\n        'Asia': dict(lon=(25,180),lat=(-12,78)),\n        'Europe': dict(lon=(-15, 68), lat=(28, 72)),\n        'North America': dict(lon=(-130,-55),lat=(5,55)),\n        'South America': dict(lon=(-83,-32),lat=(-58,14)),\n    }\n\n    REGION_HEIGHTS = {'World':650,'Africa':980,'Asia':880,'Europe':900,'North America':900,'South America':980}\n'''
new = '''    REGION_BOUNDS = {\n        'World': None,\n        'Africa': dict(lon=(-20,55),lat=(-36,38)),\n        'Asia': dict(lon=(25,180),lat=(-12,78)),\n        'Europe': dict(lon=(-15, 68), lat=(28, 72)),\n\n        # Canada and the United States. Mexico, Central America and the\n        # Caribbean are included in the combined Latin America extract below.\n        'North America': dict(lon=(-170,-50),lat=(24,82)),\n\n        # Mexico + Central America + Caribbean + South America.\n        'Latin America & Caribbean': dict(lon=(-118,-32),lat=(-58,33)),\n    }\n\n    REGION_HEIGHTS = {\n        'World':650,\n        'Africa':980,\n        'Asia':880,\n        'Europe':900,\n        'North America':900,\n        'Latin America & Caribbean':980,\n    }\n'''
if old not in s:
    raise SystemExit('Could not find REGION_BOUNDS / REGION_HEIGHTS block')
s = s.replace(old, new, 1)

# 2) Replace region membership and classification.
old = '''    REGION_OVERRIDES = {\n        'Europe': {'GBR','IRL','ISL','PRT','ESP','FRA','BEL','NLD','LUX','DEU','CHE','AUT','ITA','MLT','DNK','NOR','SWE','FIN','EST','LVA','LTU','POL','CZE','SVK','HUN','SVN','HRV','BIH','SRB','MNE','MKD','ALB','GRC','BGR','ROU','MDA','UKR','BLR'},\n        'Asia': {'RUS','TUR','GEO','ARM','AZE','CYP','KAZ'},\n        'North America': {'CAN','USA','MEX','BLZ','GTM','HND','SLV','NIC','CRI','PAN','BHS','CUB','JAM','HTI','DOM','PRI','ABW','AIA','ATG','BRB','CUW','DMA','GRD','KNA','LCA','SXM','TTO','VCT'},\n        'South America': {'ARG','BOL','BRA','CHL','COL','ECU','GUY','PRY','PER','SUR','URY','VEN'},\n    }\n\n    def country_region(code,lat,lon):\n        for rg in ['Europe','Asia','North America','South America']:\n            if code in REGION_OVERRIDES.get(rg,set()):\n                return rg\n        for rg in ['Africa','South America','North America','Europe','Asia']:\n            b = REGION_BOUNDS[rg]\n            if b['lon'][0] <= lon <= b['lon'][1] and b['lat'][0] <= lat <= b['lat'][1]:\n                return rg\n        return 'Other'\n'''
new = '''    REGION_OVERRIDES = {\n        'Europe': {'GBR','IRL','ISL','PRT','ESP','FRA','BEL','NLD','LUX','DEU','CHE','AUT','ITA','MLT','DNK','NOR','SWE','FIN','EST','LVA','LTU','POL','CZE','SVK','HUN','SVN','HRV','BIH','SRB','MNE','MKD','ALB','GRC','BGR','ROU','MDA','UKR','BLR'},\n        'Asia': {'RUS','TUR','GEO','ARM','AZE','CYP','KAZ'},\n\n        # North America is kept as the Canada / United States extract.\n        'North America': {'CAN','USA'},\n\n        # Combined Mexico, Central America, Caribbean and South America extract.\n        'Latin America & Caribbean': {\n            'MEX',\n            'BLZ','GTM','HND','SLV','NIC','CRI','PAN',\n            'BHS','CUB','JAM','HTI','DOM','PRI','ABW','AIA','ATG','BRB','CUW',\n            'DMA','GRD','KNA','LCA','SXM','TTO','VCT',\n            'ARG','BOL','BRA','CHL','COL','ECU','GUY','PRY','PER','SUR','URY','VEN',\n        },\n    }\n\n    def country_region(code,lat,lon):\n        # Explicit membership takes priority where regional bounding boxes overlap.\n        for rg in ['Europe','Asia','Latin America & Caribbean','North America']:\n            if code in REGION_OVERRIDES.get(rg,set()):\n                return rg\n\n        for rg in ['Africa','Latin America & Caribbean','North America','Europe','Asia']:\n            b = REGION_BOUNDS[rg]\n            if b['lon'][0] <= lon <= b['lon'][1] and b['lat'][0] <= lat <= b['lat'][1]:\n                return rg\n        return 'Other'\n'''
if old not in s:
    raise SystemExit('Could not find REGION_OVERRIDES / country_region block')
s = s.replace(old, new, 1)

# 3) Update the unused-but-kept reference title mapping for consistency.
s = s.replace(
    "        'North America': 'Figure A-4: Debt in default, North America and the Caribbean',\n        'South America': 'Figure A-5: Debt in default, Latin America',",
    "        'North America': 'Figure A-4: Debt in default, North America',\n        'Latin America & Caribbean': 'Figure A-5: Debt in default, Latin America and the Caribbean',",
    1,
)

# 4) Merge map label offsets for Central America, Caribbean and South America.
old = '''        'North America': {'BLZ':(-1.0,0.8),'GTM':(-1.0,0.3),'HND':(0.8,0.9),'SLV':(-1.5,-0.6),'NIC':(0.9,-0.3),'CRI':(-0.8,-0.8),'PAN':(1.2,-0.7),'CUB':(0.0,1.2),'JAM':(0.0,-1.0),'HTI':(-0.8,0.8),'DOM':(1.0,0.4)},\n        'South America': {'URY':(1.3,-0.5),'PRY':(1.0,0.8),'ECU':(-1.0,0.5),'GUY':(1.0,0.7),'SUR':(1.0,-0.5)},\n'''
new = '''        'North America': {},\n        'Latin America & Caribbean': {\n            'BLZ':(-1.0,0.8),'GTM':(-1.0,0.3),'HND':(0.8,0.9),\n            'SLV':(-1.5,-0.6),'NIC':(0.9,-0.3),'CRI':(-0.8,-0.8),'PAN':(1.2,-0.7),\n            'CUB':(0.0,1.2),'JAM':(0.0,-1.0),'HTI':(-0.8,0.8),'DOM':(1.0,0.4),\n            'TTO':(1.0,-0.5),\n            'URY':(1.3,-0.5),'PRY':(1.0,0.8),'ECU':(-1.0,0.5),\n            'GUY':(1.0,0.7),'SUR':(1.0,-0.5),\n        },\n'''
if old not in s:
    raise SystemExit('Could not find Americas LABEL_OFFSETS block')
s = s.replace(old, new, 1)

# 5) Replace label policies for the combined region.
old = '''    REGION_LABEL_SIZE = {'World':10,'Africa':12,'Asia':11,'Europe':10,'North America':11,'South America':12}\n    REGION_HIDE_LABELS = {'North America': {'ABW','AIA','ATG','BHS','BRB','CUW','DMA','GRD','KNA','LCA','PRI','SXM','TTO','VCT'}, 'South America': set()}\n    REGION_ANCHOR_LABELS = {'North America': {'CAN','USA','MEX'}, 'South America': {'BRA','ARG','CHL','COL','PER'}, 'Europe': {'GBR','FRA','DEU','ESP','ITA'}, 'Africa': {'ZAF','NGA','EGY','DZA','ETH'}, 'Asia': {'CHN','IND','JPN','IDN','SAU'}}\n    REGION_MAX_LABELS = {'North America':14,'South America':12,'Europe':18,'Africa':22,'Asia':18}\n'''
new = '''    REGION_LABEL_SIZE = {\n        'World':10,\n        'Africa':12,\n        'Asia':11,\n        'Europe':10,\n        'North America':12,\n        'Latin America & Caribbean':11,\n    }\n\n    REGION_HIDE_LABELS = {\n        'North America': set(),\n        'Latin America & Caribbean': {\n            # Keep tiny island polygons/hover data but suppress overlapping text.\n            'ABW','AIA','ATG','BHS','BRB','CUW','DMA','GRD','KNA','LCA','PRI','SXM','VCT'\n        },\n    }\n\n    REGION_ANCHOR_LABELS = {\n        'North America': {'CAN','USA'},\n        'Latin America & Caribbean': {'MEX','CUB','BRA','ARG','CHL','COL','PER'},\n        'Europe': {'GBR','FRA','DEU','ESP','ITA'},\n        'Africa': {'ZAF','NGA','EGY','DZA','ETH'},\n        'Asia': {'CHN','IND','JPN','IDN','SAU'},\n    }\n\n    REGION_MAX_LABELS = {\n        'North America':6,\n        'Latin America & Caribbean':20,\n        'Europe':18,\n        'Africa':22,\n        'Asia':18,\n    }\n'''
if old not in s:
    raise SystemExit('Could not find region label policy block')
s = s.replace(old, new, 1)

# 6) Make the generated export filename clean when the region contains '&'.
old = '''    show_chart(fig_map,f"debt_default_map_{region.lower().replace(' ','_')}_{map_year}.html","cmap")\n'''
new = '''    map_region_slug = region.lower().replace('&', 'and').replace(' ', '_')\n    show_chart(fig_map,f"debt_default_map_{map_region_slug}_{map_year}.html","cmap")\n'''
if old not in s:
    raise SystemExit('Could not find map show_chart filename line')
s = s.replace(old, new, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Combined Latin America & Caribbean map applied; syntax check passed.')
