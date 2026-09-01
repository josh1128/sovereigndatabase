from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# Show enough of western Asia to make the Middle East callouts meaningful,
# while preserving the tighter northern crop that removes most of Russia.
s = s.replace(
    "        'Asia': dict(lon=(60,180),lat=(-12,58)),",
    "        'Asia': dict(lon=(30,180),lat=(-12,58)),",
    1,
)

start_marker = "    if region == 'Asia':\n        MIDDLE_EAST_NAMES = {\n"
end_marker = "    if region == 'Latin America & Caribbean':\n"
start = s.find(start_marker)
if start == -1:
    raise SystemExit('Current Middle East summary block not found')
end = s.find(end_marker, start)
if end == -1:
    raise SystemExit('LATAM callout block not found after Middle East block')

new_block = '''    if region == 'Asia':
        MIDDLE_EAST_NAMES = {
            'TUR': 'TURKIYE',
            'CYP': 'CYPRUS',
            'IRN': 'IRAN',
            'IRQ': 'IRAQ',
            'SYR': 'SYRIA',
            'LBN': 'LEBANON',
            'ISR': 'ISRAEL',
            'PSE': 'WEST BANK & GAZA',
            'JOR': 'JORDAN',
            'SAU': 'SAUDI ARABIA',
            'YEM': 'YEMEN',
            'OMN': 'OMAN',
            'ARE': 'UAE',
            'KWT': 'KUWAIT',
            'QAT': 'QATAR',
            'BHR': 'BAHRAIN',
        }

        # Visually group the Middle East without covering the sovereign-default
        # colour fills. The outline remains visible in interactive and PNG maps.
        middle_east_outline_lon = [30.5, 35.0, 42.0, 50.0, 60.0, 60.0,
                                   56.0, 50.0, 43.0, 37.0, 32.0, 30.5]
        middle_east_outline_lat = [41.5, 43.0, 42.0, 40.0, 36.0, 24.0,
                                   12.0, 12.0, 13.0, 18.0, 29.0, 41.5]
        fig_map.add_trace(go.Scattergeo(
            lon=middle_east_outline_lon,
            lat=middle_east_outline_lat,
            mode='lines',
            fill='toself',
            fillcolor='rgba(255,255,255,0.05)',
            line=dict(color='#333333', width=2.2),
            showlegend=False,
            hoverinfo='skip',
        ))
        fig_map.add_trace(go.Scattergeo(
            lon=[46.0], lat=[43.5],
            text=['<b>MIDDLE EAST</b>'],
            mode='text',
            textfont=dict(color='#111111', size=13, family='Arial Black'),
            showlegend=False,
            hoverinfo='skip',
        ))

        middle_east_df = map_df[
            map_df['code'].isin(MIDDLE_EAST_NAMES)
            & (map_df['value'].fillna(0) > 0)
        ].copy()

        def fmt_middle_east_value(value):
            value = float(value)
            if value >= 1000:
                return f"${value/1e3:,.1f}B"
            return f"${value:,.0f}M"

        if not middle_east_df.empty:
            # Add target coordinates and split callouts to both sides of the
            # highlighted area. Sorting by latitude minimizes crossing lines.
            middle_east_df['target_lat'] = middle_east_df['code'].map(
                lambda c: float(COUNTRY_CENTROIDS[c][0])
            )
            middle_east_df['target_lon'] = middle_east_df['code'].map(
                lambda c: float(COUNTRY_CENTROIDS[c][1])
            )
            middle_east_df['side'] = np.where(
                middle_east_df['target_lon'] <= 47.0, 'left', 'right'
            )

            for side, label_lon, arrow_symbol in [
                ('left', 33.5, 'triangle-right'),
                ('right', 64.5, 'triangle-left'),
            ]:
                side_df = middle_east_df[
                    middle_east_df['side'] == side
                ].sort_values(['target_lat', 'value'], ascending=[False, False]).copy()
                if side_df.empty:
                    continue

                if len(side_df) == 1:
                    label_lats = [34.0]
                else:
                    label_lats = np.linspace(52.5, 14.0, len(side_df))

                for (_, me_row), label_lat in zip(side_df.iterrows(), label_lats):
                    code = me_row['code']
                    target_lon = float(me_row['target_lon'])
                    target_lat = float(me_row['target_lat'])
                    value_text = fmt_middle_east_value(me_row['value'])
                    country_text = MIDDLE_EAST_NAMES.get(code, code)
                    callout_text = (
                        f"<b>{country_text}</b><br>"
                        f"<b>{value_text}</b>"
                    )

                    # Connector line to the sovereign.
                    fig_map.add_trace(go.Scattergeo(
                        lon=[label_lon, target_lon],
                        lat=[float(label_lat), target_lat],
                        mode='lines',
                        line=dict(color='#111111', width=1.8),
                        showlegend=False,
                        hoverinfo='skip',
                    ))

                    # Explicit arrowhead at the country end stays visible in PNG.
                    fig_map.add_trace(go.Scattergeo(
                        lon=[target_lon], lat=[target_lat],
                        mode='markers',
                        marker=dict(
                            size=10,
                            color='#111111',
                            symbol=arrow_symbol,
                            line=dict(width=0),
                        ),
                        showlegend=False,
                        hoverinfo='skip',
                    ))

                    fig_map.add_trace(go.Scattergeo(
                        lon=[label_lon], lat=[float(label_lat)],
                        text=[callout_text],
                        mode='text',
                        textfont=dict(
                            color='#111111', size=11, family='Arial Black'
                        ),
                        showlegend=False,
                        hoverinfo='skip',
                    ))

'''

s = s[:start] + new_block + s[end:]

# The old summary panel used an annotation-specific PNG size override. The new
# callouts are Scattergeo traces, so the existing geo export boost handles them.
old_png = '''                    for ann in export_fig.layout.annotations:\n                        if ann.text and 'MIDDLE EAST' in str(ann.text):\n                            ann.font.size = 16\n                            ann.font.family = 'Arial Black'\n                            ann.borderpad = 11\n\n'''
s = s.replace(old_png, '', 1)

# Guard against stale/duplicate summary-panel code.
if 'middle_east_text' in s:
    raise SystemExit('Old Middle East summary panel code still present')
if s.count("text=['<b>MIDDLE EAST</b>']") != 1:
    raise SystemExit('Expected exactly one Middle East highlight label')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Middle East highlight and arrow callouts applied; syntax check passed.')
