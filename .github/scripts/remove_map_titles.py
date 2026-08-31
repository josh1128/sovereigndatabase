from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# Remove the World-specific Figure A-1 heading above the map.
world_heading = '''    if region == 'World':
        st.markdown(
            "<div style='font-family:Arial; font-size:16px; margin:4px 0 2px 0;'>"
            "<span style='color:#1b6f8a;'>Figure A-1:</span> "
            "<span style='color:#111111; font-weight:600;'>Global debt in default</span>"
            "</div>",
            unsafe_allow_html=True,
        )

'''
if world_heading in s:
    s = s.replace(world_heading, '', 1)
else:
    print('World heading block already absent.')

# Remove Plotly titles from regional maps as well.
old_title = '''        title=(
            None if is_world else
            dict(
                text=FIGURE_TITLES.get(region, f'Debt in default, {region}'),
                x=0.01,
                xanchor='left',
                font=dict(size=18,color='#1b6f8a'),
            )
        ),
'''
new_title = '''        title=None,
'''
if old_title not in s:
    raise SystemExit('Could not find regional map title layout block.')
s = s.replace(old_title, new_title, 1)

# Remove the extra title margin on regional views now that titles are gone.
old_margin = "        margin=dict(l=0,r=0,t=8 if is_world else 70,b=0),\n"
new_margin = "        margin=dict(l=0,r=0,t=8,b=0),\n"
if old_margin not in s:
    raise SystemExit('Could not find map margin block.')
s = s.replace(old_margin, new_margin, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Removed all Figure A-x map titles; syntax check passed.')
