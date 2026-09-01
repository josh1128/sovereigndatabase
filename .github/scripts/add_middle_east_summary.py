from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# Insert a compact Middle East category panel on the Asia-Pacific map. The
# country polygons remain uncluttered; only countries with positive defaults
# for the selected year are listed, with a total and each default amount.
needle = """    if region == 'Latin America & Caribbean':\n        LATAM_CALLOUTS = {\n"""
insert = """    if region == 'Asia':\n        MIDDLE_EAST_NAMES = {\n            'TUR': 'TURKIYE',\n            'CYP': 'CYPRUS',\n            'IRN': 'IRAN',\n            'IRQ': 'IRAQ',\n            'SYR': 'SYRIA',\n            'LBN': 'LEBANON',\n            'ISR': 'ISRAEL',\n            'PSE': 'WEST BANK & GAZA',\n            'JOR': 'JORDAN',\n            'SAU': 'SAUDI ARABIA',\n            'YEM': 'YEMEN',\n            'OMN': 'OMAN',\n            'ARE': 'UAE',\n            'KWT': 'KUWAIT',\n            'QAT': 'QATAR',\n            'BHR': 'BAHRAIN',\n        }\n\n        middle_east_df = map_df[\n            map_df['code'].isin(MIDDLE_EAST_NAMES)\n            & (map_df['value'].fillna(0) > 0)\n        ].copy()\n        middle_east_df = middle_east_df.sort_values(\n            ['value', 'country'], ascending=[False, True]\n        )\n\n        def fmt_middle_east_value(value):\n            value = float(value)\n            if value >= 1000:\n                return f\"${value/1e3:,.1f}B\"\n            return f\"${value:,.0f}M\"\n\n        if middle_east_df.empty:\n            middle_east_text = (\n                f\"<b>MIDDLE EAST</b><br>\"\n                f\"<b>{map_year} DEFAULTS</b><br>\"\n                \"No positive defaults\"\n            )\n        else:\n            middle_east_total = middle_east_df['value'].sum()\n            summary_lines = [\n                \"<b>MIDDLE EAST</b>\",\n                f\"<b>{map_year} DEFAULTS · {fmt_middle_east_value(middle_east_total)} TOTAL</b>\",\n            ]\n            for _, me_row in middle_east_df.iterrows():\n                summary_lines.append(\n                    f\"{MIDDLE_EAST_NAMES.get(me_row['code'], me_row['code'])}  \"\n                    f\"<b>{fmt_middle_east_value(me_row['value'])}</b>\"\n                )\n            middle_east_text = '<br>'.join(summary_lines)\n\n        fig_map.add_annotation(\n            text=middle_east_text,\n            xref='paper', yref='paper',\n            x=0.985, y=0.965,\n            xanchor='right', yanchor='top',\n            showarrow=False, align='left',\n            bgcolor='rgba(255,255,255,0.96)',\n            bordercolor='#b8b8b8', borderwidth=1.2, borderpad=9,\n            font=dict(size=11, color='#111111', family='Arial Black'),\n        )\n\n    if region == 'Latin America & Caribbean':\n        LATAM_CALLOUTS = {\n"""
if needle not in s:
    raise SystemExit('LATAM callout insertion point not found')
s = s.replace(needle, insert, 1)

# Make the Middle East panel larger in PNG exports so it stays readable after
# Kaleido rasterization. Other annotations keep their existing sizing.
needle = """                    export_fig.update_layout(\n                        font=dict(size=16),\n                        legend=dict(\n"""
replacement = """                    for ann in export_fig.layout.annotations:\n                        if ann.text and 'MIDDLE EAST' in str(ann.text):\n                            ann.font.size = 16\n                            ann.font.family = 'Arial Black'\n                            ann.borderpad = 11\n\n                    export_fig.update_layout(\n                        font=dict(size=16),\n                        legend=dict(\n"""
if needle not in s:
    raise SystemExit('PNG export layout block not found')
s = s.replace(needle, replacement, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Middle East category/default summary added; syntax check passed.')
