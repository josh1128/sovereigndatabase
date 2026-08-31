from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# 1) For geo exports, make the entire export canvas/geo domain use the same
# ocean blue. This prevents a legend positioned near the lower-left from
# appearing over a white letterbox/margin when Kaleido preserves projection
# aspect ratio.
needle = '''    out.update_layout(\n        paper_bgcolor="white", plot_bgcolor="white",\n        font=dict(color=INK),\n        legend=dict(font=dict(color=INK)),\n        title=dict(font=dict(color=INK)),\n    )\n    if not is_geo:\n'''
replacement = '''    out.update_layout(\n        paper_bgcolor="white", plot_bgcolor="white",\n        font=dict(color=INK),\n        legend=dict(font=dict(color=INK)),\n        title=dict(font=dict(color=INK)),\n    )\n\n    # Geo/map exports should keep the full canvas visually continuous with\n    # the ocean. Plotly can otherwise leave white letterboxing around Mercator\n    # regional maps when rendered at a different export aspect ratio.\n    if is_geo:\n        OCEAN = "#a9c7e8"\n        out.update_layout(paper_bgcolor=OCEAN)\n        out.update_geos(bgcolor=OCEAN, oceancolor=OCEAN, showocean=True)\n\n    if not is_geo:\n'''
if needle not in s:
    raise SystemExit('Could not find export layout block')
s = s.replace(needle, replacement, 1)

# 2) Use the figure's actual height for geo PNGs instead of forcing all maps
# into 1600x900. If a user note adds bottom margin, add that extra margin to
# the exported height so the geographic area is not squeezed smaller.
needle2 = '''            try:\n                st.download_button(\n                    f"⬇️ Download PNG ({scale}x)",\n                    data=plotly_png_bytes(export_fig.to_json(), scale=scale),\n                    file_name=f"{base_name}.png",\n'''
replacement2 = '''            try:\n                is_geo_export = bool(export_fig.data) and export_fig.data[0].type in (\n                    "choropleth", "scattergeo"\n                )\n\n                export_width = 1600\n                export_height = 900\n\n                if is_geo_export:\n                    export_height = int(export_fig.layout.height or 900)\n\n                    # figure_with_note() increases the bottom margin. Preserve\n                    # the map's original drawable height by adding that margin\n                    # increase to the final PNG height instead of squeezing the map.\n                    original_bottom = int(fig.layout.margin.b or 0)\n                    export_bottom = int(export_fig.layout.margin.b or 0)\n                    export_height += max(0, export_bottom - original_bottom)\n\n                    # Re-pin the legend after final export sizing. Regional maps\n                    # need a higher y position than the rectangular World map.\n                    projection_type = str(\n                        getattr(\n                            getattr(export_fig.layout.geo, 'projection', None),\n                            'type',\n                            ''\n                        ) or ''\n                    ).lower()\n                    is_world_export = projection_type == 'equirectangular'\n                    export_fig.update_layout(\n                        legend=dict(\n                            x=0.02 if is_world_export else 0.055,\n                            y=0.055 if is_world_export else 0.18,\n                            xanchor='left',\n                            yanchor='bottom',\n                        )\n                    )\n\n                st.download_button(\n                    f"⬇️ Download PNG ({scale}x)",\n                    data=plotly_png_bytes(\n                        export_fig.to_json(),\n                        scale=scale,\n                        width=export_width,\n                        height=export_height,\n                    ),\n                    file_name=f"{base_name}.png",\n'''
if needle2 not in s:
    raise SystemExit('Could not find PNG download block')
s = s.replace(needle2, replacement2, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Geo PNG export sizing/background fix applied; syntax check passed.')
