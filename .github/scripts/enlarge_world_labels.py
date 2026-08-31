from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

old = "textfont=dict(color='#2f2f2f',size=12,family='Arial')"
new = "textfont=dict(color='#2f2f2f',size=18,family='Arial Black')"

if old not in s:
    raise SystemExit('Could not find the current World-map textfont block.')

s = s.replace(old, new, 1)
compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('World-map continent labels enlarged and bolded; syntax check passed.')
