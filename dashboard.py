import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

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
    if not is_geo:
        out.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=LINE,
                         tickcolor=LINE, tickfont=dict(color=INK),
                         title=dict(font=dict(color=INK)))
        out.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=LINE,
                         tickcolor=LINE, tickfont=dict(color=INK),
                         title=dict(font=dict(color=INK)))
    # Pie labels sitting outside the slices follow the layout font; make sure any
    # that were light are now dark. Inside labels keep Plotly's auto contrast.
    if out.data and out.data[0].type == "pie":
        out.update_traces(outsidetextfont=dict(color=INK), selector=dict(type="pie"))
    # Existing annotations (e.g. subplot panel titles) that had no explicit
    # colour would inherit the old light template — pin them dark.
    for ann in out.layout.annotations:
        if ann.font is None or ann.font.color is None:
            ann.font.color = INK

    # 2) Stamp the note in a band at the very bottom.
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
    """Display a Plotly chart with only user-entered notes.

    The note typed by the user is displayed below the chart and included
    in exported HTML/PNG output. No hard-coded/source notes are displayed
    or exported.
    """
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

        # ONLY the user's note is stamped into the export.
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
                st.download_button(
                    f"⬇️ Download PNG ({scale}x)",
                    data=plotly_png_bytes(export_fig.to_json(), scale=scale),
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

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Sovereign Defaults")
    st.markdown("*BoC–BoE Sovereign Default Database*")
    st.markdown("*Last Update: July 22, 2026*")
    st.divider()
    year_range = st.slider("Year range", min_value=years[0], max_value=years[-1],
                           value=(1976, LAST_OBS))
    st.caption("Each chart clamps this range to the period it covers.")
    st.divider()
    st.markdown("**Creditors to show** (Charts 3 & 5)")
    sel_creditors = st.multiselect("Creditors", options=CREDITOR_ORDER,
                                   default=CREDITOR_ORDER, label_visibility="collapsed")

y0, y1 = year_range


def span(lo=None, hi=None):
    a = max(y0, lo) if lo else y0
    b = min(y1, hi) if hi else y1
    return [y for y in years if a <= y <= b]


# ── Header + KPIs ────────────────────────────────────────────────────────────
st.title("🌍 Sovereign Default Database")
st.caption(f"Last observation: **{LAST_OBS}** · {len(df_countries)} countries tracked "
           f"· showing **{y0}–{y1}**")

k1, k2, k3, k4 = st.columns(4)
tot_latest = df_creditors.loc[LAST_OBS, 'Total']
rate_latest = df_rates.loc[LAST_OBS, '% of all Sovereigns']
n_latest = df_counts.loc[LAST_OBS, 'Total in default']
gdp_latest = df_rates.loc[LAST_OBS, '% of World GDP']
for col, lab, val, sub in [
    (k1, f"Total debt in default ({LAST_OBS})", f"${tot_latest/1e3:,.0f}B", "US$ billions"),
    (k2, f"Sovereigns in default ({LAST_OBS})", f"{int(n_latest)}", f"of {int(total_sovereigns[LAST_OBS])} sovereigns"),
    (k3, "Share of all sovereigns", f"{rate_latest:.1f}%", "in default"),
    (k4, "Share of world GDP", f"{gdp_latest:.2f}%", "debt in default"),
]:
    with col:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">{lab}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab_a, tab_b, tab_c, tab_map = st.tabs([
    "📊 Charts 1–3", "📈 Charts 4–6", "📉 Charts 7–8", "🗺️ Map"])

