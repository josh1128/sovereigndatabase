import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

st.set_page_config(page_title="Sovereign Default Database", layout="wide", page_icon="🌍")

# Country name -> ISO alpha-3 code, for the choropleth world map.
# Dissolved states with no modern geometry map to None and render as "no data".
ISO3_MAP = {
    'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA', 'Angola': 'AGO',
    'Anguila': 'AIA', 'Antigua and Barbuda': 'ATG', 'Argentina': 'ARG', 'Armenia': 'ARM',
    'Aruba': 'ABW', 'Azerbaijan': 'AZE', 'Bahamas': 'BHS', 'Bangladesh': 'BGD',
    'Barbados': 'BRB', 'Belarus': 'BLR', 'Belize': 'BLZ', 'Benin': 'BEN', 'Bhutan': 'BTN',
    'Bolivia': 'BOL', 'Bosnia & Herzegovina': 'BIH', 'Botswana': 'BWA', 'Brazil': 'BRA',
    'Bulgaria': 'BGR', 'Burkina Faso': 'BFA', 'Burundi': 'BDI', 'Cabo Verde': 'CPV',
    'Cambodia': 'KHM', 'Cameroon': 'CMR', 'Central African Republic': 'CAF', 'Chad': 'TCD',
    'Chile': 'CHL', 'China': 'CHN', 'Colombia': 'COL', 'Comoros': 'COM',
    'Rep. Of Congo (Brazzaville)': 'COG', 'Dem. Rep. of Congo (Kinshasa)': 'COD',
    'Cook Islands': 'COK', 'Costa Rica': 'CRI', 'Côte d’Ivoire': 'CIV', 'Croatia': 'HRV',
    'Cuba': 'CUB', 'Curaçao': 'CUW', 'Cyprus': 'CYP', 'Czechoslovakia': None,
    'Djibouti': 'DJI', 'Dominica': 'DMA', 'Dominican Republic': 'DOM', 'Ecuador': 'ECU',
    'Egypt': 'EGY', 'El Salvador': 'SLV', 'Equatorial Guinea': 'GNQ', 'Eritrea': 'ERI',
    'Ethiopia': 'ETH', 'Fiji': 'FJI', 'Gabon': 'GAB', 'The Gambia': 'GMB', 'Georgia': 'GEO',
    'Ghana': 'GHA', 'Greece': 'GRC', 'Grenada': 'GRD', 'Guatemala': 'GTM', 'Guinea': 'GIN',
    'Guinea-Bissau': 'GNB', 'Guyana': 'GUY', 'Haiti': 'HTI', 'Honduras': 'HND',
    'Hungary': 'HUN', 'India': 'IND', 'Indonesia': 'IDN', 'Iran': 'IRN', 'Iraq': 'IRQ',
    'Ireland': 'IRL', 'Jamaica': 'JAM', 'Jordan': 'JOR', 'Kazakhstan': 'KAZ', 'Kenya': 'KEN',
    "Korea, Democratic People's Republic of (North)": 'PRK', 'Kosovo': 'XKX',
    'Kyrgyz Republic': 'KGZ', 'Laos': 'LAO', 'Latvia': 'LVA', 'Lebanon': 'LBN',
    'Lesotho': 'LSO', 'Liberia': 'LBR', 'Libya': 'LBY', 'Lithuania': 'LTU',
    'North Macedonia': 'MKD', 'Madagascar': 'MDG', 'Malawi': 'MWI', 'Malaysia': 'MYS',
    'Maldives': 'MDV', 'Mali': 'MLI', 'Marshall Islands': 'MHL', 'Mauritania': 'MRT',
    'Mauritius': 'MUS', 'Mexico': 'MEX', 'Micronesia': 'FSM', 'Moldova': 'MDA',
    'Mongolia': 'MNG', 'Montenegro': 'MNE', 'Morocco': 'MAR', 'Mozambique': 'MOZ',
    'Myanmar': 'MMR', 'Namibia': 'NAM', 'Nauru': 'NRU', 'Nepal': 'NPL',
    'Netherlands Antilles': None, 'Nicaragua': 'NIC', 'Niger': 'NER', 'Nigeria': 'NGA',
    'Pakistan': 'PAK', 'Palau': 'PLW', 'Panama': 'PAN', 'Papua New Guinea': 'PNG',
    'Paraguay': 'PRY', 'Peru': 'PER', 'Philippines': 'PHL', 'Poland': 'POL',
    'Portugal': 'PRT', 'Puerto Rico': 'PRI', 'Romania': 'ROU', 'Rwanda': 'RWA',
    'St. Kitts & Nevis': 'KNA', 'St. Lucia': 'LCA', 'St. Vincent and the Grenadines': 'VCT',
    'Samoa': 'WSM', 'São Tomé and Príncipe': 'STP', 'Senegal': 'SEN', 'Serbia': 'SRB',
    'Seychelles': 'SYC', 'Sierra Leone': 'SLE', 'Sint Maarten': 'SXM', 'Slovak Republic': 'SVK',
    'Slovenia': 'SVN', 'Solomon Islands': 'SLB', 'Somalia': 'SOM', 'South Africa': 'ZAF',
    'South Sudan': 'SSD', 'Sri Lanka': 'LKA', 'Sudan': 'SDN', 'Suriname': 'SUR',
    'eSwatini (Swaziland)': 'SWZ', 'Syria': 'SYR', 'Tajikistan': 'TJK', 'Tanzania': 'TZA',
    'Thailand': 'THA', 'Togo': 'TGO', 'Tonga': 'TON', 'Trinidad & Tobago': 'TTO',
    'Tunisia': 'TUN', 'Turkey': 'TUR', 'Turkmenistan': 'TKM', 'Tuvalu': 'TUV', 'Uganda': 'UGA',
    'Ukraine': 'UKR', 'United Kingdom': 'GBR', 'Uruguay': 'URY',
    'USSR/Russian Federation': 'RUS', 'Uzbekistan': 'UZB', 'Vanuatu': 'VUT',
    'Venezuela': 'VEN', 'Vietnam': 'VNM', 'West Bank & Gaza': 'PSE', 'Yemen': 'YEM',
    'Yugoslavia': None, 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE',
}

