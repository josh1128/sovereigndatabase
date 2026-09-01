from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# 1) Remove the custom Middle East outline, header, and arrow/value callouts.
# Middle East countries remain in the Asia regional dataframe and therefore
# keep their existing choropleth fill based on the shared six-category legend.
start_marker = "    if region == 'Asia':\n        MIDDLE_EAST_NAMES = {\n"
end_marker = "    if region == 'Latin America & Caribbean':\n"
start = s.find(start_marker)
if start == -1:
    raise SystemExit('Middle East custom block not found')
end = s.find(end_marker, start)
if end == -1:
    raise SystemExit('LATAM block not found after Middle East block')
s = s[:start] + s[end:]

# 2) De-clutter mainland Southeast Asia. Laos and Myanmar/Burma remain fully
# represented by polygon colour, hover information, and the table; only their
# printed country-name/default labels are suppressed.
old = """            'SAU','YEM','OMN','ARE','KWT','QAT','BHR',\n            'SGP','BRN'\n"""
new = """            'SAU','YEM','OMN','ARE','KWT','QAT','BHR',\n            'LAO','MMR','SGP','BRN'\n"""
if old not in s:
    raise SystemExit('Asia hidden-label tail not found')
s = s.replace(old, new, 1)

# 3) Remove stale Middle East-specific export handling if any remains.
if 'middle_east_text' in s or 'MIDDLE_EAST_CALLOUTS' in s or 'middle_east_outline_lon' in s:
    raise SystemExit('Stale Middle East custom-rendering code remains')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Asia map simplified; syntax check passed.')
