from pathlib import Path
import re

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# 1) Export safeguard. Geo maps can leave unused white space inside the paper
# area because the projection preserves its aspect ratio. After export margins
# (especially note margins) are applied, force regional legends farther into
# the actual map area. Keep the World legend lower because its rectangular
# equirectangular view already fills most of the canvas.
needle = '''    for ann in out.layout.annotations:\n        if ann.font is None or ann.font.color is None:\n            ann.font.color = INK\n\n    note = (note or "").strip()\n'''
replacement = '''    for ann in out.layout.annotations:\n        if ann.font is None or ann.font.color is None:\n            ann.font.color = INK\n\n    # Keep map legends inside the blue shaded geography in exported files.\n    # Regional maps use Mercator; the World view uses equirectangular.\n    if is_geo and out.layout.legend is not None:\n        projection_type = str(\n            getattr(getattr(out.layout.geo, 'projection', None), 'type', '') or ''\n        ).lower()\n        is_world_geo = projection_type == 'equirectangular'\n\n        out.update_layout(\n            legend=dict(\n                x=0.02 if is_world_geo else 0.055,\n                y=0.055 if is_world_geo else 0.18,\n                xanchor='left',\n                yanchor='bottom',\n            )\n        )\n\n    note = (note or "").strip()\n'''
if needle not in s:
    raise SystemExit('Could not find figure_with_note insertion point.')
s = s.replace(needle, replacement, 1)

# 2) Also move the regional legend on-screen so the interactive view and PNG
# preview use the same safe placement. Restrict the edit to the map layout.
start = s.find('    fig_map.update_layout(')
if start == -1:
    raise SystemExit('fig_map.update_layout block not found.')
end = s.find('    show_chart(', start)
if end == -1:
    raise SystemExit('show_chart after map layout not found.')
block = s[start:end]

# Support both the conditional World/regional layout and older fixed values.
block2, nx = re.subn(
    r"(?m)^(\s*)x\s*=\s*(?:0\.015 if is_world else 0\.02|0\.02),\s*$",
    r"\1x=0.02 if is_world else 0.055,",
    block,
    count=1,
)
if nx != 1:
    raise SystemExit('Could not update map legend x position.')

block3, ny = re.subn(
    r"(?m)^(\s*)y\s*=\s*(?:0\.025 if is_world else 0\.03|0\.03),\s*$",
    r"\1y=0.055 if is_world else 0.18,",
    block2,
    count=1,
)
if ny != 1:
    raise SystemExit('Could not update map legend y position.')

s = s[:start] + block3 + s[end:]

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Regional map legends moved safely inside blue map area; syntax check passed.')
