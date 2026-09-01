from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# Pull the numeric US$ millions range labels closer to the left by reducing
# the symbol/text spacing. Keep the legend box itself and title unchanged.
old_live = "        itemwidth=78,\n"
new_live = "        itemwidth=44,\n"
if old_live in s:
    s = s.replace(old_live, new_live, 1)
elif new_live not in s:
    raise SystemExit('Live legend itemwidth not found')

old_export = "                            itemwidth=82,\n"
new_export = "                            itemwidth=48,\n"
if old_export in s:
    s = s.replace(old_export, new_export, 1)
elif new_export not in s:
    raise SystemExit('Export legend itemwidth not found')

if "by country (US$ millions)</b>" not in s:
    raise SystemExit('Legend title unexpectedly changed')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Legend US$ millions values shifted left; syntax check passed.')