# ═══ CHART 1: Share of debt in default by creditor (pie) ═════════════════════
with tab_a:
    st.subheader(f"Chart 1: Total share of debt in default by creditor, {LAST_OBS}")
    pie_year = st.select_slider("Year", options=[y for y in years if pd.notna(df_creditors.loc[y, 'Total'])],
                                value=LAST_OBS, key="c1_year")
    total_pie = df_creditors.loc[pie_year, 'Total']
    labels, vals, cols = [], [], []
    for c in CREDITOR_ORDER:
        v = df_creditors.loc[pie_year, c]
        if pd.notna(v) and v > 0:
            labels.append(c); vals.append(v); cols.append(CREDITOR_COLORS[c])
    fig1 = go.Figure(go.Pie(
        labels=labels, values=vals, marker_colors=cols, sort=False,
        textinfo='label+percent', textposition='auto',
        insidetextfont=dict(size=12), hole=0,
        hovertemplate='<b>%{label}</b><br>$%{value:,.0f}M<br>%{percent}<extra></extra>'))
    fig1.update_layout(template='plotly_dark', height=520, showlegend=True,
                       legend=dict(orientation='v', x=1.02, y=0.5, font=dict(size=11)),
                       margin=dict(l=20, r=20, t=20, b=20),
                       paper_bgcolor='rgba(0,0,0,0)')
    show_chart(fig1, f"chart1_share_by_creditor_{pie_year}.html", "c1")

    # ═══ CHART 2: Default rates on FC bonds and bank loans (panels a & b) ════
    st.divider()
    st.subheader("Chart 2: Sovereign default rates on foreign currency bonds and bank loans")
    bonds_ct = df_counts['FC bonds']
    loans_ct = df_counts['FC bank loans']
    rate_bonds = (bonds_ct / total_sovereigns * 100)
    rate_both = ((bonds_ct + loans_ct) / total_sovereigns * 100)

    s = span()
    s2 = span(2020)
    y_max = float(np.nanmax([rate_both.loc[s].max(), rate_both.loc[s2].max()])) if s and s2 else 10
    y_top = max(5, np.ceil(y_max / 5) * 5)

    fig2 = make_subplots(
        rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.06,
        column_widths=[0.62, 0.38],
        subplot_titles=(f'a. Sovereign default rates, {s[0]}–{s[-1]}',
                        f'b. Sovereign default rates, {s2[0]}–{s2[-1]}'))

    for col, sp in [(1, s), (2, s2)]:
        fig2.add_trace(go.Scatter(
            x=sp, y=rate_bonds.loc[sp], name='Foreign currency bonds',
            line=dict(color='#c00000', width=2.5), legendgroup='bonds',
            showlegend=(col == 1),
            hovertemplate='%{x}: %{y:.1f}%<extra>FC bonds</extra>'), row=1, col=col)
        fig2.add_trace(go.Scatter(
            x=sp, y=rate_both.loc[sp], name='Foreign currency bonds and bank loans',
            line=dict(color='#00b0f0', width=2.5), legendgroup='both',
            showlegend=(col == 1),
            hovertemplate='%{x}: %{y:.1f}%<extra>FC bonds and bank loans</extra>'),
            row=1, col=col)

    dark(fig2, 430, legend=dict(orientation='h', y=-0.16, x=0.5, xanchor='center'))
    fig2.update_yaxes(title_text='% of all sovereigns', range=[0, y_top], row=1, col=1)
    fig2.update_yaxes(range=[0, y_top], showticklabels=True, row=1, col=2)
    fig2.update_xaxes(dtick=1, row=1, col=2)
    for ann in fig2.layout.annotations:
        ann.font.size = 13
    show_chart(fig2, "chart2_default_rates.html", "c2")

    # ═══ CHART 3: Total sovereign debt in default by creditor ════════════════
    st.divider()
    s3 = span(1976)

    # Cleaner stacking order: largest / most important series are placed lower
    # in the stack so their time trends are easier to follow.
    CHART3_ORDER = [
        'FC bonds',
        'FC bank loans',
        'Paris Club',
        'China',
        'Other official creditors',
        'LC debt',
        'Other private creditors',
        'IMF',
        'IBRD',
        'IDA',
        'IADB',
    ]

    # More restrained palette. Major creditor groups remain distinct while the
    # smaller series use quieter tones so they do not compete visually.
    CHART3_COLORS = {
        'FC bonds': '#8c6d46',
        'FC bank loans': '#d98bbd',
        'Paris Club': '#2e7d32',
        'China': '#3f7fbf',
        'Other official creditors': '#e0a100',
        'LC debt': '#3d87a6',
        'Other private creditors': '#5fa85f',
        'IMF': '#8172a8',
        'IBRD': '#c6b700',
        'IDA': '#b94b55',
        'IADB': '#6c9db5',
    }

    st.subheader(f"Sovereign Debt in Default by Creditor, {s3[0]}–{s3[-1]}")
    st.caption("US$ billions")

    fig3 = go.Figure()

    visible_creditors = [c for c in CHART3_ORDER if c in sel_creditors]

    for c in visible_creditors:
        fig3.add_trace(
            go.Bar(
                x=s3,
                y=df_creditors.loc[s3, c].fillna(0) / 1e3,
                name=c,
                marker_color=CHART3_COLORS[c],
                hovertemplate="<b>%{x}</b><br>" + c + ": $%{y:,.1f}B<extra></extra>",
            )
        )

    # Dynamic peak annotations so the chart remains useful if the selected
    # year range changes.
    total_visible = (
        df_creditors.loc[s3, visible_creditors].fillna(0).sum(axis=1) / 1e3
        if visible_creditors else pd.Series(index=s3, dtype=float)
    )

    annotation_candidates = []
    if not total_visible.empty:
        early_years = [y for y in total_visible.index if 1988 <= y <= 1995]
        if early_years:
            early = total_visible.loc[early_years]
            annotation_candidates.append(
                (int(early.idxmax()), float(early.max()), "Early-1990s peak")
            )

        euro_years = [y for y in total_visible.index if 2010 <= y <= 2014]
        if euro_years:
            euro = total_visible.loc[euro_years]
            annotation_candidates.append(
                (int(euro.idxmax()), float(euro.max()), "Euro-area crisis period")
            )

        recent_years = [y for y in total_visible.index if 2020 <= y <= s3[-1]]
        if recent_years:
            recent = total_visible.loc[recent_years]
            annotation_candidates.append(
                (int(recent.idxmax()), float(recent.max()), "Recent rise")
            )

    fig3.update_layout(
        template="plotly_white",
        height=560,
        barmode="stack",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=70, r=35, t=35, b=125),
        hovermode="x unified",
        font=dict(color="#222222", size=12),
        yaxis=dict(
            title="US$ billions",
            gridcolor="rgba(0,0,0,0.10)",
            gridwidth=0.8,
            zeroline=False,
            showline=False,
            tickfont=dict(color="#444444"),
        ),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0)",
            zeroline=False,
            showline=False,
            tickfont=dict(color="#444444"),
            tickmode="linear",
            dtick=10,
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#333333"),
            traceorder="normal",
            itemwidth=55,
        ),
    )

    for i, (yr, val, label) in enumerate(annotation_candidates[:3]):
        fig3.add_annotation(
            x=yr,
            y=val,
            text=label,
            showarrow=True,
            arrowhead=2,
            arrowsize=0.8,
            arrowwidth=1,
            arrowcolor="#666666",
            ax=0,
            ay=-35 - (i % 2) * 10,
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor="rgba(0,0,0,0.12)",
            borderwidth=1,
            font=dict(size=10.5, color="#333333"),
        )

    # If categories are filtered out, make that explicit so the remaining stack
    # is not mistaken for the full total.
    if len(visible_creditors) < len(CHART3_ORDER):
        st.caption(
            "Filtered view: one or more creditor categories are hidden. "
            "The stacked bars therefore represent only the selected creditors."
        )

    show_chart(fig3, "chart3_debt_by_creditor.html", "c3")

