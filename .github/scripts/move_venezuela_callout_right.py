from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

old = """            'VEN': dict(\n                label_lon=-76.5, label_lat=13.0, arrow='→',\n                marker_symbol='triangle-right'\n            ),\n"""
new = """            'VEN': dict(\n                # Put Venezuela's label in the open Atlantic to the east so it\n                # does not collide with Honduras/Nicaragua/Central America.\n                label_lon=-48.0, label_lat=13.5, arrow='←',\n                marker_symbol='triangle-left'\n            ),\n"""

if old not in s:
    raise SystemExit('Current Venezuela callout configuration not found')

s = s.replace(old, new, 1)

# Venezuela is now east/right of the target, so show the directional arrow on
# the left side of the label, matching the line direction back to the country.
old_text = """            if code == 'VEN':\n                callout_text = (\n                    f\"<b>{display_name} {spec['arrow']}</b>\"\n                    f\"<br><b>{value_text}</b>\"\n                )\n            else:\n"""
new_text = """            if code == 'VEN':\n                callout_text = (\n                    f\"<b>{spec['arrow']} {display_name}</b>\"\n                    f\"<br><b>{value_text}</b>\"\n                )\n            else:\n"""

if old_text not in s:
    raise SystemExit('Current Venezuela callout text block not found')

s = s.replace(old_text, new_text, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Venezuela callout moved east/right; syntax check passed.')
