from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# Remove the old figure-title lookup. The map-only dashboard no longer renders
# figure headings, and leaving stale title metadata can surface as "undefined"
# in the client after the old chart-tab UI was removed.
old_titles = """FIGURE_TITLES = {\n    'World': 'Figure A-1: Global debt in default',\n    'Europe': 'Figure A-2: Debt in default, Europe',\n    'Asia': 'Figure A-3: Debt in default, Asia Pacific',\n    'North America': 'Figure A-4: Debt in default, North America',\n    'Latin America & Caribbean': 'Figure A-5: Debt in default, Latin America and the Caribbean',\n    'Africa': 'Figure A-6: Debt in default, Africa',\n}\n\n"""
if old_titles in s:
    s = s.replace(old_titles, '', 1)

# Give Plotly an explicit blank title rather than a null/undefined title object.
old_layout = """    geo=geo_kw,\n    title=None,\n    legend=dict(\n"""
new_layout = """    geo=geo_kw,\n    title=dict(text=''),\n    legend=dict(\n"""
if old_layout in s:
    s = s.replace(old_layout, new_layout, 1)
elif new_layout not in s:
    raise SystemExit('Map layout title block not found')

if 'FIGURE_TITLES = {' in s:
    raise SystemExit('Stale FIGURE_TITLES block still present')
if "title=dict(text='')" not in s:
    raise SystemExit('Explicit blank map title missing')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Undefined map title removed; syntax check passed.')
