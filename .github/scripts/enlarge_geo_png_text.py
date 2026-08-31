from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

needle = '''                if is_geo_export:\n                    export_height = int(export_fig.layout.height or 900)\n\n                    # figure_with_note() increases the bottom margin. Preserve\n'''

replacement = '''                if is_geo_export:\n                    export_height = int(export_fig.layout.height or 900)\n\n                    # PNG-only typography boost. Kaleido's scale parameter adds\n                    # pixels but does not make labels larger relative to the map.\n                    # Increase geo text and legend typography before rendering so\n                    # downloaded maps remain readable when pasted into Word/PPT.\n                    projection_type = str(\n                        getattr(\n                            getattr(export_fig.layout.geo, 'projection', None),\n                            'type',\n                            ''\n                        ) or ''\n                    ).lower()\n                    is_world_export = projection_type == 'equirectangular'\n\n                    for trace in export_fig.data:\n                        if getattr(trace, 'type', None) != 'scattergeo':\n                            continue\n\n                        current_size = getattr(\n                            getattr(trace, 'textfont', None), 'size', None\n                        ) or 12\n\n                        # World continent labels start larger and should be very\n                        # prominent; regional country labels get a ~60% boost.\n                        if is_world_export:\n                            new_size = max(28, int(round(float(current_size) * 1.55)))\n                        else:\n                            new_size = max(17, int(round(float(current_size) * 1.65)))\n\n                        trace.textfont.size = new_size\n\n                    export_fig.update_layout(\n                        font=dict(size=16),\n                        legend=dict(\n                            title=dict(\n                                font=dict(size=18 if is_world_export else 20)\n                            ),\n                            font=dict(size=15 if is_world_export else 17),\n                        ),\n                    )\n\n                    # figure_with_note() increases the bottom margin. Preserve\n'''

if needle not in s:
    raise SystemExit('Could not find geo export sizing block')

s = s.replace(needle, replacement, 1)

# Avoid recalculating projection_type later in the same block. Replace the
# repeated block with reuse of the variables established above.
old = '''                    # Re-pin the legend after final export sizing. Regional maps\n                    # need a higher y position than the rectangular World map.\n                    projection_type = str(\n                        getattr(\n                            getattr(export_fig.layout.geo, 'projection', None),\n                            'type',\n                            ''\n                        ) or ''\n                    ).lower()\n                    is_world_export = projection_type == 'equirectangular'\n                    export_fig.update_layout(\n'''
new = '''                    # Re-pin the legend after final export sizing. Regional maps\n                    # need a higher y position than the rectangular World map.\n                    export_fig.update_layout(\n'''

if old not in s:
    raise SystemExit('Could not find repeated projection block')
s = s.replace(old, new, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('PNG-only geo text enlargement applied; syntax check passed.')
