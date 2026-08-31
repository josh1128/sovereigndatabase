from pathlib import Path
import re

p = Path('dashboard.py')
s = p.read_text(encoding='utf-8')

# 1) Widen the Europe extract to resemble the published reference map and
# include eastern context (Russia / Caucasus / Kazakhstan / Türkiye).
s, n = re.subn(
    r"'Europe':\s*dict\(lon=\([^\)]*\),\s*lat=\([^\)]*\)\),",
    "'Europe': dict(lon=(-15, 68), lat=(28, 72)),",
    s,
    count=1,
)
if n != 1:
    raise SystemExit(f'Could not update Europe bounds; matches={n}')

# 2) Give the Europe view more vertical room for its much denser label set.
# Handle both one-line and multi-line REGION_HEIGHTS formats.
start = s.find('REGION_HEIGHTS =')
if start == -1:
    raise SystemExit('REGION_HEIGHTS block not found')
end = s.find('\n\n', start)
if end == -1:
    end = min(len(s), start + 800)
block = s[start:end]
new_block, n = re.subn(r"('Europe'\s*:\s*)\d+", r"\g<1>900", block, count=1)
if n != 1:
    raise SystemExit('Could not update Europe height')
s = s[:start] + new_block + s[end:]

# 3) Add a dedicated Europe label layer before the generic regional label code.
# This is independent of df_countries, so countries with no default history
# still receive geographic labels like in the published map.
marker = "    elif not view_df.empty:\n"
if marker not in s:
    raise SystemExit('Regional label marker not found')

EuropeBlock = r'''    elif region == 'Europe':
        # Europe gets a curated cartographic label layer so the extract looks
        # like the published reference map. These labels do not depend on a
        # country having a default observation in df_countries.
        EUROPE_LABEL_CODES = [
            'ISL', 'IRL', 'GBR', 'PRT', 'ESP', 'FRA', 'BEL', 'NLD', 'LUX',
            'DEU', 'DNK', 'NOR', 'SWE', 'FIN', 'EST', 'LVA', 'LTU', 'POL',
            'CZE', 'SVK', 'AUT', 'CHE', 'HUN', 'SVN', 'HRV', 'BIH', 'SRB',
            'MNE', 'MKD', 'ALB', 'ITA', 'GRC', 'BGR', 'ROU', 'MDA', 'UKR',
            'BLR', 'RUS', 'TUR', 'GEO', 'ARM', 'AZE', 'KAZ',
        ]

        EUROPE_LABEL_NAMES = {
            'ISL': 'ICELAND',
            'IRL': 'IRELAND',
            'GBR': 'UNITED\nKINGDOM',
            'PRT': 'PORTUGAL',
            'ESP': 'SPAIN',
            'FRA': 'FRANCE',
            'BEL': 'BELGIUM',
            'NLD': 'NETHERLANDS',
            'LUX': 'LUX.',
            'DEU': 'GERMANY',
            'DNK': 'DENMARK',
            'NOR': 'NORWAY',
            'SWE': 'SWEDEN',
            'FIN': 'FINLAND',
            'EST': 'ESTONIA',
            'LVA': 'LATVIA',
            'LTU': 'LITHUANIA',
            'POL': 'POLAND',
            'CZE': 'CZECHIA',
            'SVK': 'SLOVAKIA',
            'AUT': 'AUSTRIA',
            'CHE': 'SWITZERLAND',
            'HUN': 'HUNGARY',
            'SVN': 'SLOVENIA',
            'HRV': 'CROATIA',
            'BIH': 'BOSNIA &\nHERZ.',
            'SRB': 'SERBIA',
            'MNE': 'MONTENEGRO',
            'MKD': 'N. MACEDONIA',
            'ALB': 'ALBANIA',
            'ITA': 'ITALY',
            'GRC': 'GREECE',
            'BGR': 'BULGARIA',
            'ROU': 'ROMANIA',
            'MDA': 'MOLDOVA',
            'UKR': 'UKRAINE',
            'BLR': 'BELARUS',
            'RUS': 'RUSSIA',
            'TUR': 'TÜRKIYE',
            'GEO': 'GEORGIA',
            'ARM': 'ARMENIA',
            'AZE': 'AZERBAIJAN',
            'KAZ': 'KAZAKHSTAN',
        }

        # Exact positions keep dense central/southeastern Europe legible and
        # place large transcontinental countries where they are visible in this
        # regional crop rather than at their geographic centroids.
        EUROPE_LABEL_POSITIONS = {
            'ISL': (-19.0, 65.0),
            'IRL': (-8.2, 53.2),
            'GBR': (-3.2, 55.0),
            'PRT': (-8.0, 39.5),
            'ESP': (-3.7, 40.2),
            'FRA': (2.0, 46.3),
            'BEL': (3.4, 50.7),
            'NLD': (5.8, 52.7),
            'LUX': (6.8, 49.5),
            'DEU': (10.5, 51.4),
            'DNK': (10.0, 56.3),
            'NOR': (8.5, 62.0),
            'SWE': (16.0, 61.5),
            'FIN': (26.0, 63.5),
            'EST': (26.5, 58.8),
            'LVA': (24.8, 56.9),
            'LTU': (23.8, 54.8),
            'POL': (19.4, 52.0),
            'CZE': (14.5, 49.5),
            'SVK': (20.4, 48.6),
            'AUT': (14.3, 47.5),
            'CHE': (8.0, 46.4),
            'HUN': (19.0, 47.0),
            'SVN': (14.3, 45.8),
            'HRV': (16.4, 44.7),
            'BIH': (18.1, 43.7),
            'SRB': (21.0, 44.5),
            'MNE': (19.2, 42.7),
            'MKD': (22.0, 41.2),
            'ALB': (19.5, 40.7),
            'ITA': (12.5, 42.2),
            'GRC': (22.5, 38.8),
            'BGR': (25.4, 42.8),
            'ROU': (25.0, 46.0),
            'MDA': (29.0, 47.2),
            'UKR': (31.5, 49.2),
            'BLR': (28.0, 53.6),
            'RUS': (49.0, 59.0),
            'TUR': (34.5, 39.1),
            'GEO': (43.3, 42.0),
            'ARM': (45.2, 40.0),
            'AZE': (48.0, 40.5),
            'KAZ': (58.0, 48.5),
        }

        europe_labels = []
        for code in EUROPE_LABEL_CODES:
            if code not in COUNTRY_CENTROIDS:
                continue
            default_lat, default_lon, _ = COUNTRY_CENTROIDS[code]
            plot_lon, plot_lat = EUROPE_LABEL_POSITIONS.get(
                code, (default_lon, default_lat)
            )
            europe_labels.append({
                'code': code,
                'text': EUROPE_LABEL_NAMES.get(code, code),
                'lon': plot_lon,
                'lat': plot_lat,
            })

        europe_label_df = pd.DataFrame(europe_labels)

        fig_map.add_trace(go.Scattergeo(
            lon=europe_label_df['lon'],
            lat=europe_label_df['lat'],
            text=europe_label_df['text'],
            mode='text',
            showlegend=False,
            hoverinfo='skip',
            textfont=dict(
                color='#2b2b2b',
                size=9,
                family='Arial'
            )
        ))

'''

s = s.replace(marker, EuropeBlock + marker, 1)

compile(s, 'dashboard.py', 'exec')
p.write_text(s, encoding='utf-8')
print('Expanded Europe labels and widened Europe view; syntax check passed.')
