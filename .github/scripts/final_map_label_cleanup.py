from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# 1) Africa: keep Iraq/Lebanon polygons and hover data, but suppress their
# printed names/default amounts so the northeast corner stays uncluttered.
old = """    REGION_HIDE_LABELS = {\n        'North America': set(),\n        'Asia': {\n"""
new = """    REGION_HIDE_LABELS = {\n        'North America': set(),\n        'Africa': {\n            # These Middle East sovereigns can fall inside the Africa crop. Keep\n            # their polygons/default colours and hover data, but suppress text.\n            'IRQ','LBN'\n        },\n        'Asia': {\n"""
if old not in s:
    raise SystemExit('REGION_HIDE_LABELS header not found')
s = s.replace(old, new, 1)

# Update the LATAM hidden-label comment now that only Venezuela has a callout.
s = s.replace(
    "            # Venezuela and Haiti are rendered separately as callouts below.\n",
    "            # Venezuela is rendered separately as a callout below; Haiti stays unlabeled.\n",
    1,
)

# 2) Europe: always append the selected-year amount for Russia as well as
# Ukraine/Belarus whenever the value is positive.
old = "            if code in {'UKR', 'BLR'}:\n"
new = "            if code in {'UKR', 'BLR', 'RUS'}:\n"
if old not in s:
    raise SystemExit('Europe key-default label condition not found')
s = s.replace(old, new, 1)

# Keep Russia out of the shared 9pt Europe text traces so it can have a dedicated
# larger, high-contrast label below.
old = "            europe_part = europe_label_df[europe_label_df['light_text'] == light_text]\n"
new = "            europe_part = europe_label_df[(europe_label_df['light_text'] == light_text) & (europe_label_df['code'] != 'RUS')]\n"
if old not in s:
    raise SystemExit('Europe label partition line not found')
s = s.replace(old, new, 1)

marker = """            fig_map.add_trace(go.Scattergeo(\n                lon=europe_part['lon'],\n                lat=europe_part['lat'],\n                text=europe_part['text'],\n                mode='text',\n                showlegend=False,\n                hoverinfo='skip',\n                textfont=dict(\n                    color=text_color,\n                    size=9,\n                    family=font_family,\n                )\n            ))\n\n    elif not view_df.empty:\n"""
replacement = """            fig_map.add_trace(go.Scattergeo(\n                lon=europe_part['lon'],\n                lat=europe_part['lat'],\n                text=europe_part['text'],\n                mode='text',\n                showlegend=False,\n                hoverinfo='skip',\n                textfont=dict(\n                    color=text_color,\n                    size=9,\n                    family=font_family,\n                )\n            ))\n\n        # Russia gets its own larger label so both the name and default amount\n        # remain easy to read on-screen and in PNG exports.\n        russia_label = europe_label_df[europe_label_df['code'] == 'RUS']\n        if not russia_label.empty:\n            russia_row = russia_label.iloc[0]\n            russia_color = '#ffffff' if bool(russia_row['light_text']) else '#222222'\n            fig_map.add_trace(go.Scattergeo(\n                lon=[russia_row['lon']],\n                lat=[russia_row['lat']],\n                text=[russia_row['text']],\n                mode='text',\n                showlegend=False,\n                hoverinfo='skip',\n                textfont=dict(\n                    color=russia_color,\n                    size=12,\n                    family='Arial Black',\n                )\n            ))\n\n    elif not view_df.empty:\n"""
if marker not in s:
    raise SystemExit('Europe label trace block not found')
s = s.replace(marker, replacement, 1)

# 3) Latin America: remove Haiti callout entirely and shorten Venezuela's arrow.
old = """        LATAM_CALLOUTS = {\n            'VEN': dict(\n                # Put Venezuela's label in the open Atlantic to the east so it\n                # does not collide with Honduras/Nicaragua/Central America.\n                label_lon=-48.0, label_lat=13.5, arrow='←',\n                marker_symbol='triangle-left'\n            ),\n            'HTI': dict(\n                label_lon=-66.0, label_lat=22.2, arrow='←',\n                marker_symbol='triangle-left'\n            ),\n        }\n"""
new = """        LATAM_CALLOUTS = {\n            'VEN': dict(\n                # Keep the label east of Venezuela but start the connector away\n                # from the text so the line/arrow never crosses the amount.\n                label_lon=-51.0, label_lat=12.0,\n                line_lon=-56.0, line_lat=9.5,\n                marker_symbol='triangle-left'\n            ),\n        }\n"""
if old not in s:
    raise SystemExit('LATAM callout dictionary not found')
s = s.replace(old, new, 1)

old = """            if code == 'VEN':\n                callout_text = (\n                    f\"<b>{spec['arrow']} {display_name}</b>\"\n                    f\"<br><b>{value_text}</b>\"\n                )\n            else:\n                callout_text = (\n                    f\"<b>{spec['arrow']} {display_name}</b>\"\n                    f\"<br><b>{value_text}</b>\"\n                )\n"""
new = """            callout_text = (\n                f\"<b>{display_name}</b>\"\n                f\"<br><b>{value_text}</b>\"\n            )\n"""
if old not in s:
    raise SystemExit('LATAM callout text block not found')
s = s.replace(old, new, 1)

old = """            fig_map.add_trace(go.Scattergeo(\n                lon=[spec['label_lon'], target_lon],\n                lat=[spec['label_lat'], target_lat],\n                mode='lines',\n                line=dict(color='#111111', width=2.0),\n"""
new = """            fig_map.add_trace(go.Scattergeo(\n                lon=[spec['line_lon'], target_lon],\n                lat=[spec['line_lat'], target_lat],\n                mode='lines',\n                line=dict(color='#111111', width=1.5),\n"""
if old not in s:
    raise SystemExit('LATAM connector line block not found')
s = s.replace(old, new, 1)

old = "                    size=11, color='#111111',\n"
new = "                    size=8, color='#111111',\n"
if old not in s:
    raise SystemExit('LATAM arrowhead size not found')
s = s.replace(old, new, 1)

# Guards.
if "'HTI': dict(" in s:
    raise SystemExit('Haiti callout still present')
if "'Africa': {\n            # These Middle East sovereigns" not in s:
    raise SystemExit('Africa hidden-label rule missing')
if "if code in {'UKR', 'BLR', 'RUS'}:" not in s:
    raise SystemExit('Russia default amount rule missing')
if "size=12,\n                    family='Arial Black'" not in s:
    raise SystemExit('Dedicated Russia emphasis missing')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Final map label cleanup applied; syntax check passed.')