# ═══ CHARTS 4–6 ══════════════════════════════════════════════════════════════
with tab_b:
    s4 = span(1976)
    st.subheader(f"Chart 4: Sovereign debt in default by debtor, {s4[0]}–{s4[-1]}")
    fig4 = go.Figure()
    for d in DEBTOR_ORDER:
        fig4.add_trace(go.Bar(x=s4, y=df_debtors.loc[s4, d].fillna(0) / 1e3,
                              name=d, marker_color=DEBTOR_COLORS[d]))
    dark(fig4, 460, barmode='stack', yaxis=dict(title='US$ billions'),
         legend=dict(orientation='h', y=-0.16, font=dict(size=10)))
    show_chart(fig4, "chart4_debt_by_debtor.html", "c4")

    st.divider()
    s5 = span(1960)
    st.subheader(f"Chart 5: Proportion of debt in default by creditor, {s5[0]}–{s5[-1]}")
    shares = df_creditors.loc[s5, CREDITOR_ORDER].fillna(0)
    denom = shares.sum(axis=1).replace(0, np.nan)
    shares = shares.div(denom, axis=0) * 100
    fig5 = go.Figure()
    for c in CREDITOR_ORDER:
        if c in sel_creditors:
            fig5.add_trace(go.Scatter(
                x=s5, y=shares[c], name=c, mode='lines', stackgroup='one',
                line=dict(width=0.5, color=CREDITOR_COLORS[c]),
                fillcolor=CREDITOR_COLORS[c],
                hovertemplate='%{y:.1f}%<extra>' + c + '</extra>'))
    dark(fig5, 520, yaxis=dict(title='%', range=[0, 100]),
         legend=dict(orientation='h', y=-0.16, font=dict(size=10)))
    show_chart(fig5, "chart5_proportion_by_creditor.html", "c5")

    st.divider()
    s6 = span(2000)
    st.subheader(f"Chart 6: Official loans in default for Paris Club and China, {s6[0]}–{s6[-1]}")
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(x=s6, y=df_creditors.loc[s6, 'Paris Club'].fillna(0) / 1e3,
                          name='Paris Club', marker_color='#ff0000'))
    fig6.add_trace(go.Bar(x=s6, y=df_creditors.loc[s6, 'China'].fillna(0) / 1e3,
                          name='China', marker_color='#5b9bd5'))
    dark(fig6, 440, barmode='stack', yaxis=dict(title='US$ billions'),
         xaxis=dict(dtick=1), legend=dict(orientation='h', y=-0.2))
    show_chart(fig6, "chart6_paris_club_china.html", "c6")


