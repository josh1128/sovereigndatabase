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

    MAP_BINS = [0, 100, 1000, 10000, 25000, 50000, np.inf]
    MAP_LABELS = ['>0 - 100', '100 - 1,000', '1,000 - 10,000',
                  '10,000 - 25,000', '25,000 - 50,000', '>50,000']
    MAP_COLORS = {'#N/A or 0': '#d9d9d9', '>0 - 100': '#ffffcc', '100 - 1,000': '#ffff33',
                  '1,000 - 10,000': '#ff9900', '10,000 - 25,000': '#f4978e',
                  '25,000 - 50,000': '#ff0000', '>50,000': '#5c1a1a'}
    MAP_ORDER = ['#N/A or 0'] + MAP_LABELS

    def bin_label(v):
        if pd.isna(v) or v <= 0:
            return '#N/A or 0'
        for lo, hi, lab in zip(MAP_BINS[:-1], MAP_BINS[1:], MAP_LABELS):
            if lo < v <= hi:
                return lab
        return '>50,000'

    opts = span() or years
    map_year = st.select_slider("Map year", options=opts,
                                value=LAST_OBS if LAST_OBS in opts else opts[-1],
                                key="map_year")

    fig_map = go.Figure()
    counts = {lab: 0 for lab in MAP_ORDER}
    for lab in MAP_ORDER:
        locs, txt, cd = [], [], []
        for name in df_countries.index:
            code = ISO3_MAP.get(name)
            if not code:
                continue
            v = df_countries.loc[name, map_year]
            if bin_label(v) == lab:
                locs.append(code); txt.append(name)
                cd.append("N/A" if (pd.isna(v) or v <= 0) else f"${v:,.0f}M")
                counts[lab] += 1
        fig_map.add_trace(go.Choropleth(
            locations=locs, z=[0] * len(locs), text=txt, customdata=cd,
            colorscale=[[0, MAP_COLORS[lab]], [1, MAP_COLORS[lab]]], showscale=False,
            marker_line_color='#ffffff', marker_line_width=0.4,
            name=lab, showlegend=True, legendgroup=lab,
            hovertemplate='<b>%{text}</b><br>' + lab + '<br>%{customdata}<extra></extra>'))

    continents = [('NORTH AMERICA', 46, -100), ('SOUTH AMERICA', -14, -58),
                  ('EUROPE', 56, -12), ('AFRICA', 11, 18),
                  ('ASIA', 50, 100), ('AUSTRALIA', -25, 134)]
    oceans = [('Atlantic<br>Ocean', 6, -34), ('Pacific<br>Ocean', 18, -150),
              ('Pacific<br>Ocean', -20, -120), ('Indian<br>Ocean', -28, 80)]
    fig_map.add_trace(go.Scattergeo(
        lon=[c[2] for c in continents], lat=[c[1] for c in continents],
        text=[c[0] for c in continents], mode='text', showlegend=False, hoverinfo='skip',
        textfont=dict(color='#6b6b6b', size=13, family='Arial Black')))
    fig_map.add_trace(go.Scattergeo(
        lon=[o[2] for o in oceans], lat=[o[1] for o in oceans],
        text=[o[0] for o in oceans], mode='text', showlegend=False, hoverinfo='skip',
        textfont=dict(color='#5b7fb0', size=11, family='Arial')))

    # ── Numeric callouts for major countries with > US$10,000M in default ──
    # Keep only the largest values so labels do not overwhelm the map.
    CALLOUT_THRESHOLD = 10_000   # US$ millions
    MAX_CALLOUTS = 8

    # Approximate country-centre coordinates used only for text callouts.
    CALLOUT_COORDS = {
        'Argentina': (-38.4, -63.6),
        'Brazil': (-14.2, -51.9),
        'China': (35.9, 104.2),
        'Greece': (39.1, 21.8),
        'India': (20.6, 78.9),
        'Indonesia': (-0.8, 113.9),
        'Mexico': (23.6, -102.5),
        'Pakistan': (30.4, 69.3),
        'Russia': (61.5, 105.3),
        'USSR/Russian Federation': (61.5, 105.3),
        'South Africa': (-30.6, 22.9),
        'Turkey': (39.0, 35.2),
        'Ukraine': (48.4, 31.2),
        'Venezuela': (6.4, -66.6),
    }

    callout_rows = []
    for name in df_countries.index:
        v = df_countries.loc[name, map_year]
        if (
            pd.notna(v)
            and v > CALLOUT_THRESHOLD
            and name in CALLOUT_COORDS
        ):
            lat, lon = CALLOUT_COORDS[name]
            callout_rows.append((name, float(v), lat, lon))

    # Largest countries first; cap the number of visible labels.
    callout_rows = sorted(callout_rows, key=lambda x: x[1], reverse=True)[:MAX_CALLOUTS]

    if callout_rows:
        fig_map.add_trace(go.Scattergeo(
            lon=[r[3] for r in callout_rows],
            lat=[r[2] for r in callout_rows],
            text=[f"<b>{r[0]}</b><br>${r[1]/1e3:,.1f}B" for r in callout_rows],
            mode='text',
            showlegend=False,
            hoverinfo='skip',
            textfont=dict(color='#111111', size=11, family='Arial Black'),
        ))

    fig_map.update_layout(
        height=600,
        title=dict(text=f'Total debt in default by country, {map_year} (US$ millions)',
                   x=0.01, font=dict(size=14, color='#222')),
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor='#ffffff',
                 coastlinewidth=0.4, projection_type='equirectangular',
                 landcolor='#e6e6e6', showland=True,
                 showocean=True, oceancolor='#a9c7e8',
                 showlakes=True, lakecolor='#a9c7e8',
                 showcountries=True, countrycolor='#ffffff', countrywidth=0.4,
                 lataxis_range=[-58, 85], bgcolor='rgba(0,0,0,0)'),
        legend=dict(title='<b>US$ millions</b>', x=0.012, y=0.55,
                    bgcolor='rgba(255,255,255,0.92)', bordercolor='#bbb', borderwidth=1,
                    font=dict(size=11, color='#222'), itemsizing='constant'),
        margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor='white')
    show_chart(fig_map, f"global_debt_default_map_{map_year}.html", "cmap")

    mapped = sum(1 for c in ISO3_MAP.values() if c)
    st.caption(f"{mapped} of {len(ISO3_MAP)} countries mapped · "
               f"{counts['>50,000'] + counts['25,000 - 50,000']} in the top two bands in {map_year}. "
               "Grey = no data or zero (includes dissolved states).")

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(f"Source: BoC–BoE Sovereign Default Database · Last update: July 22, 2026 · "
           f"Last observation: {LAST_OBS} · Built with Streamlit + Plotly")
