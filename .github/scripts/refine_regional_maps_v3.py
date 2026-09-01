from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# 1) Crop Asia-Pacific so only the eastern/visible portion of Russia remains,
# and make the World map taller on screen before export.
s = s.replace(
    "        'Asia': dict(lon=(25,180),lat=(-12,78)),",
    "        'Asia': dict(lon=(60,180),lat=(-12,72)),",
    1,
)
s = s.replace("        'World':650,", "        'World':760,", 1)

# 2) Always render all six legend categories, using the same square key for
# every map. Choropleth traces themselves no longer create legend entries.
old = '''    fig_map = go.Figure()\n    for lab in MAP_LABELS:\n        band_df = view_df[view_df['band'] == lab]\n        if band_df.empty:\n            continue\n        customdata = np.column_stack([band_df['value'].map(lambda x:f"${x:,.0f}M"),band_df['rank'].map(lambda x:'' if pd.isna(x) else f"#{int(x)}")])\n        fig_map.add_trace(go.Choropleth(locations=band_df['code'],z=np.ones(len(band_df)),text=band_df['country'],customdata=customdata,colorscale=[[0,MAP_COLORS[lab]],[1,MAP_COLORS[lab]]],showscale=False,marker_line_color='#8c8c8c',marker_line_width=0.75,name=lab,showlegend=True,legendgroup=lab,hovertemplate='<b>%{text}</b><br>Debt in default: %{customdata[0]}<br>Regional order: %{customdata[1]}<extra></extra>'))\n'''
new = '''    fig_map = go.Figure()\n    for lab in MAP_LABELS:\n        # Dedicated legend key: this guarantees the same six categories, in the\n        # same order and style, even when a selected region has no country in a band.\n        fig_map.add_trace(go.Scattergeo(\n            lon=[None], lat=[None], mode='markers',\n            marker=dict(size=13, color=MAP_COLORS[lab], symbol='square'),\n            name=f"\\u2002{lab}\\u2002",\n            showlegend=True, legendgroup=lab, hoverinfo='skip',\n        ))\n\n        band_df = view_df[view_df['band'] == lab]\n        if band_df.empty:\n            continue\n\n        customdata = np.column_stack([\n            band_df['value'].map(lambda x:f"${x:,.0f}M"),\n            band_df['rank'].map(lambda x:'' if pd.isna(x) else f"#{int(x)}")\n        ])\n        fig_map.add_trace(go.Choropleth(\n            locations=band_df['code'], z=np.ones(len(band_df)),\n            text=band_df['country'], customdata=customdata,\n            colorscale=[[0,MAP_COLORS[lab]],[1,MAP_COLORS[lab]]],\n            showscale=False, marker_line_color='#8c8c8c', marker_line_width=0.75,\n            name=lab, showlegend=False, legendgroup=lab,\n            hovertemplate='<b>%{text}</b><br>Debt in default: %{customdata[0]}<br>Regional order: %{customdata[1]}<extra></extra>'\n        ))\n'''
if old not in s:
    raise SystemExit('Legend/choropleth loop not found')
s = s.replace(old, new, 1)

# 3) Add spacing for crowded South/Southeast Asia labels.
old = "        'Asia': {'LBN':(-1.5,0.7),'ISR':(-1.5,-0.5),'PSE':(1.5,-0.7),'JOR':(1.5,0.4),'KWT':(1.3,0.8),'QAT':(1.4,-0.4),'BHR':(1.4,0.5),'SGP':(1.5,-0.8),'BRN':(1.5,0.5)},\n"
new = "        'Asia': {'LBN':(-2.0,1.2),'ISR':(-2.0,-0.8),'PSE':(2.0,-1.0),'JOR':(2.0,0.7),'KWT':(1.8,1.0),'QAT':(1.8,-0.7),'BHR':(1.8,0.7),'SGP':(2.0,-1.0),'BRN':(2.0,0.8),'BGD':(2.0,1.0),'NPL':(-2.0,1.0),'LKA':(2.0,-1.5),'THA':(-2.2,1.0),'LAO':(-2.2,1.4),'KHM':(2.2,-1.2),'VNM':(2.5,0.4),'MYS':(2.5,-1.0)},\n"
if old not in s:
    raise SystemExit('Asia label offsets not found')
s = s.replace(old, new, 1)

