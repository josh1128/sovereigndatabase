from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

old = "x=0.03 if is_world_geo else 0.06"
new = "x=0.015 if is_world_geo else 0.035"
if old in s:
    s = s.replace(old, new)

old = "x=0.03 if is_world_export else 0.06"
new = "x=0.015 if is_world_export else 0.035"
if old in s:
    s = s.replace(old, new)

old = "x=0.03 if is_world else 0.06"
new = "x=0.015 if is_world else 0.035"
if old in s:
    s = s.replace(old, new)

for expected in [
    "x=0.015 if is_world_geo else 0.035",
    "x=0.015 if is_world_export else 0.035",
    "x=0.015 if is_world else 0.035",
]:
    if expected not in s:
        raise SystemExit(f'Missing expected left-indented legend position: {expected}')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Map legend shifted left on live and exported maps; syntax check passed.')
