from pathlib import Path
p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')
old = "            if float(row['value'] or 0) <= 0:\n                continue\n"
new = "            if pd.isna(row['value']) or float(row['value']) <= 0:\n                continue\n"
if old not in s:
    raise SystemExit('LATAM callout value guard not found')
s = s.replace(old, new, 1)
compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('LATAM callout value guard fixed; syntax check passed.')
