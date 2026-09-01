from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# Remove an accidental second copy of the Asia Middle East summary block.
marker = "    if region == 'Asia':\n        MIDDLE_EAST_NAMES = {\n"
first = s.find(marker)
second = s.find(marker, first + len(marker)) if first != -1 else -1
if second != -1:
    latam = s.find("    if region == 'Latin America & Caribbean':\n", second)
    if latam == -1:
        raise SystemExit('Could not find LATAM block after duplicate Middle East block')
    s = s[:second] + s[latam:]

# Remove an accidental duplicate PNG annotation-sizing loop.
ann_block = """                    for ann in export_fig.layout.annotations:\n                        if ann.text and 'MIDDLE EAST' in str(ann.text):\n                            ann.font.size = 16\n                            ann.font.family = 'Arial Black'\n                            ann.borderpad = 11\n\n"""
while s.count(ann_block) > 1:
    first_pos = s.find(ann_block)
    second_pos = s.find(ann_block, first_pos + len(ann_block))
    s = s[:second_pos] + s[second_pos + len(ann_block):]

if s.count(marker) != 1:
    raise SystemExit(f'Expected one Middle East block, found {s.count(marker)}')
if s.count(ann_block) != 1:
    raise SystemExit(f'Expected one Middle East PNG loop, found {s.count(ann_block)}')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Middle East summary duplicates removed; syntax check passed.')
