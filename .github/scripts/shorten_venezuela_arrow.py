from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

old = """                line_lon=-56.0, line_lat=9.5,\n"""
new = """                line_lon=-62.8, line_lat=7.5,\n"""

if new in s:
    print('Venezuela arrow already shortened; no change needed.')
elif old in s:
    s = s.replace(old, new, 1)
else:
    raise SystemExit('Current Venezuela connector coordinates not found')

if s.count("line_lon=-62.8, line_lat=7.5") != 1:
    raise SystemExit('Expected exactly one shortened Venezuela connector')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Venezuela arrow shortened; syntax check passed.')
