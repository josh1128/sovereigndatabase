from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# Middle East countries should be visible in the Asia-Pacific extract even when
# their centroids are captured by the broad Europe/Africa regional bounds.
# This is a view-only inclusion: it does not remove those countries from their
# existing Europe/Africa classifications.
old = """    map_df = pd.DataFrame(rows)\n    view_df = map_df.copy() if region == 'World' else map_df[map_df['region'] == region].copy()\n    positive = view_df[view_df['value'].fillna(0) > 0].copy().sort_values(['value','country'],ascending=[False,True])\n"""
new = """    map_df = pd.DataFrame(rows)\n\n    MIDDLE_EAST_CODES = {\n        'TUR','CYP','EGY','IRN','IRQ','SYR','LBN','ISR','PSE','JOR',\n        'SAU','YEM','OMN','ARE','KWT','QAT','BHR',\n    }\n\n    if region == 'World':\n        view_df = map_df.copy()\n    elif region == 'Asia':\n        # Include Middle East sovereigns explicitly in Asia-Pacific. Several of\n        # their centroids overlap the broad Europe/Africa bounds, so relying only\n        # on country_region() can incorrectly drop them from this choropleth.\n        view_df = map_df[\n            (map_df['region'] == 'Asia') | map_df['code'].isin(MIDDLE_EAST_CODES)\n        ].copy()\n    else:\n        view_df = map_df[map_df['region'] == region].copy()\n\n    positive = view_df[view_df['value'].fillna(0) > 0].copy().sort_values(['value','country'],ascending=[False,True])\n"""
if old not in s:
    raise SystemExit('view_df construction block not found')
s = s.replace(old, new, 1)

# Keep all Middle East labels suppressed in the Asia-Pacific map. Their polygons
# still receive the shared six-category legend colours and retain hover/table data.
old = """            'TUR','CYP','GEO','ARM','AZE',\n            'IRN','IRQ','SYR','LBN','ISR','PSE','JOR',\n            'SAU','YEM','OMN','ARE','KWT','QAT','BHR',\n            'LAO','MMR','SGP','BRN'\n"""
new = """            'TUR','CYP','GEO','ARM','AZE',\n            'EGY','IRN','IRQ','SYR','LBN','ISR','PSE','JOR',\n            'SAU','YEM','OMN','ARE','KWT','QAT','BHR',\n            'LAO','MMR','SGP','BRN'\n"""
if old not in s:
    raise SystemExit('Asia hidden-label block not found')
s = s.replace(old, new, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Middle East sovereigns explicitly included in Asia-Pacific choropleth; syntax check passed.')
