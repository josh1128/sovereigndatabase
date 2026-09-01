from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# Remove the extra em-space padding around each legend range label.
old_name = '        name=f"\\u2002{lab}\\u2002",\n'
new_name = '        name=lab,\n'
if old_name in s:
    s = s.replace(old_name, new_name, 1)
elif new_name not in s:
    raise SystemExit('Legend label padding line not found')

# Plotly legend itemwidth has a minimum of 30 px. Use that minimum so the
# numeric US$ millions ranges sit as far left as possible next to the swatch.
old_live = '        itemwidth=44,\n'
new_live = '        itemwidth=30,\n'
if old_live in s:
    s = s.replace(old_live, new_live, 1)
elif new_live not in s:
    raise SystemExit('Live legend itemwidth not found')

old_export = '                            itemwidth=48,\n'
new_export = '                            itemwidth=30,\n'
if old_export in s:
    s = s.replace(old_export, new_export, 1)
elif new_export not in s:
    raise SystemExit('Export legend itemwidth not found')

if 'name=f"\\u2002{lab}\\u2002"' in s:
    raise SystemExit('Old padded legend labels still present')
if s.count('itemwidth=30,') < 2:
    raise SystemExit('Expected minimum itemwidth on live and export legends')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Legend values moved to minimum left indent; syntax check passed.')
