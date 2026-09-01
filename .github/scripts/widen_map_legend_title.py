from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

old_title = '''legend_title = (\n    f"<b>{map_year} total debt in default<br>by country<br>(US$ millions)</b>"\n)\n'''
new_title = '''legend_title = (\n    f"<b>{map_year} total debt in default<br>by country (US$ millions)</b>"\n)\n'''

if old_title in s:
    s = s.replace(old_title, new_title, 1)
elif new_title not in s:
    raise SystemExit('Legend title block not found')

# Widen the live legend so the full title line and category labels fit comfortably.
old_live = "        itemwidth=52,\n"
new_live = "        itemwidth=78,\n"
if old_live in s:
    s = s.replace(old_live, new_live, 1)
elif new_live not in s:
    raise SystemExit('Live legend itemwidth not found')

# Keep exported PNG legends equally roomy.
old_export = "                            itemwidth=58,\n"
new_export = "                            itemwidth=82,\n"
if old_export in s:
    s = s.replace(old_export, new_export, 1)
elif new_export not in s:
    raise SystemExit('Export legend itemwidth not found')

if "by country (US$ millions)</b>" not in s:
    raise SystemExit('Updated legend title missing')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Legend title widened and US$ millions moved after country; syntax check passed.')
