from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# 1) Remove Middle East country names/default amounts from the Asia-Pacific
# printed label layer. Polygons, colors, hover, legend, and table data remain.
old = """        'Asia': {\n            # Tiny, dense labels remain available via hover/table but are omitted\n            # from the printed label layer to keep Asia-Pacific readable.\n            'PSE','QAT','BHR','SGP','BRN'\n        },\n"""
new = """        'Asia': {\n            # Keep Asia-Pacific focused on APAC. Middle East polygons/default\n            # colors remain visible where they intersect the crop, but their\n            # names and inline default amounts are suppressed. Tiny APAC labels\n            # below are also omitted to prevent crowding.\n            'TUR','CYP','GEO','ARM','AZE',\n            'IRN','IRQ','SYR','LBN','ISR','PSE','JOR',\n            'SAU','YEM','OMN','ARE','KWT','QAT','BHR',\n            'SGP','BRN'\n        },\n"""
if old not in s:
    raise SystemExit('Asia REGION_HIDE_LABELS block not found')
s = s.replace(old, new, 1)

# Saudi Arabia must not be reintroduced as an anchor label.
old = "        'Asia': {'CHN','IND','JPN','IDN','SAU'},\n"
new = "        'Asia': {'CHN','IND','JPN','IDN'},\n"
if old not in s:
    raise SystemExit('Asia anchor labels line not found')
s = s.replace(old, new, 1)

# 2) Add selected-year default amounts to Ukraine and Belarus in Europe.
# Keep the amount on its own bold line and use B/M formatting consistently.
old = """            europe_labels.append({\n                'code': code,\n                'text': f\"<b>{EUROPE_LABEL_NAMES.get(code, code)}</b>\",\n                'lon': plot_lon,\n                'lat': plot_lat,\n            })\n"""
new = """            label_text = f\"<b>{EUROPE_LABEL_NAMES.get(code, code)}</b>\"\n            if code in {'UKR', 'BLR'}:\n                value_match = view_df.loc[view_df['code'] == code, 'value']\n                if not value_match.empty and pd.notna(value_match.iloc[0]) and float(value_match.iloc[0]) > 0:\n                    default_value = float(value_match.iloc[0])\n                    if default_value >= 1000:\n                        value_text = f\"${default_value/1e3:,.1f}B\"\n                    else:\n                        value_text = f\"${default_value:,.0f}M\"\n                    label_text += f\"<br><b>{value_text}</b>\"\n\n            europe_labels.append({\n                'code': code,\n                'text': label_text,\n                'lon': plot_lon,\n                'lat': plot_lat,\n            })\n"""
if old not in s:
    raise SystemExit('Europe label append block not found')
s = s.replace(old, new, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Ukraine/Belarus values added and Middle East labels removed; syntax check passed.')