# 4) De-clutter Asia-Pacific and reserve Venezuela/Haiti for callouts.
old = '''    REGION_HIDE_LABELS = {\n        'North America': set(),\n        'Latin America & Caribbean': {\n            # Keep tiny island polygons/hover data but suppress overlapping text.\n            'ABW','AIA','ATG','BHS','BRB','CUW','DMA','GRD','KNA','LCA','PRI','SXM','VCT'\n        },\n    }\n'''
new = '''    REGION_HIDE_LABELS = {\n        'North America': set(),\n        'Asia': {\n            # Tiny, dense labels remain available via hover/table but are omitted\n            # from the printed label layer to keep Asia-Pacific readable.\n            'PSE','QAT','BHR','SGP','BRN'\n        },\n        'Latin America & Caribbean': {\n            # Keep tiny island polygons/hover data but suppress overlapping text.\n            # Venezuela and Haiti are rendered separately as callouts below.\n            'ABW','AIA','ATG','BHS','BRB','CUW','DMA','GRD','KNA','LCA','PRI','SXM','VCT',\n            'VEN','HTI'\n        },\n    }\n'''
if old not in s:
    raise SystemExit('REGION_HIDE_LABELS block not found')
s = s.replace(old, new, 1)
s = s.replace("        'Asia':18,", "        'Asia':14,", 1)

# 5) Europe: show labels only for countries actually in default for the selected
# year, plus Greece as a permanent reference label.
needle = '''        europe_labels = []\n        for code in EUROPE_LABEL_CODES:\n            if code not in COUNTRY_CENTROIDS:\n                continue\n'''
replacement = '''        europe_labels = []\n        europe_default_codes = set(\n            view_df.loc[view_df['value'].fillna(0) > 0, 'code'].dropna()\n        )\n        europe_visible_codes = europe_default_codes | {'GRC'}\n\n        for code in EUROPE_LABEL_CODES:\n            if code not in europe_visible_codes:\n                continue\n            if code not in COUNTRY_CENTROIDS:\n                continue\n'''
if needle not in s:
    raise SystemExit('Europe label loop not found')
s = s.replace(needle, replacement, 1)

# 6) Add external callouts for Venezuela and Haiti. These are only shown when
# the country has debt in default in the selected year. A pointer line plus a
# directional arrow in the label makes the small/awkward geography legible.
needle = '''    geo_kw = dict(showframe=False,showcoastlines=True,coastlinecolor='#8c8c8c',coastlinewidth=0.75,showland=True,landcolor='#f2f2f2',showocean=True,oceancolor='#a9c7e8',showlakes=True,lakecolor='#a9c7e8',showcountries=True,countrycolor='#8c8c8c',countrywidth=0.75,bgcolor='white',projection_type='equirectangular' if region == 'World' else 'mercator')\n'''
callouts = '''    if region == 'Latin America & Caribbean':\n        LATAM_CALLOUTS = {\n            'VEN': dict(label_lon=-75.0, label_lat=11.5, arrow='→'),\n            'HTI': dict(label_lon=-66.5, label_lat=22.0, arrow='←'),\n        }\n\n        for code, spec in LATAM_CALLOUTS.items():\n            row_match = view_df[view_df['code'] == code]\n            if row_match.empty:\n                continue\n            row = row_match.iloc[0]\n            if float(row['value'] or 0) <= 0:\n                continue\n\n            target_lat, target_lon, display_name = COUNTRY_CENTROIDS[code]\n            if code == 'VEN':\n                callout_text = f"<b>{display_name} {spec['arrow']}</b>"\n            else:\n                callout_text = f"<b>{spec['arrow']} {display_name}</b>"\n            if row['value'] >= 10000:\n                callout_text += f"<br><b>${row['value']/1e3:,.1f}B</b>"\n\n            fig_map.add_trace(go.Scattergeo(\n                lon=[spec['label_lon'], target_lon],\n                lat=[spec['label_lat'], target_lat],\n                mode='lines',\n                line=dict(color='#222222', width=1.4),\n                showlegend=False, hoverinfo='skip',\n            ))\n            fig_map.add_trace(go.Scattergeo(\n                lon=[spec['label_lon']], lat=[spec['label_lat']],\n                text=[callout_text], mode='text',\n                textfont=dict(color='#222222', size=11, family='Arial Black'),\n                showlegend=False, hoverinfo='skip',\n            ))\n\n    geo_kw = dict(showframe=False,showcoastlines=True,coastlinecolor='#8c8c8c',coastlinewidth=0.75,showland=True,landcolor='#f2f2f2',showocean=True,oceancolor='#a9c7e8',showlakes=True,lakecolor='#a9c7e8',showcountries=True,countrycolor='#8c8c8c',countrywidth=0.75,bgcolor='white',projection_type='equirectangular' if region == 'World' else 'mercator')\n'''
if needle not in s:
    raise SystemExit('geo_kw line not found for callout insertion')
