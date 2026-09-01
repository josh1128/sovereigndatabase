from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

old = """    if region == 'World':\n        view_df = map_df.copy()\n    elif region == 'Asia':\n        # Include Middle East sovereigns explicitly in Asia-Pacific. Several of\n        # their centroids overlap the broad Europe/Africa bounds, so relying only\n        # on country_region() can incorrectly drop them from this choropleth.\n        view_df = map_df[\n            (map_df['region'] == 'Asia') | map_df['code'].isin(MIDDLE_EAST_CODES)\n        ].copy()\n    else:\n        view_df = map_df[map_df['region'] == region].copy()\n"""

new = """    if region == 'World':\n        view_df = map_df.copy()\n    elif region == 'Asia':\n        # Include Middle East sovereigns explicitly in Asia-Pacific. Several of\n        # their centroids overlap the broad Europe/Africa bounds, so relying only\n        # on country_region() can incorrectly drop them from this choropleth.\n        view_df = map_df[\n            (map_df['region'] == 'Asia') | map_df['code'].isin(MIDDLE_EAST_CODES)\n        ].copy()\n    elif region == 'Europe':\n        # Russia remains classified with Asia for the Asia-Pacific extract, but\n        # also include it in Europe so its polygon uses the selected year's\n        # shared six-category debt-default colour there as well.\n        view_df = map_df[\n            (map_df['region'] == 'Europe') | (map_df['code'] == 'RUS')\n        ].copy()\n    else:\n        view_df = map_df[map_df['region'] == region].copy()\n"""

if old not in s:
    raise SystemExit('Regional view construction block not found')

s = s.replace(old, new, 1)

if "elif region == 'Europe':" not in s or "map_df['code'] == 'RUS'" not in s:
    raise SystemExit('Russia Europe inclusion was not inserted')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Russia included in Europe choropleth; syntax check passed.')
