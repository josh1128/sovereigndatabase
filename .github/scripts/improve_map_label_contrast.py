from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# 1) Take the World-map continent labels down one notch on screen.
old = "            textfont=dict(color='#2f2f2f',size=18,family='Arial Black'),\n"
new = "            textfont=dict(color='#2f2f2f',size=16,family='Arial Black'),\n"
if old not in s:
    raise SystemExit('World continent textfont line not found')
s = s.replace(old, new, 1)

# 2) Define the bands that need light text before map-label rendering.
needle = '''        if pd.notna(row['value']) and row['value'] >= 10000:\n            return f"<b>{name}</b><br>${row['value']/1e3:,.1f}B"\n        return name\n\n    if region == 'World':\n'''
replacement = '''        if pd.notna(row['value']) and row['value'] >= 10000:\n            return f"<b>{name}</b><br>${row['value']/1e3:,.1f}B"\n        return name\n\n    # Use light, bold labels on the darker red debt bands. Dark labels remain\n    # clearer on no-default, yellow, and orange countries. This contrast rule\n    # is shared by all regional extracts and carries through to PNG exports.\n    DARK_LABEL_BANDS = {\n        '10,000 - 25,000',\n        '25,000 - 50,000',\n        '50,000+',\n    }\n\n    if region == 'World':\n'''
if needle not in s:
    raise SystemExit('Could not insert DARK_LABEL_BANDS')
s = s.replace(needle, replacement, 1)

# 3) Europe uses a curated label layer. Split it into light/dark text traces so
# labels remain readable regardless of the country's debt-band fill.
old = '''        europe_label_df = pd.DataFrame(europe_labels)\n\n        fig_map.add_trace(go.Scattergeo(\n            lon=europe_label_df['lon'],\n            lat=europe_label_df['lat'],\n            text=europe_label_df['text'],\n            mode='text',\n            showlegend=False,\n            hoverinfo='skip',\n            textfont=dict(\n                color='#2b2b2b',\n                size=9,\n                family='Arial'\n            )\n        ))\n\n'''
new = '''        europe_label_df = pd.DataFrame(europe_labels)\n        europe_band_lookup = dict(zip(view_df['code'], view_df['band']))\n        europe_label_df['band'] = europe_label_df['code'].map(europe_band_lookup)\n        europe_label_df['light_text'] = europe_label_df['band'].isin(DARK_LABEL_BANDS)\n\n        for light_text, text_color, font_family in [\n            (False, '#222222', 'Arial'),\n            (True, '#ffffff', 'Arial Black'),\n        ]:\n            europe_part = europe_label_df[europe_label_df['light_text'] == light_text]\n            if europe_part.empty:\n                continue\n            fig_map.add_trace(go.Scattergeo(\n                lon=europe_part['lon'],\n                lat=europe_part['lat'],\n                text=europe_part['text'],\n                mode='text',\n                showlegend=False,\n                hoverinfo='skip',\n                textfont=dict(\n                    color=text_color,\n                    size=9,\n                    family=font_family,\n                )\n            ))\n\n'''
if old not in s:
    raise SystemExit('Europe label trace block not found')
s = s.replace(old, new, 1)

# 4) Apply the same automatic contrast rule to every other regional extract.
old = '''        label_df['map_text'] = label_df.apply(format_country_label,axis=1)\n        if not label_df.empty:\n            fig_map.add_trace(go.Scattergeo(lon=label_df['plot_lon'],lat=label_df['plot_lat'],text=label_df['map_text'],mode='text',showlegend=False,hoverinfo='skip',textfont=dict(color='#333333',size=REGION_LABEL_SIZE.get(region,11),family='Arial')))\n\n'''
new = '''        label_df['map_text'] = label_df.apply(format_country_label,axis=1)\n        label_df['light_text'] = label_df['band'].isin(DARK_LABEL_BANDS)\n        if not label_df.empty:\n            for light_text, text_color, font_family in [\n                (False, '#222222', 'Arial'),\n                (True, '#ffffff', 'Arial Black'),\n            ]:\n                label_part = label_df[label_df['light_text'] == light_text]\n                if label_part.empty:\n                    continue\n                fig_map.add_trace(go.Scattergeo(\n                    lon=label_part['plot_lon'],\n                    lat=label_part['plot_lat'],\n                    text=label_part['map_text'],\n                    mode='text',\n                    showlegend=False,\n                    hoverinfo='skip',\n                    textfont=dict(\n                        color=text_color,\n                        size=REGION_LABEL_SIZE.get(region,11),\n                        family=font_family,\n                    )\n                ))\n\n'''
if old not in s:
    raise SystemExit('Generic regional label trace block not found')
s = s.replace(old, new, 1)

# 5) The World PNG labels were deliberately enlarged earlier. Bring only the
# World export down one notch; regional export text stays large and readable.
old = '''                        if is_world_export:\n                            new_size = max(28, int(round(float(current_size) * 1.55)))\n                        else:\n                            new_size = max(17, int(round(float(current_size) * 1.65)))\n'''
new = '''                        if is_world_export:\n                            new_size = max(24, int(round(float(current_size) * 1.45)))\n                        else:\n                            new_size = max(17, int(round(float(current_size) * 1.65)))\n'''
if old not in s:
    raise SystemExit('PNG typography boost block not found')
s = s.replace(old, new, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Map label contrast and World font sizing updated; syntax check passed.')