# Country centroids (ISO3 -> lat, lon, DISPLAY NAME) for in-frame labels on
# regional extracts. Sourced from the Google canonical country dataset; Plotly
# clips these to whatever geographic scope is in view, so only the countries
# inside the selected region are labelled.
COUNTRY_CENTROIDS = {
    'ABW': (12.52, -69.97, 'ARUBA'),
    'AFG': (33.94, 67.71, 'AFGHANISTAN'),
    'AGO': (-11.2, 17.87, 'ANGOLA'),
    'AIA': (18.22, -63.07, 'ANGUILLA'),
    'ALB': (41.15, 20.17, 'ALBANIA'),
    'AND': (42.55, 1.6, 'ANDORRA'),
    'ARE': (23.42, 53.85, 'UNITED ARAB EMIRATES'),
    'ARG': (-38.42, -63.62, 'ARGENTINA'),
    'ARM': (40.07, 45.04, 'ARMENIA'),
    'ASM': (-14.27, -170.13, 'AMERICAN SAMOA'),
    'ATA': (-75.25, -0.07, 'ANTARCTICA'),
    'ATF': (-49.28, 69.35, 'FRENCH SOUTHERN TERRITORIES'),
    'ATG': (17.06, -61.8, 'ANTIGUA AND BARBUDA'),
    'AUS': (-25.27, 133.78, 'AUSTRALIA'),
    'AUT': (47.52, 14.55, 'AUSTRIA'),
    'AZE': (40.14, 47.58, 'AZERBAIJAN'),
    'BDI': (-3.37, 29.92, 'BURUNDI'),
    'BEL': (50.5, 4.47, 'BELGIUM'),
    'BEN': (9.31, 2.32, 'BENIN'),
    'BFA': (12.24, -1.56, 'BURKINA FASO'),
    'BGD': (23.68, 90.36, 'BANGLADESH'),
    'BGR': (42.73, 25.49, 'BULGARIA'),
    'BHR': (25.93, 50.64, 'BAHRAIN'),
    'BHS': (25.03, -77.4, 'BAHAMAS'),
    'BIH': (43.92, 17.68, 'BOSNIA AND HERZEGOVINA'),
    'BLR': (53.71, 27.95, 'BELARUS'),
    'BLZ': (17.19, -88.5, 'BELIZE'),
    'BMU': (32.32, -64.76, 'BERMUDA'),
    'BOL': (-16.29, -63.59, 'BOLIVIA'),
    'BRA': (-14.24, -51.93, 'BRAZIL'),
    'BRB': (13.19, -59.54, 'BARBADOS'),
    'BRN': (4.54, 114.73, 'BRUNEI'),
    'BTN': (27.51, 90.43, 'BHUTAN'),
    'BVT': (-54.42, 3.41, 'BOUVET ISLAND'),
    'BWA': (-22.33, 24.68, 'BOTSWANA'),
    'CAF': (6.61, 20.94, 'CENTRAL AFRICAN REPUBLIC'),
    'CAN': (56.13, -106.35, 'CANADA'),
    'CCK': (-12.16, 96.87, 'COCOS [KEELING] ISLANDS'),
    'CHE': (46.82, 8.23, 'SWITZERLAND'),
    'CHL': (-35.68, -71.54, 'CHILE'),
    'CHN': (35.86, 104.2, 'CHINA'),
    'CIV': (7.54, -5.55, "CÔTE D'IVOIRE"),
    'CMR': (7.37, 12.35, 'CAMEROON'),
    'COD': (-4.04, 21.76, 'CONGO [DRC]'),
    'COG': (-0.23, 15.83, 'CONGO [REPUBLIC]'),
    'COK': (-21.24, -159.78, 'COOK ISLANDS'),
    'COL': (4.57, -74.3, 'COLOMBIA'),
    'COM': (-11.88, 43.87, 'COMOROS'),
    'CPV': (16.0, -24.01, 'CAPE VERDE'),
    'CRI': (9.75, -83.75, 'COSTA RICA'),
    'CUB': (21.52, -77.78, 'CUBA'),
    'CXR': (-10.45, 105.69, 'CHRISTMAS ISLAND'),
    'CYM': (19.51, -80.57, 'CAYMAN ISLANDS'),
    'CYP': (35.13, 33.43, 'CYPRUS'),
    'CZE': (49.82, 15.47, 'CZECH REPUBLIC'),
    'DEU': (51.17, 10.45, 'GERMANY'),
    'DJI': (11.83, 42.59, 'DJIBOUTI'),
    'DMA': (15.41, -61.37, 'DOMINICA'),
    'DNK': (56.26, 9.5, 'DENMARK'),
    'DOM': (18.74, -70.16, 'DOMINICAN REPUBLIC'),
    'DZA': (28.03, 1.66, 'ALGERIA'),
    'ECU': (-1.83, -78.18, 'ECUADOR'),
    'EGY': (26.82, 30.8, 'EGYPT'),
    'ERI': (15.18, 39.78, 'ERITREA'),
    'ESH': (24.22, -12.89, 'WESTERN SAHARA'),
    'ESP': (40.46, -3.75, 'SPAIN'),
    'EST': (58.6, 25.01, 'ESTONIA'),
    'ETH': (9.14, 40.49, 'ETHIOPIA'),
    'FIN': (61.92, 25.75, 'FINLAND'),
    'FJI': (-16.58, 179.41, 'FIJI'),
    'FLK': (-51.8, -59.52, 'FALKLAND ISLANDS [ISLAS MALVINAS]'),
    'FRA': (46.23, 2.21, 'FRANCE'),
    'FRO': (61.89, -6.91, 'FAROE ISLANDS'),
    'FSM': (7.43, 150.55, 'MICRONESIA'),
    'GAB': (-0.8, 11.61, 'GABON'),
    'GBR': (55.38, -3.44, 'UNITED KINGDOM'),
    'GEO': (42.32, 43.36, 'GEORGIA'),
    'GGY': (49.47, -2.59, 'GUERNSEY'),
    'GHA': (7.95, -1.02, 'GHANA'),
    'GIB': (36.14, -5.35, 'GIBRALTAR'),
    'GIN': (9.95, -9.7, 'GUINEA'),
    'GLP': (17.0, -62.07, 'GUADELOUPE'),
    'GMB': (13.44, -15.31, 'GAMBIA'),
    'GNB': (11.8, -15.18, 'GUINEA-BISSAU'),
    'GNQ': (1.65, 10.27, 'EQUATORIAL GUINEA'),
    'GRC': (39.07, 21.82, 'GREECE'),
    'GRD': (12.26, -61.6, 'GRENADA'),
    'GRL': (71.71, -42.6, 'GREENLAND'),
    'GTM': (15.78, -90.23, 'GUATEMALA'),
    'GUF': (3.93, -53.13, 'FRENCH GUIANA'),
    'GUM': (13.44, 144.79, 'GUAM'),
    'GUY': (4.86, -58.93, 'GUYANA'),
    'HKG': (22.4, 114.11, 'HONG KONG'),
    'HMD': (-53.08, 73.5, 'HEARD ISLAND AND MCDONALD ISLANDS'),
    'HND': (15.2, -86.24, 'HONDURAS'),
    'HRV': (45.1, 15.2, 'CROATIA'),
    'HTI': (18.97, -72.29, 'HAITI'),
    'HUN': (47.16, 19.5, 'HUNGARY'),
    'IDN': (-0.79, 113.92, 'INDONESIA'),
    'IMN': (54.24, -4.55, 'ISLE OF MAN'),
    'IND': (20.59, 78.96, 'INDIA'),
    'IOT': (-6.34, 71.88, 'BRITISH INDIAN OCEAN TERRITORY'),
    'IRL': (53.41, -8.24, 'IRELAND'),
    'IRN': (32.43, 53.69, 'IRAN'),
    'IRQ': (33.22, 43.68, 'IRAQ'),
    'ISL': (64.96, -19.02, 'ICELAND'),
    'ISR': (31.05, 34.85, 'ISRAEL'),
    'ITA': (41.87, 12.57, 'ITALY'),
    'JAM': (18.11, -77.3, 'JAMAICA'),
    'JEY': (49.21, -2.13, 'JERSEY'),
    'JOR': (30.59, 36.24, 'JORDAN'),
    'JPN': (36.2, 138.25, 'JAPAN'),
    'KAZ': (48.02, 66.92, 'KAZAKHSTAN'),
    'KEN': (-0.02, 37.91, 'KENYA'),
    'KGZ': (41.2, 74.77, 'KYRGYZSTAN'),
    'KHM': (12.57, 104.99, 'CAMBODIA'),
    'KIR': (-3.37, -168.73, 'KIRIBATI'),
    'KNA': (17.36, -62.78, 'SAINT KITTS AND NEVIS'),
    'KOR': (35.91, 127.77, 'SOUTH KOREA'),
    'KWT': (29.31, 47.48, 'KUWAIT'),
    'LAO': (19.86, 102.5, 'LAOS'),
    'LBN': (33.85, 35.86, 'LEBANON'),
    'LBR': (6.43, -9.43, 'LIBERIA'),
    'LBY': (26.34, 17.23, 'LIBYA'),
    'LCA': (13.91, -60.98, 'SAINT LUCIA'),
    'LIE': (47.17, 9.56, 'LIECHTENSTEIN'),
    'LKA': (7.87, 80.77, 'SRI LANKA'),
    'LSO': (-29.61, 28.23, 'LESOTHO'),
    'LTU': (55.17, 23.88, 'LITHUANIA'),
    'LUX': (49.82, 6.13, 'LUXEMBOURG'),
    'LVA': (56.88, 24.6, 'LATVIA'),
    'MAC': (22.2, 113.54, 'MACAU'),
    'MAR': (31.79, -7.09, 'MOROCCO'),
    'MCO': (43.75, 7.41, 'MONACO'),
    'MDA': (47.41, 28.37, 'MOLDOVA'),
    'MDG': (-18.77, 46.87, 'MADAGASCAR'),
    'MDV': (3.2, 73.22, 'MALDIVES'),
    'MEX': (23.63, -102.55, 'MEXICO'),
    'MHL': (7.13, 171.18, 'MARSHALL ISLANDS'),
    'MKD': (41.61, 21.75, 'MACEDONIA [FYROM]'),
    'MLI': (17.57, -4.0, 'MALI'),
    'MLT': (35.94, 14.38, 'MALTA'),
    'MMR': (21.91, 95.96, 'MYANMAR [BURMA]'),
    'MNE': (42.71, 19.37, 'MONTENEGRO'),
    'MNG': (46.86, 103.85, 'MONGOLIA'),
    'MNP': (17.33, 145.38, 'NORTHERN MARIANA ISLANDS'),
    'MOZ': (-18.67, 35.53, 'MOZAMBIQUE'),
    'MRT': (21.01, -10.94, 'MAURITANIA'),
    'MSR': (16.74, -62.19, 'MONTSERRAT'),
    'MTQ': (14.64, -61.02, 'MARTINIQUE'),
    'MUS': (-20.35, 57.55, 'MAURITIUS'),
    'MWI': (-13.25, 34.3, 'MALAWI'),
    'MYS': (4.21, 101.98, 'MALAYSIA'),
    'MYT': (-12.83, 45.17, 'MAYOTTE'),
    'NAM': (-22.96, 18.49, 'NAMIBIA'),
    'NCL': (-20.9, 165.62, 'NEW CALEDONIA'),
    'NER': (17.61, 8.08, 'NIGER'),
    'NFK': (-29.04, 167.95, 'NORFOLK ISLAND'),
    'NGA': (9.08, 8.68, 'NIGERIA'),
    'NIC': (12.87, -85.21, 'NICARAGUA'),
    'NIU': (-19.05, -169.87, 'NIUE'),
    'NLD': (52.13, 5.29, 'NETHERLANDS'),
    'NOR': (60.47, 8.47, 'NORWAY'),
    'NPL': (28.39, 84.12, 'NEPAL'),
    'NRU': (-0.52, 166.93, 'NAURU'),
    'NZL': (-40.9, 174.89, 'NEW ZEALAND'),
    'OMN': (21.51, 55.92, 'OMAN'),
    'PAK': (30.38, 69.35, 'PAKISTAN'),
    'PAN': (8.54, -80.78, 'PANAMA'),
    'PCN': (-24.7, -127.44, 'PITCAIRN ISLANDS'),
    'PER': (-9.19, -75.02, 'PERU'),
    'PHL': (12.88, 121.77, 'PHILIPPINES'),
    'PLW': (7.51, 134.58, 'PALAU'),
    'PNG': (-6.31, 143.96, 'PAPUA NEW GUINEA'),
    'POL': (51.92, 19.15, 'POLAND'),
    'PRI': (18.22, -66.59, 'PUERTO RICO'),
    'PRK': (40.34, 127.51, 'NORTH KOREA'),
    'PRT': (39.4, -8.22, 'PORTUGAL'),
    'PRY': (-23.44, -58.44, 'PARAGUAY'),
    'PSE': (31.95, 35.23, 'PALESTINIAN TERRITORIES'),
    'PYF': (-17.68, -149.41, 'FRENCH POLYNESIA'),
    'QAT': (25.35, 51.18, 'QATAR'),
    'REU': (-21.12, 55.54, 'RÉUNION'),
    'ROU': (45.94, 24.97, 'ROMANIA'),
    'RUS': (61.52, 105.32, 'RUSSIA'),
    'RWA': (-1.94, 29.87, 'RWANDA'),
    'SAU': (23.89, 45.08, 'SAUDI ARABIA'),
    'SDN': (12.86, 30.22, 'SUDAN'),
    'SEN': (14.5, -14.45, 'SENEGAL'),
    'SGP': (1.35, 103.82, 'SINGAPORE'),
    'SGS': (-54.43, -36.59, 'SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS'),
    'SHN': (-24.14, -10.03, 'SAINT HELENA'),
    'SJM': (77.55, 23.67, 'SVALBARD AND JAN MAYEN'),
    'SLB': (-9.65, 160.16, 'SOLOMON ISLANDS'),
    'SLE': (8.46, -11.78, 'SIERRA LEONE'),
    'SLV': (13.79, -88.9, 'EL SALVADOR'),
    'SMR': (43.94, 12.46, 'SAN MARINO'),
    'SOM': (5.15, 46.2, 'SOMALIA'),
    'SPM': (46.94, -56.27, 'SAINT PIERRE AND MIQUELON'),
    'SRB': (44.02, 21.01, 'SERBIA'),
    'STP': (0.19, 6.61, 'SÃO TOMÉ AND PRÍNCIPE'),
    'SUR': (3.92, -56.03, 'SURINAME'),
    'SVK': (48.67, 19.7, 'SLOVAKIA'),
    'SVN': (46.15, 15.0, 'SLOVENIA'),
    'SWE': (60.13, 18.64, 'SWEDEN'),
    'SWZ': (-26.52, 31.47, 'SWAZILAND'),
    'SYC': (-4.68, 55.49, 'SEYCHELLES'),
    'SYR': (34.8, 39.0, 'SYRIA'),
    'TCA': (21.69, -71.8, 'TURKS AND CAICOS ISLANDS'),
    'TCD': (15.45, 18.73, 'CHAD'),
    'TGO': (8.62, 0.82, 'TOGO'),
    'THA': (15.87, 100.99, 'THAILAND'),
    'TJK': (38.86, 71.28, 'TAJIKISTAN'),
    'TKL': (-8.97, -171.86, 'TOKELAU'),
    'TKM': (38.97, 59.56, 'TURKMENISTAN'),
    'TLS': (-8.87, 125.73, 'TIMOR-LESTE'),
    'TON': (-21.18, -175.2, 'TONGA'),
    'TTO': (10.69, -61.22, 'TRINIDAD AND TOBAGO'),
    'TUN': (33.89, 9.54, 'TUNISIA'),
    'TUR': (38.96, 35.24, 'TURKEY'),
    'TUV': (-7.11, 177.65, 'TUVALU'),
    'TWN': (23.7, 120.96, 'TAIWAN'),
    'TZA': (-6.37, 34.89, 'TANZANIA'),
    'UGA': (1.37, 32.29, 'UGANDA'),
    'UKR': (48.38, 31.17, 'UKRAINE'),
    'URY': (-32.52, -55.77, 'URUGUAY'),
    'USA': (37.09, -95.71, 'UNITED STATES'),
    'UZB': (41.38, 64.59, 'UZBEKISTAN'),
    'VAT': (41.9, 12.45, 'VATICAN CITY'),
    'VCT': (12.98, -61.29, 'SAINT VINCENT AND THE GRENADINES'),
    'VEN': (6.42, -66.59, 'VENEZUELA'),
    'VGB': (18.42, -64.64, 'BRITISH VIRGIN ISLANDS'),
    'VIR': (18.34, -64.9, 'U.S. VIRGIN ISLANDS'),
    'VNM': (14.06, 108.28, 'VIETNAM'),
    'VUT': (-15.38, 166.96, 'VANUATU'),
    'WLF': (-13.77, -177.16, 'WALLIS AND FUTUNA'),
    'WSM': (-13.76, -172.1, 'SAMOA'),
    'YEM': (15.55, 48.52, 'YEMEN'),
    'ZAF': (-30.56, 22.94, 'SOUTH AFRICA'),
    'ZMB': (-13.13, 27.85, 'ZAMBIA'),
    'ZWE': (-19.02, 29.15, 'ZIMBABWE'),
}