s = s.replace(needle, callouts, 1)

# 7) Give the legend more breathing room and keep its typography/style identical
# across map views. itemwidth separates the color square from category text.
old = '''    legend_title = f"<b>{map_year} total debt in default<br>by country (US$ millions)</b>"\n    is_world = region == 'World'\n    fig_map.update_layout(\n        height=REGION_HEIGHTS.get(region,860),\n        geo=geo_kw,\n        title=None,\n        legend=dict(\n            title=dict(\n                text=legend_title,\n                font=dict(size=12 if is_world else 15,color='#111111',family='Arial Black'),\n            ),\n            x=0.02 if is_world else 0.055,\n            y=0.055 if is_world else 0.18,\n            xanchor='left',\n            yanchor='bottom',\n            bgcolor='rgba(255,255,255,0.97)',\n            bordercolor='#b8b8b8',\n            borderwidth=1,\n            font=dict(size=10 if is_world else 13,color='#111111',family='Arial Black'),\n            itemsizing='constant',\n            traceorder='normal',\n        ),\n        margin=dict(l=0,r=0,t=8,b=0),\n        paper_bgcolor='white',\n        font=dict(family='Arial',size=11 if is_world else 13,color='#222222'),\n    )\n'''
new = '''    legend_title = (\n        f"<b>{map_year} total debt in default<br>by country<br>(US$ millions)</b>"\n    )\n    is_world = region == 'World'\n    fig_map.update_layout(\n        height=REGION_HEIGHTS.get(region,860),\n        geo=geo_kw,\n        title=None,\n        legend=dict(\n            title=dict(\n                text=legend_title,\n                font=dict(size=14,color='#111111',family='Arial Black'),\n            ),\n            x=0.03 if is_world else 0.06,\n            y=0.07 if is_world else 0.19,\n            xanchor='left',\n            yanchor='bottom',\n            bgcolor='rgba(255,255,255,0.98)',\n            bordercolor='#b8b8b8',\n            borderwidth=1.2,\n            font=dict(size=12,color='#111111',family='Arial Black'),\n            itemsizing='constant',\n            itemwidth=52,\n            tracegroupgap=6,\n            traceorder='normal',\n        ),\n        margin=dict(l=0,r=0,t=8,b=0),\n        paper_bgcolor='white',\n        font=dict(family='Arial',size=13,color='#222222'),\n    )\n'''
if old not in s:
    raise SystemExit('Map legend layout block not found')
s = s.replace(old, new, 1)

# 8) Keep the export-copy legend at the same roomier position.
s = s.replace(
    "                x=0.02 if is_world_geo else 0.055,\n                y=0.055 if is_world_geo else 0.18,",
    "                x=0.03 if is_world_geo else 0.06,\n                y=0.07 if is_world_geo else 0.19,",
    1,
)

# 9) Make the World PNG taller/wider so it fills a landscape page, while
# preserving each regional map's own height. Keep export legend style consistent.
needle = '''                    is_world_export = projection_type == 'equirectangular'\n\n                    for trace in export_fig.data:\n'''
replacement = '''                    is_world_export = projection_type == 'equirectangular'\n\n                    if is_world_export:\n                        export_width = 1800\n                        export_height = max(int(export_fig.layout.height or 760), 1000)\n\n                    for trace in export_fig.data:\n'''
if needle not in s:
    raise SystemExit('World export detection block not found')
s = s.replace(needle, replacement, 1)

old = '''                    export_fig.update_layout(\n                        font=dict(size=16),\n                        legend=dict(\n                            title=dict(\n                                font=dict(\n                                    size=18 if is_world_export else 20,\n                                    family='Arial Black',\n                                )\n                            ),\n                            font=dict(\n                                size=15 if is_world_export else 17,\n                                family='Arial Black',\n                            ),\n                        ),\n                    )\n'''
new = '''                    export_fig.update_layout(\n                        font=dict(size=16),\n                        legend=dict(\n                            title=dict(\n                                font=dict(size=18, family='Arial Black')\n                            ),\n                            font=dict(size=16, family='Arial Black'),\n                            itemsizing='constant',\n                            itemwidth=58,\n                            tracegroupgap=8,\n                        ),\n                    )\n'''
if old not in s:
    raise SystemExit('PNG legend typography block not found')
s = s.replace(old, new, 1)

s = s.replace(
    "                            x=0.02 if is_world_export else 0.055,\n                            y=0.055 if is_world_export else 0.18,",
    "                            x=0.03 if is_world_export else 0.06,\n                            y=0.07 if is_world_export else 0.19,",
    1,
)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Regional map refinements applied; syntax check passed.')
