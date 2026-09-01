from pathlib import Path

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

old_dict = """            'VEN': dict(\n                # Keep the label east of Venezuela but start the connector away\n                # from the text so the line/arrow never crosses the amount.\n                label_lon=-58.5, label_lat=13.2,\n                line_lon=-62.2, line_lat=8.2,\n                marker_symbol='triangle-left'\n            ),\n"""
new_dict = """            'VEN': dict(\n                # Keep the label close to Venezuela; the connector starts just\n                # below the amount so the text and arrow read as one callout.\n                label_lon=-58.5, label_lat=13.2,\n                marker_symbol='triangle-left'\n            ),\n"""

if old_dict in s:
    s = s.replace(old_dict, new_dict, 1)
elif new_dict not in s:
    raise SystemExit('Current Venezuela callout dictionary not found')

old_line = """            # Connector line from the external label to the country.\n            fig_map.add_trace(go.Scattergeo(\n                lon=[spec['line_lon'], target_lon],\n                lat=[spec['line_lat'], target_lat],\n                mode='lines',\n                line=dict(color='#111111', width=1.5),\n                showlegend=False, hoverinfo='skip',\n            ))\n"""
new_line = """            # Start the connector immediately below the two-line label so the\n            # Venezuela text/amount is visibly connected to the arrow.\n            line_start_lon = spec['label_lon'] - 0.8\n            line_start_lat = spec['label_lat'] - 1.8\n            fig_map.add_trace(go.Scattergeo(\n                lon=[line_start_lon, target_lon],\n                lat=[line_start_lat, target_lat],\n                mode='lines',\n                line=dict(color='#111111', width=1.5),\n                showlegend=False, hoverinfo='skip',\n            ))\n"""

if old_line in s:
    s = s.replace(old_line, new_line, 1)
elif new_line not in s:
    raise SystemExit('Current Venezuela connector line block not found')

if "line_lon=" in s or "line_lat=" in s:
    raise SystemExit('Old detached Venezuela connector coordinates still present')
if s.count("line_start_lon = spec['label_lon'] - 0.8") != 1:
    raise SystemExit('Expected exactly one connected Venezuela line start')

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Venezuela label connected to arrow; syntax check passed.')