# ── Palettes (matched to the published charts) ───────────────────────────────
CREDITOR_ORDER = ['IMF', 'IBRD', 'IDA', 'IADB', 'Paris Club', 'China',
                  'Other official creditors', 'FC bank loans', 'FC bonds',
                  'Other private creditors', 'LC debt']
CREDITOR_COLORS = {
    'IMF': '#7b68a6', 'IBRD': '#ffff00', 'IDA': '#e8112d', 'IADB': '#3d7a99',
    'Paris Club': '#1a7a3c', 'China': '#2e75b6', 'Other official creditors': '#ffc000',
    'FC bank loans': '#ff9edb', 'FC bonds': '#8b6f47',
    'Other private creditors': '#4caf50', 'LC debt': '#2b7a9e',
}
DEBTOR_ORDER = ['Advanced economies', 'Emerging-market and frontier economies',
                'Heavily indebted poor countries', 'Other developing economies']
DEBTOR_COLORS = {
    'Advanced economies': '#e8112d',
    'Emerging-market and frontier economies': '#4dc3e6',
    'Heavily indebted poor countries': '#7030a0',
    'Other developing economies': '#ffc000',
}

st.markdown("""
<style>
    .metric-card { background:#1e2130; border-radius:10px; padding:16px 20px; text-align:center; }
    .metric-label { color:#9aa0b0; font-size:13px; margin-bottom:4px; }
    .metric-value { color:#f0f4ff; font-size:26px; font-weight:700; }
    .metric-sub { color:#6c8ebf; font-size:12px; margin-top:2px; }
    section[data-testid="stSidebar"] { background:#12151f; }
    .chart-note { color:#8b93a7; font-size:12px; line-height:1.5; margin-top:-6px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Parse the workbook's summary block (section A) and country block (section B)."""
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df_raw = pd.read_excel(os.path.join(base_dir, "data.xlsx"), header=None)

    DATA_START = 3
    years, n_cols = [], 0
    for c in range(DATA_START, df_raw.shape[1]):
        y = df_raw.iloc[0, c]
        if pd.isna(y):
            break
        s = str(y).strip()
        if s.endswith('p'):
            s = s[:-1]
        try:
            years.append(int(float(s)))
            n_cols += 1
        except (ValueError, TypeError):
            break

    def get_row(row_idx):
        vals = df_raw.iloc[row_idx, DATA_START:DATA_START + n_cols].values
        out = []
        for v in vals:
            try:
                out.append(float(v) if pd.notna(v) and str(v).strip() != '****' else np.nan)
            except (ValueError, TypeError):
                out.append(np.nan)
        return pd.Series(out, index=years)

    creditor_rows = {'Total': 6, 'IMF': 7, 'IBRD': 8, 'IDA': 9, 'IADB': 10,
                     'Paris Club': 11, 'China': 12, 'Other official creditors': 13,
                     'FC bank loans': 14, 'FC bonds': 15,
                     'Other private creditors': 16, 'LC debt': 17}
    df_creditors = pd.DataFrame({k: get_row(v) for k, v in creditor_rows.items()})

    debtor_rows = {'Total': 22, 'Advanced economies': 23,
                   'Emerging-market and frontier economies': 24,
                   'Heavily indebted poor countries': 25,
                   'Other developing economies': 26}
    df_debtors = pd.DataFrame({k: get_row(v) for k, v in debtor_rows.items()})

    df_rates = pd.DataFrame({
        '% of all Sovereigns': get_row(31),
        '% of World Public Debt': get_row(34),
        '% of EM/Other Developing GDP': get_row(35),
        '% of World GDP': get_row(36),
    })

    count_rows = {'Total in default': 40, 'IMF': 41, 'IBRD': 42, 'IDA': 43, 'IADB': 44,
                  'Paris Club': 45, 'China': 46, 'Other official creditors': 47,
                  'FC bank loans': 48, 'FC bonds': 49,
                  'Other private creditors': 50, 'LC debt': 51}
    df_counts = pd.DataFrame({k: get_row(v) for k, v in count_rows.items()})
    total_sovereigns = get_row(38)

    countries = []
    for i in range(66, len(df_raw)):
        idx_val = df_raw.iloc[i, 0]
        if pd.notna(idx_val) and isinstance(idx_val, (int, float)):
            name = str(df_raw.iloc[i, 1]).strip()
            vals = df_raw.iloc[i, DATA_START:DATA_START + n_cols].values
            ser = []
            for v in vals:
                try:
                    ser.append(float(v) if pd.notna(v) and str(v).strip() != '****' else np.nan)
                except (ValueError, TypeError):
                    ser.append(np.nan)
            countries.append({'name': name, 'total': ser})
    df_countries = pd.DataFrame([c['total'] for c in countries],
                                index=[c['name'] for c in countries], columns=years)

    return (df_creditors, df_debtors, df_rates, df_counts,
            total_sovereigns, df_countries, years)


@st.cache_data(show_spinner=False)
def plotly_png_bytes(fig_json, scale=2, width=1600, height=900):
    """Render a Plotly figure to static PNG bytes (requires kaleido)."""
    return pio.from_json(fig_json).to_image(format="png", scale=scale,
                                            width=width, height=height)


@st.cache_data(show_spinner=False)
def plotly_html_bytes(fig_json):
    """Return a lightweight interactive Plotly HTML file as UTF-8 bytes."""
    fig = pio.from_json(fig_json)
    return pio.to_html(
        fig, full_html=True, include_plotlyjs="cdn",
        config={"responsive": True, "displaylogo": False, "scrollZoom": True,
                "toImageButtonOptions": {"format": "png", "scale": 2}},
        default_width="100%", default_height="100%",
    ).encode("utf-8")


def figure_with_note(fig, note, on_white=False):
    """Return an export-ready copy of `fig`: restyled for a white page, with the
    note (if any) stamped in a legible band at the very bottom.

    The on-screen charts are dark-themed with a transparent background, so their
    light text disappears when a PNG is pasted onto a white surface such as
    Microsoft Word. For downloads we therefore force a white background and dark
    text/gridlines so everything stays visible, then bake in the note.
    """
    import copy
    import textwrap

    out = copy.deepcopy(fig)

    is_geo = bool(out.data) and out.data[0].type in ("choropleth", "scattergeo")
    INK = "#222222"
    GRID = "#e6e6e6"
    LINE = "#c8c8c8"

    # 1) Make the figure readable on a white page.
    if not is_geo:
        out.update_layout(template="plotly_white")
    out.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(color=INK),
        legend=dict(font=dict(color=INK)),
        title=dict(font=dict(color=INK)),
    )

    # Geo/map exports should keep the full canvas visually continuous with
    # the ocean. Plotly can otherwise leave white letterboxing around Mercator
    # regional maps when rendered at a different export aspect ratio.
    if is_geo:
        OCEAN = "#a9c7e8"
        out.update_layout(paper_bgcolor=OCEAN)
        out.update_geos(bgcolor=OCEAN, oceancolor=OCEAN, showocean=True)

    if not is_geo:
        out.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=LINE,
                         tickcolor=LINE, tickfont=dict(color=INK),
                         title=dict(font=dict(color=INK)))
        out.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=LINE,
                         tickcolor=LINE, tickfont=dict(color=INK),
                         title=dict(font=dict(color=INK)))
    if out.data and out.data[0].type == "pie":
        out.update_traces(outsidetextfont=dict(color=INK), selector=dict(type="pie"))
    for ann in out.layout.annotations:
        if ann.font is None or ann.font.color is None:
            ann.font.color = INK

    # Keep map legends inside the blue shaded geography in exported files.
    # Regional maps use Mercator; the World view uses equirectangular.
    if is_geo and out.layout.legend is not None:
        projection_type = str(
            getattr(getattr(out.layout.geo, 'projection', None), 'type', '') or ''
        ).lower()
        is_world_geo = projection_type == 'equirectangular'

        out.update_layout(
            legend=dict(
                x=0.03 if is_world_geo else 0.06,
                y=0.07 if is_world_geo else 0.19,
                xanchor='left',
                yanchor='bottom',
            )
        )

    note = (note or "").strip()
    if not note:
        return out

    lines = textwrap.wrap(note, width=120) or [note]
    line_px = 17

    leg = out.layout.legend
    bottom_legend = bool(leg is not None and leg.orientation == 'h'
                         and leg.y is not None and leg.y <= 0.05)
    legend_px = 48 if bottom_legend else 0
    gap = 22

    base_b = out.layout.margin.b if out.layout.margin.b is not None else 50
    out.update_layout(
        margin=dict(b=base_b + legend_px + gap + line_px * len(lines) + 14))

    out.add_annotation(
        text="<br>".join(lines),
        xref='paper', yref='paper', x=0.0, y=0.0,
        xanchor='left', yanchor='top',
        yshift=-(base_b + legend_px + gap),
        showarrow=False, align='left',
        font=dict(family='Arial', size=12.5, color='#2b2b2b'),
    )
    return out


