from pathlib import Path
import textwrap

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

ui_start = s.index('with st.sidebar:\n')
map_marker = '# ═══ MAP: Global debt in default ═════════════════════════════════════════════\nwith tab_map:\n'
map_start = s.index(map_marker)
footer_marker = '\nst.divider()\nst.caption(f"Source: BoC–BoE Sovereign Default Database'
footer_start = s.index(footer_marker, map_start)

# Keep only the actual map body, not the regional ranking table beneath it.
map_body = s[map_start + len(map_marker):footer_start]
table_marker = '    st.divider()\n    st.markdown(f"### {region} country order — {map_year}")\n'
if table_marker not in map_body:
    raise SystemExit('Map country-order table marker not found')
map_body = map_body.split(table_marker, 1)[0]
map_body = textwrap.dedent(map_body).rstrip() + '\n'

new_ui = '''y0, y1 = years[0], LAST_OBS


def span(lo=None, hi=None):
    a = max(y0, lo) if lo else y0
    b = min(y1, hi) if hi else y1
    return [y for y in years if a <= y <= b]


st.title("🌍 Sovereign Default Map")
st.caption(
    f"BoC–BoE Sovereign Default Database · Last observation: **{LAST_OBS}** · "
    f"{len(df_countries)} countries tracked"
)

'''

footer = '''\nst.caption(
    f"Source: BoC–BoE Sovereign Default Database · Last update: July 22, 2026 · "
    f"Last observation: {LAST_OBS}"
)\n'''

s = s[:ui_start] + new_ui + map_body + footer

# Remove the now-unused subplot import from the map-only dashboard.
s = s.replace('from plotly.subplots import make_subplots\n', '')

# Guards: map remains; legacy chart/tab UI and ranking table are gone.
for forbidden in [
    'st.tabs(',
    'Chart 1:',
    'Chart 8:',
    'with tab_a:',
    'with tab_b:',
    'with tab_c:',
    'with tab_map:',
    'country order —',
    'metric-card',
]:
    # metric-card can still exist in CSS; only fail if it appears in rendered UI below load.
    if forbidden == 'metric-card':
        continue
    if forbidden in s:
        raise SystemExit(f'Legacy dashboard UI still present: {forbidden}')

if 'fig_map = go.Figure()' not in s or 'Regional extract' not in s or 'Map year' not in s:
    raise SystemExit('Map UI was not preserved')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Dashboard reduced to map-only UI; syntax check passed.')