# ═══ CHARTS 7–8 ══════════════════════════════════════════════════════════════
with tab_c:
    s7 = span(1980)
    st.subheader(f"Chart 7: Sovereign debt in default as a share of global public debt "
                 f"and global GDP, {s7[0]}–{s7[-1]}")
    fig7 = go.Figure()
    for col, color, name in [
        ('% of World Public Debt', '#a52929',
         'Defaulted global public debt as a share of global public debt'),
        ('% of World GDP', '#2e9bd6',
         'Defaulted global public debt as a share of world GDP'),
        ('% of EM/Other Developing GDP', '#f5a623',
         'Defaulted emerging-market public debt as a share of emerging-market GDP'),
    ]:
        ser = df_rates.loc[s7, col]
        fig7.add_trace(go.Scatter(x=s7, y=ser, name=name, mode='lines',
                                  line=dict(color=color, width=2.5)))
    dark(fig7, 480, yaxis=dict(title='%'),
         legend=dict(orientation='h', y=-0.22, font=dict(size=10)))
    show_chart(fig7, "chart7_share_of_debt_and_gdp.html", "c7")

    st.divider()
    s8 = span(1976)
    st.subheader(f"Chart 8: Number of sovereign defaults, {s8[0]}–{s8[-1]}")
    fig8 = go.Figure()
    for col, color in [('FC bank loans', '#2e75b6'), ('FC bonds', '#c0504d'),
                       ('LC debt', '#9bbb59')]:
        fig8.add_trace(go.Scatter(x=s8, y=df_counts.loc[s8, col], name=col, mode='lines',
                                  line=dict(color=color, width=2.5)))
    dark(fig8, 460, yaxis=dict(title='Number of sovereigns'),
         legend=dict(orientation='h', y=-0.18))
    show_chart(fig8, "chart8_number_of_defaults.html", "c8")