def show_chart(fig, filename, key):
    """Display a Plotly chart with only user-entered notes."""
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"responsive": True, "displaylogo": False},
        key=f"chart_{key}",
    )

    custom_note = st.text_area(
        "Your notes",
        value="",
        key=f"user_note_{key}",
        placeholder="Type your notes here. They will appear in the exported chart/PDF.",
        height=90,
    ).strip()

    if custom_note:
        st.markdown(
            f"<div class='chart-note'>{custom_note}</div>",
            unsafe_allow_html=True,
        )

    if st.checkbox(
        "Prepare download",
        key=f"prepare_{key}",
        help="Enable this only when you want to export this chart as a file.",
    ):
        col_fmt, col_scale = st.columns([1, 1])

        with col_fmt:
            fmt = st.radio(
                "Format",
                ["HTML (interactive)", "PNG (image)"],
                key=f"fmt_{key}",
                horizontal=True,
            )

        base_name = filename.rsplit(".", 1)[0]
        on_white = str(fig.layout.paper_bgcolor or "").lower() in (
            "white", "#fff", "#ffffff"
        )

        export_fig = figure_with_note(
            fig,
            custom_note,
            on_white=on_white,
        )

        if custom_note:
            st.caption("Your note is included in the downloaded file.")

        if fmt.startswith("HTML"):
            st.download_button(
                "⬇️ Download interactive HTML",
                data=plotly_html_bytes(export_fig.to_json()),
                file_name=f"{base_name}.html",
                mime="text/html",
                key=f"download_html_{key}",
                help="The downloaded file loads Plotly from the internet when opened.",
            )
        else:
            with col_scale:
                scale = st.select_slider(
                    "Resolution",
                    options=[1, 2, 3, 4],
                    value=2,
                    format_func=lambda s: f"{s}x",
                    key=f"scale_{key}",
                    help="Higher values produce a larger, sharper image.",
                )

            try:
                is_geo_export = bool(export_fig.data) and export_fig.data[0].type in (
                    "choropleth", "scattergeo"
                )

                export_width = 1600
                export_height = 900

                if is_geo_export:
                    export_height = int(export_fig.layout.height or 900)

                    # PNG-only typography boost. Kaleido's scale parameter adds
                    # pixels but does not make labels larger relative to the map.
                    # Increase geo text and legend typography before rendering so
                    # downloaded maps remain readable when pasted into Word/PPT.
                    projection_type = str(
                        getattr(
                            getattr(export_fig.layout.geo, 'projection', None),
                            'type',
                            ''
                        ) or ''
                    ).lower()
                    is_world_export = projection_type == 'equirectangular'

                    if is_world_export:
                        export_width = 1800
                        export_height = max(int(export_fig.layout.height or 760), 1000)

                    for trace in export_fig.data:
                        if getattr(trace, 'type', None) != 'scattergeo':
                            continue

                        current_size = getattr(
                            getattr(trace, 'textfont', None), 'size', None
                        ) or 12

                        # World continent labels start larger and should be very
                        # prominent; regional country labels get a ~60% boost.
                        if is_world_export:
                            new_size = max(24, int(round(float(current_size) * 1.45)))
                        else:
                            new_size = max(17, int(round(float(current_size) * 1.65)))

                        trace.textfont.size = new_size
                        trace.textfont.family = 'Arial Black'

                    export_fig.update_layout(
                        font=dict(size=16),
                        legend=dict(
                            title=dict(
                                font=dict(size=18, family='Arial Black')
                            ),
                            font=dict(size=16, family='Arial Black'),
                            itemsizing='constant',
                            itemwidth=58,
                            tracegroupgap=8,
                        ),
                    )

                    # figure_with_note() increases the bottom margin. Preserve
                    # the map's original drawable height by adding that margin
                    # increase to the final PNG height instead of squeezing the map.
                    original_bottom = int(fig.layout.margin.b or 0)
                    export_bottom = int(export_fig.layout.margin.b or 0)
                    export_height += max(0, export_bottom - original_bottom)

                    # Re-pin the legend after final export sizing. Regional maps
                    # need a higher y position than the rectangular World map.
                    export_fig.update_layout(
                        legend=dict(
                            x=0.03 if is_world_export else 0.06,
                            y=0.07 if is_world_export else 0.19,
                            xanchor='left',
                            yanchor='bottom',
                        )
                    )

                st.download_button(
                    f"⬇️ Download PNG ({scale}x)",
                    data=plotly_png_bytes(
                        export_fig.to_json(),
                        scale=scale,
                        width=export_width,
                        height=export_height,
                    ),
                    file_name=f"{base_name}.png",
                    mime="image/png",
                    key=f"download_png_{key}",
                    help="Static image export of the chart, including only your note.",
                )
            except Exception as e:
                if "topojson" in str(e).lower():
                    st.error(
                        "The map needs to fetch its base geometry (topojson) from "
                        "cdn.plot.ly to render a PNG, and it couldn't be reached. "
                        "Use the HTML export and save a PNG from the camera icon instead."
                    )
                else:
                    st.error(
                        "PNG export needs the `kaleido` package. Install it with "
                        "`pip install kaleido==0.2.1`, then restart the app. "
                        "(HTML export works without it.)"
                    )
                st.caption(f"Details: {e}")


