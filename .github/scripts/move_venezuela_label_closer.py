from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

old = """                label_lon=-51.0, label_lat=12.0,\n                line_lon=-62.8, line_lat=7.5,\n"""
new = """                label_lon=-58.5, label_lat=13.2,\n                line_lon=-62.2, line_lat=8.2,\n"""

if new in s:
    print('Venezuela label already moved closer; no change needed.')
elif old in s:
    s = s.replace(old, new, 1)
else:
    raise SystemExit('Current Venezuela callout coordinates not found')

if s.count("label_lon=-58.5, label_lat=13.2") != 1:
    raise SystemExit('Expected exactly one closer Venezuela label position')
if s.count("line_lon=-62.2, line_lat=8.2") != 1:
    raise SystemExit('Expected exactly one Venezuela pointer position')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Venezuela label moved closer to arrow; syntax check passed.')