# ═══ MAP: Global debt in default ═════════════════════════════════════════════
with tab_map:
    st.subheader("Figure A-1: Global debt in default")

    # Match the published regional-map style: six discrete debt bands, light-blue
    # water, light land for no/zero debt, thin grey borders, and country names
    # printed directly on the map.
    MAP_BINS = [0, 100, 1000, 10000, 25000, 50000, np.inf]
    MAP_LABELS = [
        '0 - 100',
        '100 - 1,000',
        '1,000 - 10,000',
        '10,000 - 25,000',
        '25,000 - 50,000',
        '50,000+',
    ]
    MAP_COLORS = {
        '0 - 100': '#fff200',
        '100 - 1,000': '#f5a623',
        '1,000 - 10,000': '#d98100',
        '10,000 - 25,000': '#ed1c24',
        '25,000 - 50,000': '#b5121b',
        '50,000+': '#7a0000',
    }

    def bin_label(v):
        if pd.isna(v) or v <= 0:
            return None
        for lo, hi, lab in zip(MAP_BINS[:-1], MAP_BINS[1:], MAP_LABELS):
            if lo < v <= hi:
                return lab
        return MAP_LABELS[-1]

    # Explicit geographic extents make regional extracts deterministic rather
    # than depending on Plotly's broad continent scope.
    REGION_BOUNDS = {
        'World': None,
        'Africa': dict(lon=(-22, 55), lat=(-38, 38)),
        'Asia': dict(lon=(25, 180), lat=(-12, 80)),
        'Europe': dict(lon=(-25, 45), lat=(34, 72)),
        'North America': dict(lon=(-170, -50), lat=(5, 85)),
        'South America': dict(lon=(-85, -30), lat=(-60, 15)),
    }

    REGION_OVERRIDES = {
        'Europe': {'GBR', 'IRL', 'ISL', 'PRT', 'ESP', 'FRA', 'BEL', 'NLD', 'LUX', 'DEU',
                   'CHE', 'AUT', 'ITA', 'MLT', 'DNK', 'NOR', 'SWE', 'FIN', 'EST', 'LVA',
                   'LTU', 'POL', 'CZE', 'SVK', 'HUN', 'SVN', 'HRV', 'BIH', 'SRB', 'MNE',
                   'MKD', 'ALB', 'GRC', 'BGR', 'ROU', 'MDA', 'UKR', 'BLR'},
        'Asia': {'RUS', 'TUR', 'GEO', 'ARM', 'AZE', 'CYP', 'KAZ'},
    }

    def country_region(code, lat, lon):
        if code in REGION_OVERRIDES['Europe']:
            return 'Europe'
        if code in REGION_OVERRIDES['Asia']:
            return 'Asia'
        for rg in ['Africa', 'South America', 'North America', 'Europe', 'Asia']:
            b = REGION_BOUNDS[rg]
            if b['lon'][0] <= lon <= b['lon'][1] and b['lat'][0] <= lat <= b['lat'][1]:
                return rg
        return 'Other'

    opts = span() or years
    c1, c2 = st.columns([2.5, 1.5])
    with c1:
        map_year = st.select_slider(
            "Map year", options=opts,
            value=LAST_OBS if LAST_OBS in opts else opts[-1],
            key="map_year"
        )
    with c2:
        region = st.selectbox(
            "Regional extract", list(REGION_BOUNDS),
            index=0, key="map_region"
        )

    st.caption(
        "Country polygons are always shown. Labels adapt to the view: the world map "
        "uses selective labels to avoid crowding, while regional extracts show all "
        "country names. Exact values and ranking are available in the table below."
    )

    # Build one reusable country-level frame per selected year. This is faster
    # than repeatedly scanning df_countries for every map band and every label.
    rows = []
    for name in df_countries.index:
        code = ISO3_MAP.get(name)
        centroid = COUNTRY_CENTROIDS.get(code) if code else None
        if not code or not centroid:
            continue
        lat, lon, display_name = centroid
        value = df_countries.loc[name, map_year]
        value = np.nan if pd.isna(value) else float(value)
        rows.append({
            'source_name': name,
            'country': display_name.title(),
            'label': display_name.upper(),
            'code': code,
            'lat': float(lat),
            'lon': float(lon),
            'value': value,
            'band': bin_label(value),
            'region': country_region(code, float(lat), float(lon)),
        })

    map_df = pd.DataFrame(rows)
    view_df = map_df.copy() if region == 'World' else map_df[map_df['region'] == region].copy()

    # Country order is kept in the extract table below. Positive/defaulting
    # countries are ranked highest-to-lowest by debt for the chosen year/region.
    positive = view_df[view_df['value'].fillna(0) > 0].copy()
    positive = positive.sort_values(['value', 'country'], ascending=[False, True])
    positive['rank'] = np.arange(1, len(positive) + 1)
    rank_lookup = dict(zip(positive['code'], positive['rank']))
    view_df['rank'] = view_df['code'].map(rank_lookup)

    fig_map = go.Figure()

    # One choropleth trace per debt band gives a clean discrete legend exactly
    # like the reference chart. Zero/no-data countries are left in the base land
    # colour rather than being given their own legend entries.
    for lab in MAP_LABELS:
        band_df = view_df[view_df['band'] == lab]
        if band_df.empty:
            continue

        customdata = np.column_stack([
            band_df['value'].map(lambda x: f"${x:,.0f}M"),
            band_df['rank'].map(lambda x: '' if pd.isna(x) else f"#{int(x)}")
        ])

        fig_map.add_trace(go.Choropleth(
            locations=band_df['code'],
            z=np.ones(len(band_df)),
            text=band_df['country'],
            customdata=customdata,
            colorscale=[[0, MAP_COLORS[lab]], [1, MAP_COLORS[lab]]],
            showscale=False,
            marker_line_color='#8c8c8c',
            marker_line_width=0.75,
            name=lab,
            showlegend=True,
            legendgroup=lab,
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Debt in default: %{customdata[0]}<br>'
                'Regional order: %{customdata[1]}'
                '<extra></extra>'
            )
        ))

    # ── Adaptive country labels ──────────────────────────────────────────────
    # A world map cannot legibly carry every country name at once. Keep every
    # country polygon visible, but use a clean default labelling rule:
    #   • World: label defaulting countries >= US$1bn; append values >= US$10bn.
    #   • Regional extracts: label every country in the region; append values
    #     for defaults >= US$10bn.
    # This avoids the previous duplicate name + value text layers.
    if not view_df.empty:
        if region == 'World':
            label_df = view_df[view_df['value'].fillna(0) >= 1000].copy()
            label_size = 7.5
            major_threshold = 10000
        else:
            label_df = view_df.copy()
            label_size = 9
            major_threshold = 10000

        if not label_df.empty:
            def make_map_label(row):
                name = row['label']
                value = row['value']
                if pd.notna(value) and value >= major_threshold:
                    return f"<b>{name}</b><br>${value/1e3:,.1f}B"
                return name

            label_df['map_text'] = label_df.apply(make_map_label, axis=1)

            fig_map.add_trace(go.Scattergeo(
                lon=label_df['lon'],
                lat=label_df['lat'],
                text=label_df['map_text'],
                mode='text',
                showlegend=False,
                hoverinfo='skip',
                textfont=dict(
                    color='#333333',
                    size=label_size,
                    family='Arial'
                )
            ))

    # A short explanation avoids implying that unlabelled world-map countries
    # are missing from the data. Exact values/order remain in the table below.
    if region == 'World':
        st.caption(
            "World view uses selective labels for readability: country names are shown "
            "for defaults of US$1bn or more, with values added at US$10bn or more. "
            "All mapped countries remain visible and are listed in the table below."
        )

    geo_kw = dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor='#8c8c8c',
        coastlinewidth=0.75,
        showland=True,
        landcolor='#f2f2f2',
        showocean=True,
        oceancolor='#a9c7e8',
        showlakes=True,
        lakecolor='#a9c7e8',
        showcountries=True,
        countrycolor='#8c8c8c',
        countrywidth=0.75,
        bgcolor='white',
        projection_type='natural earth' if region == 'World' else 'mercator',
    )

    if region == 'World':
        geo_kw.update(lataxis_range=[-58, 85])
    else:
        b = REGION_BOUNDS[region]
        geo_kw.update(
            lonaxis=dict(range=list(b['lon']), showgrid=False),
            lataxis=dict(range=list(b['lat']), showgrid=False),
        )

    # For regional extracts, put the year/title inside the legend box in the
    # lower-left corner, like the supplied reference image.
    legend_title = (
        f"<b>{map_year} total debt in default<br>by country (US$ millions)</b>"
        if region != 'World'
        else '<b>US$ millions</b>'
    )

    fig_map.update_layout(
        height=760 if region != 'World' else 780,
        geo=geo_kw,
        title=(
            None if region != 'World' else
            dict(text=f'Total debt in default by country, {map_year} (US$ millions)',
                 x=0.01, font=dict(size=14, color='#222'))
        ),
        legend=dict(
            title=dict(text=legend_title, font=dict(size=13, color='#111111')),
            x=0.02,
            y=0.03,
            xanchor='left',
            yanchor='bottom',
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#c7c7c7',
            borderwidth=1,
            font=dict(size=11, color='#111111'),
            itemsizing='constant',
            traceorder='normal',
        ),
        margin=dict(l=0, r=0, t=20 if region != 'World' else 45, b=0),
        paper_bgcolor='white',
    )

    show_chart(
        fig_map,
        f"debt_default_map_{region.lower().replace(' ', '_')}_{map_year}.html",
        "cmap"
    )

    # ── Regional/country extract ────────────────────────────────────────────
    st.divider()
    st.markdown(f"### {region} country order — {map_year}")

    table_df = view_df.copy()
    table_df['Debt in default (US$M)'] = table_df['value']
    table_df['Debt in default (US$B)'] = table_df['value'] / 1e3
    table_df['Order'] = table_df['rank']
    table_df['Band'] = table_df['band'].fillna('No default / no data')

    table_df['_sort_group'] = np.where(table_df['rank'].notna(), 0, 1)
    table_df['_sort_rank'] = table_df['rank'].fillna(10_000)
    table_df = table_df.sort_values(
        ['_sort_group', '_sort_rank', 'country'], ascending=[True, True, True]
    )

    display_df = table_df[[
        'Order', 'country', 'code', 'Debt in default (US$M)',
        'Debt in default (US$B)', 'Band'
    ]].rename(columns={'country': 'Country', 'code': 'ISO3'})

    display_df['Order'] = display_df['Order'].apply(
        lambda x: '' if pd.isna(x) else int(x)
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Countries shown", f"{len(view_df):,}")
    m2.metric("Countries with debt in default", f"{len(positive):,}")
    m3.metric("Debt in default", f"${positive['value'].sum()/1e3:,.1f}B")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Order': st.column_config.NumberColumn('Order', format='%d'),
            'Debt in default (US$M)': st.column_config.NumberColumn(format='$%,.0f'),
            'Debt in default (US$B)': st.column_config.NumberColumn(format='$%,.1f'),
        },
        height=min(700, 38 + 35 * min(len(display_df), 18))
    )

    st.caption(
        f"{len(view_df)} countries shown in {region} · "
        f"{len(positive)} have debt in default in {map_year}. "
        "Order ranks defaulting countries from highest to lowest debt in default."
    )

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(f"Source: BoC–BoE Sovereign Default Database · Last update: July 22, 2026 · "
           f"Last observation: {LAST_OBS} · Built with Streamlit + Plotly")