def dark(fig, height, **kw):
    """Shared dark-theme layout."""
    fig.update_layout(template='plotly_dark', height=height,
                      margin=dict(l=60, r=30, t=30, b=50),
                      hovermode='x unified', paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', **kw)
    return fig


(df_creditors, df_debtors, df_rates, df_counts,
 total_sovereigns, df_countries, years) = load_data()

LAST_OBS = max(y for y in years if pd.notna(df_creditors.loc[y, 'Total']))

y0, y1 = years[0], LAST_OBS


def span(lo=None, hi=None):
    a = max(y0, lo) if lo else y0
    b = min(y1, hi) if hi else y1
    return [y for y in years if a <= y <= b]


st.title("🌍 Sovereign Default Map")
st.caption(
    f"BoC–BoE Sovereign Default Database · Last observation: **{LAST_OBS}** · "
    f"{len(df_countries)} countries tracked"
)

# MAP_FORMAT_V2: reference-style regional maps with larger labels.

MAP_BINS = [0,100,1000,10000,25000,50000,np.inf]
MAP_LABELS = ['0 - 100','100 - 1,000','1,000 - 10,000','10,000 - 25,000','25,000 - 50,000','50,000+']
MAP_COLORS = {'0 - 100':'#fff200','100 - 1,000':'#f5a623','1,000 - 10,000':'#d98100','10,000 - 25,000':'#ed1c24','25,000 - 50,000':'#b5121b','50,000+':'#7a0000'}

def bin_label(v):
    if pd.isna(v) or v <= 0:
        return None
    for lo,hi,lab in zip(MAP_BINS[:-1],MAP_BINS[1:],MAP_LABELS):
        if lo < v <= hi:
            return lab
    return MAP_LABELS[-1]

REGION_BOUNDS = {
    'World': None,
    'Africa': dict(lon=(-20,55),lat=(-36,38)),
    'Asia': dict(lon=(30,180),lat=(-12,58)),
    'Europe': dict(lon=(-15, 68), lat=(28, 72)),

    # Canada and the United States. Mexico, Central America and the
    # Caribbean are included in the combined Latin America extract below.
    'North America': dict(lon=(-170,-50),lat=(24,82)),

    # Mexico + Central America + Caribbean + South America.
    'Latin America & Caribbean': dict(lon=(-118,-32),lat=(-58,33)),
}

REGION_HEIGHTS = {
    'World':760,
    'Africa':980,
    'Asia':880,
    'Europe':900,
    'North America':900,
    'Latin America & Caribbean':980,
}

REGION_OVERRIDES = {
    'Europe': {'GBR','IRL','ISL','PRT','ESP','FRA','BEL','NLD','LUX','DEU','CHE','AUT','ITA','MLT','DNK','NOR','SWE','FIN','EST','LVA','LTU','POL','CZE','SVK','HUN','SVN','HRV','BIH','SRB','MNE','MKD','ALB','GRC','BGR','ROU','MDA','UKR','BLR'},
    'Asia': {'RUS','TUR','GEO','ARM','AZE','CYP','KAZ'},

    # North America is kept as the Canada / United States extract.
    'North America': {'CAN','USA'},

    # Combined Mexico, Central America, Caribbean and South America extract.
    'Latin America & Caribbean': {
        'MEX',
        'BLZ','GTM','HND','SLV','NIC','CRI','PAN',
        'BHS','CUB','JAM','HTI','DOM','PRI','ABW','AIA','ATG','BRB','CUW',
        'DMA','GRD','KNA','LCA','SXM','TTO','VCT',
        'ARG','BOL','BRA','CHL','COL','ECU','GUY','PRY','PER','SUR','URY','VEN',
    },
}

def country_region(code,lat,lon):
    # Explicit membership takes priority where regional bounding boxes overlap.
    for rg in ['Europe','Asia','Latin America & Caribbean','North America']:
        if code in REGION_OVERRIDES.get(rg,set()):
            return rg

    for rg in ['Africa','Latin America & Caribbean','North America','Europe','Asia']:
        b = REGION_BOUNDS[rg]
        if b['lon'][0] <= lon <= b['lon'][1] and b['lat'][0] <= lat <= b['lat'][1]:
            return rg
    return 'Other'

opts = span() or years
c1,c2 = st.columns([2.5,1.5])
with c1:
    map_year = st.select_slider("Map year",options=opts,value=LAST_OBS if LAST_OBS in opts else opts[-1],key="map_year")
with c2:
    region = st.selectbox("Regional extract",list(REGION_BOUNDS),index=0,key="map_region")

st.caption(
    "Country polygons are always shown. Regional extracts use larger country "
    "labels while suppressing tiny or crowded names. Hidden country names "
    "remain available through hover and the table below."
)

rows = []
for name in df_countries.index:
    code = ISO3_MAP.get(name)
    centroid = COUNTRY_CENTROIDS.get(code) if code else None
    if not code or not centroid:
        continue
    lat,lon,display_name = centroid
    value = df_countries.loc[name,map_year]
    value = np.nan if pd.isna(value) else float(value)
    rows.append({'source_name':name,'country':display_name.title(),'label':display_name.upper(),'code':code,'lat':float(lat),'lon':float(lon),'value':value,'band':bin_label(value),'region':country_region(code,float(lat),float(lon))})

map_df = pd.DataFrame(rows)

MIDDLE_EAST_CODES = {
    'TUR','CYP','EGY','IRN','IRQ','SYR','LBN','ISR','PSE','JOR',
    'SAU','YEM','OMN','ARE','KWT','QAT','BHR',
}

if region == 'World':
    view_df = map_df.copy()
elif region == 'Asia':
    # Include Middle East sovereigns explicitly in Asia-Pacific. Several of
    # their centroids overlap the broad Europe/Africa bounds, so relying only
    # on country_region() can incorrectly drop them from this choropleth.
    view_df = map_df[
        (map_df['region'] == 'Asia') | map_df['code'].isin(MIDDLE_EAST_CODES)
    ].copy()
elif region == 'Europe':
    # Russia remains classified with Asia for the Asia-Pacific extract, but
    # also include it in Europe so its polygon uses the selected year's
    # shared six-category debt-default colour there as well.
    view_df = map_df[
        (map_df['region'] == 'Europe') | (map_df['code'] == 'RUS')
    ].copy()
else:
    view_df = map_df[map_df['region'] == region].copy()

positive = view_df[view_df['value'].fillna(0) > 0].copy().sort_values(['value','country'],ascending=[False,True])
positive['rank'] = np.arange(1,len(positive)+1)
rank_lookup = dict(zip(positive['code'],positive['rank']))
view_df['rank'] = view_df['code'].map(rank_lookup)

fig_map = go.Figure()
for lab in MAP_LABELS:
    # Dedicated legend key: this guarantees the same six categories, in the
    # same order and style, even when a selected region has no country in a band.
    fig_map.add_trace(go.Scattergeo(
        lon=[None], lat=[None], mode='markers',
        marker=dict(size=13, color=MAP_COLORS[lab], symbol='square'),
        name=f"\u2002{lab}\u2002",
        showlegend=True, legendgroup=lab, hoverinfo='skip',
    ))

    band_df = view_df[view_df['band'] == lab]
    if band_df.empty:
        continue

    customdata = np.column_stack([
        band_df['value'].map(lambda x:f"${x:,.0f}M"),
        band_df['rank'].map(lambda x:'' if pd.isna(x) else f"#{int(x)}")
    ])
    fig_map.add_trace(go.Choropleth(
        locations=band_df['code'], z=np.ones(len(band_df)),
        text=band_df['country'], customdata=customdata,
        colorscale=[[0,MAP_COLORS[lab]],[1,MAP_COLORS[lab]]],
        showscale=False, marker_line_color='#8c8c8c', marker_line_width=0.75,
        name=lab, showlegend=False, legendgroup=lab,
        hovertemplate='<b>%{text}</b><br>Debt in default: %{customdata[0]}<br>Regional order: %{customdata[1]}<extra></extra>'
    ))

SHORT_LABELS = {'United Kingdom':'UK','United States':'USA','Central African Republic':'CENTRAL AFRICAN<br>REPUBLIC','Democratic Republic Of The Congo':'DR CONGO','Congo [Drc]':'DR CONGO','Congo [Republic]':'CONGO','Bosnia And Herzegovina':'BOSNIA &<br>HERZ.','North Macedonia':'N. MACEDONIA','Papua New Guinea':'PAPUA NEW<br>GUINEA','Equatorial Guinea':'EQUATORIAL<br>GUINEA','Guinea-Bissau':'GUINEA-<br>BISSAU','South Africa':'SOUTH AFRICA','South Sudan':'SOUTH SUDAN','Saudi Arabia':'SAUDI ARABIA','North Korea':'NORTH KOREA','South Korea':'SOUTH KOREA','New Zealand':'NEW ZEALAND'}

LABEL_OFFSETS = {
    'Africa': {'GMB':(-2.5,0.5),'GNB':(-2.3,-0.7),'SLE':(-1.6,-0.8),'LBR':(-1.4,-1.0),'TGO':(0.0,-1.2),'BEN':(0.8,1.0),'RWA':(1.4,0.5),'BDI':(1.5,-0.8),'UGA':(0.8,1.2),'MWI':(1.1,-0.4),'SWZ':(1.0,-0.8),'LSO':(0.0,-1.4),'DJI':(1.4,0.4),'ERI':(0.7,1.0)},
    'Europe': {'BEL':(-1.7,0.7),'NLD':(0.0,1.3),'LUX':(1.3,-0.4),'CHE':(-1.1,-0.8),'AUT':(1.0,0.3),'SVN':(-0.8,-0.7),'HRV':(1.0,-0.5),'BIH':(1.5,0.2),'MNE':(0.5,-0.8),'SRB':(1.2,0.4),'MKD':(0.8,-0.9),'ALB':(-0.6,-0.7),'SVK':(0.7,0.7),'CZE':(-0.5,0.8),'MDA':(1.1,0.3)},
    'Asia': {'LBN':(-2.0,1.2),'ISR':(-2.0,-0.8),'PSE':(2.0,-1.0),'JOR':(2.0,0.7),'KWT':(1.8,1.0),'QAT':(1.8,-0.7),'BHR':(1.8,0.7),'SGP':(2.0,-1.0),'BRN':(2.0,0.8),'BGD':(2.0,1.0),'NPL':(-2.0,1.0),'LKA':(2.0,-1.5),'THA':(-2.2,1.0),'LAO':(-2.2,1.4),'KHM':(2.2,-1.2),'VNM':(2.5,0.4),'MYS':(2.5,-1.0)},
    'North America': {},
    'Latin America & Caribbean': {
        'BLZ':(-1.0,0.8),'GTM':(-1.0,0.3),'HND':(0.8,0.9),
        'SLV':(-1.5,-0.6),'NIC':(0.9,-0.3),'CRI':(-0.8,-0.8),'PAN':(1.2,-0.7),
        'CUB':(0.0,1.2),'JAM':(0.0,-1.0),'HTI':(-0.8,0.8),'DOM':(1.0,0.4),
        'TTO':(1.0,-0.5),
        'URY':(1.3,-0.5),'PRY':(1.0,0.8),'ECU':(-1.0,0.5),
        'GUY':(1.0,0.7),'SUR':(1.0,-0.5),
    },
}

REGION_LABEL_SIZE = {
    'World':10,
    'Africa':12,
    'Asia':11,
    'Europe':10,
    'North America':12,
    'Latin America & Caribbean':11,
}

REGION_HIDE_LABELS = {
    'North America': set(),
    'Africa': {
        # These Middle East sovereigns can fall inside the Africa crop. Keep
        # their polygons/default colours and hover data, but suppress text.
        'IRQ','LBN'
    },
    'Asia': {
        # Keep Asia-Pacific focused on APAC. Middle East polygons/default
        # colors remain visible where they intersect the crop, but their
        # names and inline default amounts are suppressed. Tiny APAC labels
        # below are also omitted to prevent crowding.
        'TUR','CYP','GEO','ARM','AZE',
        'EGY','IRN','IRQ','SYR','LBN','ISR','PSE','JOR',
        'SAU','YEM','OMN','ARE','KWT','QAT','BHR',
        'LAO','MMR','SGP','BRN'
    },
    'Latin America & Caribbean': {
        # Keep tiny island polygons/hover data but suppress overlapping text.
        # Venezuela is rendered separately as a callout below; Haiti stays unlabeled.
        'ABW','AIA','ATG','BHS','BRB','CUW','DMA','GRD','KNA','LCA','PRI','SXM','VCT',
        'VEN','HTI'
    },
}

REGION_ANCHOR_LABELS = {
    'North America': {'CAN','USA'},
    'Latin America & Caribbean': {'MEX','CUB','BRA','ARG','CHL','COL','PER'},
    'Europe': {'GBR','FRA','DEU','ESP','ITA'},
    'Africa': {'ZAF','NGA','EGY','DZA','ETH'},
    'Asia': {'CHN','IND','JPN','IDN'},
}

REGION_MAX_LABELS = {
    'North America':6,
    'Latin America & Caribbean':20,
    'Europe':18,
    'Africa':22,
    'Asia':14,
}

def format_country_label(row):
    country = row['country']
    name = SHORT_LABELS.get(country,country.upper())
    if '<br>' not in name and len(name) > 15:
        words = name.split()
        if len(words) >= 2:
            mid = len(words)//2
            name = ' '.join(words[:mid]) + '<br>' + ' '.join(words[mid:])
    if pd.notna(row['value']) and row['value'] >= 10000:
        return f"<b>{name}</b><br><b>${row['value']/1e3:,.1f}B</b>"
    return f"<b>{name}</b>"

# Use light, bold labels on the darker red debt bands. Dark labels remain
# clearer on no-default, yellow, and orange countries. This contrast rule
# is shared by all regional extracts and carries through to PNG exports.
DARK_LABEL_BANDS = {
    '10,000 - 25,000',
    '25,000 - 50,000',
    '50,000+',
}

if region == 'World':
    CONTINENT_LABELS = pd.DataFrame([
        {'name':'<b>NORTH AMERICA</b>','lat':47,'lon':-107},
        {'name':'<b>SOUTH AMERICA</b>','lat':-17,'lon':-61},
        {'name':'<b>EUROPE</b>','lat':51,'lon':15},
        {'name':'<b>AFRICA</b>','lat':3,'lon':20},
        {'name':'<b>ASIA</b>','lat':42,'lon':92},
        {'name':'<b>AUSTRALIA</b>','lat':-27,'lon':134},
    ])
    fig_map.add_trace(go.Scattergeo(
        lon=CONTINENT_LABELS['lon'],
        lat=CONTINENT_LABELS['lat'],
        text=CONTINENT_LABELS['name'],
        mode='text',
        showlegend=False,
        hoverinfo='skip',
        textfont=dict(color='#2f2f2f',size=16,family='Arial Black'),
    ))
elif region == 'Europe':
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
    europe_default_codes = set(
        view_df.loc[view_df['value'].fillna(0) > 0, 'code'].dropna()
    )
    europe_visible_codes = europe_default_codes | {'GRC'}

    for code in EUROPE_LABEL_CODES:
        if code not in europe_visible_codes:
            continue
        if code not in COUNTRY_CENTROIDS:
            continue
        default_lat, default_lon, _ = COUNTRY_CENTROIDS[code]
        plot_lon, plot_lat = EUROPE_LABEL_POSITIONS.get(
            code, (default_lon, default_lat)
        )
        label_text = f"<b>{EUROPE_LABEL_NAMES.get(code, code)}</b>"
        if code in {'UKR', 'BLR', 'RUS'}:
            value_match = view_df.loc[view_df['code'] == code, 'value']
            if not value_match.empty and pd.notna(value_match.iloc[0]) and float(value_match.iloc[0]) > 0:
                default_value = float(value_match.iloc[0])
                if default_value >= 1000:
                    value_text = f"${default_value/1e3:,.1f}B"
                else:
                    value_text = f"${default_value:,.0f}M"
                label_text += f"<br><b>{value_text}</b>"

        europe_labels.append({
            'code': code,
            'text': label_text,
            'lon': plot_lon,
            'lat': plot_lat,
        })

    europe_label_df = pd.DataFrame(europe_labels)
    europe_band_lookup = dict(zip(view_df['code'], view_df['band']))
    europe_label_df['band'] = europe_label_df['code'].map(europe_band_lookup)
    europe_label_df['light_text'] = europe_label_df['band'].isin(DARK_LABEL_BANDS)

    for light_text, text_color, font_family in [
        (False, '#222222', 'Arial Black'),
        (True, '#ffffff', 'Arial Black'),
    ]:
        europe_part = europe_label_df[(europe_label_df['light_text'] == light_text) & (europe_label_df['code'] != 'RUS')]
        if europe_part.empty:
            continue
        fig_map.add_trace(go.Scattergeo(
            lon=europe_part['lon'],
            lat=europe_part['lat'],
            text=europe_part['text'],
            mode='text',
            showlegend=False,
            hoverinfo='skip',
            textfont=dict(
                color=text_color,
                size=9,
                family=font_family,
            )
        ))

    # Russia gets its own larger label so both the name and default amount
    # remain easy to read on-screen and in PNG exports.
    russia_label = europe_label_df[europe_label_df['code'] == 'RUS']
    if not russia_label.empty:
        russia_row = russia_label.iloc[0]
        russia_color = '#ffffff' if bool(russia_row['light_text']) else '#222222'
        fig_map.add_trace(go.Scattergeo(
            lon=[russia_row['lon']],
            lat=[russia_row['lat']],
            text=[russia_row['text']],
            mode='text',
            showlegend=False,
            hoverinfo='skip',
            textfont=dict(
                color=russia_color,
                size=12,
                family='Arial Black',
            )
        ))

elif not view_df.empty:
    label_df = view_df.copy()
    hidden_codes = REGION_HIDE_LABELS.get(region,set())
    anchor_codes = REGION_ANCHOR_LABELS.get(region,set())
    label_df['has_default'] = label_df['value'].fillna(0) > 0
    label_df['is_anchor'] = label_df['code'].isin(anchor_codes)
    label_df = label_df[label_df['has_default'] | label_df['is_anchor']].copy()
    label_df = label_df[~label_df['code'].isin(hidden_codes)].copy()
    label_df['_label_value'] = label_df['value'].fillna(0)
    label_df = label_df.sort_values(['has_default','_label_value','is_anchor','country'],ascending=[False,False,False,True]).head(REGION_MAX_LABELS.get(region,20)).copy()
    label_df['plot_lon'] = label_df['lon']
    label_df['plot_lat'] = label_df['lat']
    if region == 'North America':
        manual_positions = {'CAN':(-106.0,51.0),'USA':(-98.0,38.0),'MEX':(-102.0,23.5)}
        for idx,row in label_df.iterrows():
            if row['code'] in manual_positions:
                label_df.at[idx,'plot_lon'],label_df.at[idx,'plot_lat'] = manual_positions[row['code']]
    region_offsets = LABEL_OFFSETS.get(region,{})
    for idx,row in label_df.iterrows():
        if region == 'North America' and row['code'] in {'CAN','USA','MEX'}:
            continue
        if row['code'] in region_offsets:
            dx,dy = region_offsets[row['code']]
            label_df.at[idx,'plot_lon'] += dx
            label_df.at[idx,'plot_lat'] += dy
    label_df['map_text'] = label_df.apply(format_country_label,axis=1)
    label_df['light_text'] = label_df['band'].isin(DARK_LABEL_BANDS)
    if not label_df.empty:
        for light_text, text_color, font_family in [
            (False, '#222222', 'Arial Black'),
            (True, '#ffffff', 'Arial Black'),
        ]:
            label_part = label_df[label_df['light_text'] == light_text]
            if label_part.empty:
                continue
            fig_map.add_trace(go.Scattergeo(
                lon=label_part['plot_lon'],
                lat=label_part['plot_lat'],
                text=label_part['map_text'],
                mode='text',
                showlegend=False,
                hoverinfo='skip',
                textfont=dict(
                    color=text_color,
                    size=REGION_LABEL_SIZE.get(region,11),
                    family=font_family,
                )
            ))

if region == 'Latin America & Caribbean':
    LATAM_CALLOUTS = {
        'VEN': dict(
            # Keep the label close to Venezuela; the connector starts just
            # below the amount so the text and arrow read as one callout.
            label_lon=-58.5, label_lat=13.2,
            marker_symbol='triangle-left'
        ),
    }

    for code, spec in LATAM_CALLOUTS.items():
        row_match = view_df[view_df['code'] == code]
        if row_match.empty:
            continue
        row = row_match.iloc[0]
        if pd.isna(row['value']) or float(row['value']) <= 0:
            continue

        target_lat, target_lon, display_name = COUNTRY_CENTROIDS[code]
        default_value = float(row['value'])
        if default_value >= 1000:
            value_text = f"${default_value/1e3:,.1f}B"
        else:
            value_text = f"${default_value:,.0f}M"

        callout_text = (
            f"<b>{display_name}</b>"
            f"<br><b>{value_text}</b>"
        )

        # Start the connector immediately below the two-line label so the
        # Venezuela text/amount is visibly connected to the arrow.
        line_start_lon = spec['label_lon'] - 0.8
        line_start_lat = spec['label_lat'] - 1.8
        fig_map.add_trace(go.Scattergeo(
            lon=[line_start_lon, target_lon],
            lat=[line_start_lat, target_lat],
            mode='lines',
            line=dict(color='#111111', width=1.5),
            showlegend=False, hoverinfo='skip',
        ))

        # Explicit arrowhead at the country end makes the pointer clear even
        # after Kaleido downsizes the map for a PNG.
        fig_map.add_trace(go.Scattergeo(
            lon=[target_lon], lat=[target_lat],
            mode='markers',
            marker=dict(
                size=8, color='#111111',
                symbol=spec['marker_symbol'],
                line=dict(width=0),
            ),
            showlegend=False, hoverinfo='skip',
        ))

        # The number is always shown on its own bold line for readability.
        fig_map.add_trace(go.Scattergeo(
            lon=[spec['label_lon']], lat=[spec['label_lat']],
            text=[callout_text], mode='text',
            textfont=dict(color='#111111', size=13, family='Arial Black'),
            showlegend=False, hoverinfo='skip',
        ))

geo_kw = dict(showframe=False,showcoastlines=True,coastlinecolor='#8c8c8c',coastlinewidth=0.75,showland=True,landcolor='#f2f2f2',showocean=True,oceancolor='#a9c7e8',showlakes=True,lakecolor='#a9c7e8',showcountries=True,countrycolor='#8c8c8c',countrywidth=0.75,bgcolor='white',projection_type='equirectangular' if region == 'World' else 'mercator')
if region == 'World':
    geo_kw.update(
        lonaxis=dict(range=[-180,180],showgrid=False),
        lataxis=dict(range=[-60,85],showgrid=False),
    )
else:
    b = REGION_BOUNDS[region]
    geo_kw.update(lonaxis=dict(range=list(b['lon']),showgrid=False),lataxis=dict(range=list(b['lat']),showgrid=False))

legend_title = (
    f"<b>{map_year} total debt in default<br>by country<br>(US$ millions)</b>"
)
is_world = region == 'World'
fig_map.update_layout(
    height=REGION_HEIGHTS.get(region,860),
    geo=geo_kw,
    title=dict(text=''),
    legend=dict(
        title=dict(
            text=legend_title,
            font=dict(size=14,color='#111111',family='Arial Black'),
        ),
        x=0.03 if is_world else 0.06,
        y=0.07 if is_world else 0.19,
        xanchor='left',
        yanchor='bottom',
        bgcolor='rgba(255,255,255,0.98)',
        bordercolor='#b8b8b8',
        borderwidth=1.2,
        font=dict(size=12,color='#111111',family='Arial Black'),
        itemsizing='constant',
        itemwidth=52,
        tracegroupgap=6,
        traceorder='normal',
    ),
    margin=dict(l=0,r=0,t=8,b=0),
    paper_bgcolor='white',
    font=dict(family='Arial',size=13,color='#222222'),
)
map_region_slug = region.lower().replace('&', 'and').replace(' ', '_')
show_chart(fig_map,f"debt_default_map_{map_region_slug}_{map_year}.html","cmap")

st.caption(
    f"Source: BoC–BoE Sovereign Default Database · Last update: July 22, 2026 · "
    f"Last observation: {LAST_OBS}"
)
