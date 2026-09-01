from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# 1) Make every standard regional country label explicitly bold in the text.
old = '''        if pd.notna(row['value']) and row['value'] >= 10000:\n            return f"<b>{name}</b><br>${row['value']/1e3:,.1f}B"\n        return name\n'''
new = '''        if pd.notna(row['value']) and row['value'] >= 10000:\n            return f"<b>{name}</b><br><b>${row['value']/1e3:,.1f}B</b>"\n        return f"<b>{name}</b>"\n'''
if old not in s:
    raise SystemExit('format_country_label block not found')
s = s.replace(old, new, 1)

# 2) Make World continent label strings explicitly bold too.
world_repls = {
    "{'name':'NORTH AMERICA','lat':47,'lon':-107}": "{'name':'<b>NORTH AMERICA</b>','lat':47,'lon':-107}",
    "{'name':'SOUTH AMERICA','lat':-17,'lon':-61}": "{'name':'<b>SOUTH AMERICA</b>','lat':-17,'lon':-61}",
    "{'name':'EUROPE','lat':51,'lon':15}": "{'name':'<b>EUROPE</b>','lat':51,'lon':15}",
    "{'name':'AFRICA','lat':3,'lon':20}": "{'name':'<b>AFRICA</b>','lat':3,'lon':20}",
    "{'name':'ASIA','lat':42,'lon':92}": "{'name':'<b>ASIA</b>','lat':42,'lon':92}",
    "{'name':'AUSTRALIA','lat':-27,'lon':134}": "{'name':'<b>AUSTRALIA</b>','lat':-27,'lon':134}",
}
for old_text, new_text in world_repls.items():
    if old_text not in s:
        raise SystemExit(f'World label not found: {old_text}')
    s = s.replace(old_text, new_text, 1)

# 3) Europe uses a curated label layer; explicitly wrap each label in <b>.
old = "                'text': EUROPE_LABEL_NAMES.get(code, code),\n"
new = "                'text': f\"<b>{EUROPE_LABEL_NAMES.get(code, code)}</b>\",\n"
if old not in s:
    raise SystemExit('Europe label text assignment not found')
s = s.replace(old, new, 1)

# 4) Use a bold family for BOTH dark and light contrast label traces.
s = s.replace("            (False, '#222222', 'Arial'),\n            (True, '#ffffff', 'Arial Black'),", "            (False, '#222222', 'Arial Black'),\n            (True, '#ffffff', 'Arial Black'),", 1)
s = s.replace("                (False, '#222222', 'Arial'),\n                (True, '#ffffff', 'Arial Black'),", "                (False, '#222222', 'Arial Black'),\n                (True, '#ffffff', 'Arial Black'),", 1)

# 5) Bold the map legend family on-screen as well.
old = "                font=dict(size=12 if is_world else 15,color='#111111'),\n"
new = "                font=dict(size=12 if is_world else 15,color='#111111',family='Arial Black'),\n"
if old not in s:
    raise SystemExit('Map legend title font line not found')
s = s.replace(old, new, 1)
old = "            font=dict(size=10 if is_world else 13,color='#111111'),\n"
new = "            font=dict(size=10 if is_world else 13,color='#111111',family='Arial Black'),\n"
if old not in s:
    raise SystemExit('Map legend font line not found')
s = s.replace(old, new, 1)

# 6) During PNG generation, explicitly force every geo text trace to a bold
# family after the export copy is created. <b> markup remains in the text too,
# so Kaleido/Chromium has two independent bold signals.
needle = '''                        trace.textfont.size = new_size\n\n                    export_fig.update_layout(\n                        font=dict(size=16),\n                        legend=dict(\n                            title=dict(\n                                font=dict(size=18 if is_world_export else 20)\n                            ),\n                            font=dict(size=15 if is_world_export else 17),\n                        ),\n                    )\n'''
replacement = '''                        trace.textfont.size = new_size\n                        trace.textfont.family = 'Arial Black'\n\n                    export_fig.update_layout(\n                        font=dict(size=16),\n                        legend=dict(\n                            title=dict(\n                                font=dict(\n                                    size=18 if is_world_export else 20,\n                                    family='Arial Black',\n                                )\n                            ),\n                            font=dict(\n                                size=15 if is_world_export else 17,\n                                family='Arial Black',\n                            ),\n                        ),\n                    )\n'''
if needle not in s:
    raise SystemExit('PNG geo typography block not found')
s = s.replace(needle, replacement, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Bold map labels enforced on-screen and in PNG exports; syntax check passed.')
