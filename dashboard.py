import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

st.set_page_config(page_title="Sovereign Defaults Dashboard", layout="wide", page_icon="🌍")

st.markdown("""
<style>
    .metric-card {
        background: #1e2130;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-label { color: #9aa0b0; font-size: 13px; margin-bottom: 4px; }
    .metric-value { color: #f0f4ff; font-size: 26px; font-weight: 700; }
    .metric-sub { color: #6c8ebf; font-size: 12px; margin-top: 2px; }
    section[data-testid="stSidebar"] { background: #12151f; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df_raw = pd.read_excel(os.path.join(base_dir, "data.xlsx"), header=None)

    # Parse years from row 0
    years_raw = df_raw.iloc[0, 4:].values
    years = []
    for y in years_raw:
        try:
            if str(y).strip() == '2024p':
                years.append(2024)
            elif pd.notna(y):
                years.append(int(float(y)))
        except:
            pass

    def get_row(row_idx):
        vals = df_raw.iloc[row_idx, 4:4+len(years)].values
        result = []
        for v in vals:
            try:
                if pd.notna(v) and str(v).strip() != '****':
                    result.append(float(v))
                else:
                    result.append(np.nan)
            except:
                result.append(np.nan)
        return pd.Series(result, index=years)

    # Summary: Creditor breakdown (rows 6–17)
    creditor_rows = {
        'Total': 6, 'IMF': 7, 'IBRD': 8, 'IDA': 9, 'IADB': 10,
        'Paris Club': 11, 'China': 12, 'Other Official': 13,
        'FC Bank Loans': 14, 'FC Bonds': 15,
        'Other Private': 16, 'LC Debt': 17
    }
    df_creditors = pd.DataFrame({k: get_row(v) for k, v in creditor_rows.items()})

    # Summary: Debtor breakdown (rows 22–26)
    debtor_rows = {
        'Total': 22, 'Advanced Economies': 23,
        'Emerging/Frontier': 24, 'HIPC': 25, 'Other Developing': 26
    }
    df_debtors = pd.DataFrame({k: get_row(v) for k, v in debtor_rows.items()})

    # Default rates (rows 31, 36)
    df_rates = pd.DataFrame({
        '% of all Sovereigns': get_row(31),
        '% of World GDP': get_row(36),
    })

    # Sovereigns in default count (row 40)
    sov_in_default = get_row(40)
    total_sovereigns = get_row(38)

    # Country-level data
    countries = []
    for i in range(66, len(df_raw)):
        val1 = df_raw.iloc[i, 1]
        val2 = df_raw.iloc[i, 2]
        if pd.notna(val1) and isinstance(val1, (int, float)):
            try:
                name = str(val2).strip()
                vals = df_raw.iloc[i, 4:4+len(years)].values
                total_series = []
                for v in vals:
                    try:
                        if pd.notna(v) and str(v).strip() != '****':
                            total_series.append(float(v))
                        else:
                            total_series.append(np.nan)
                    except:
                        total_series.append(np.nan)
                countries.append({'name': name, 'total': total_series})
            except:
                pass

    df_countries = pd.DataFrame(
        [c['total'] for c in countries],
        index=[c['name'] for c in countries],
        columns=years
    )

    return df_creditors, df_debtors, df_rates, sov_in_default, total_sovereigns, df_countries, years


def plotly_html_bytes(fig):
    """Return a self-contained, interactive Plotly HTML file as UTF-8 bytes."""
    html = pio.to_html(
        fig,
        full_html=True,
        include_plotlyjs=True,
        config={
            "responsive": True,
            "displaylogo": False,
            "scrollZoom": True,
            "toImageButtonOptions": {
                "format": "png",
                "scale": 2,
            },
        },
        default_width="100%",
        default_height="100%",
    )
    return html.encode("utf-8")


def show_plotly_chart_with_download(fig, filename, key):
    """Display a Plotly chart and add a standalone HTML download button."""
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "responsive": True,
            "displaylogo": False,
        },
    )
    st.download_button(
        label="⬇️ Download standalone HTML",
        data=plotly_html_bytes(fig),
        file_name=filename,
        mime="text/html",
        key=key,
        help="Downloads a self-contained interactive HTML file that can be opened directly in a browser.",
    )


df_creditors, df_debtors, df_rates, sov_in_default, total_sovereigns, df_countries, years = load_data()

CREDITOR_COLORS = {
    'IMF': '#4e9af1', 'IBRD': '#f1c44e', 'IDA': '#e87040',
    'IADB': '#9b59b6', 'Paris Club': '#2ecc71',
    'China': '#e74c3c', 'Other Official': '#1abc9c',
    'FC Bank Loans': '#f39c12', 'FC Bonds': '#3498db',
    'Other Private': '#95a5a6', 'LC Debt': '#d35400'
}

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Sovereign Defaults")
    st.markdown("*Database — Last Update: July 2025*")
    st.divider()
    year_range = st.slider("Year Range", min_value=years[0], max_value=years[-1],
                           value=(1980, years[-1]))
    st.divider()
    st.markdown("**Select Countries**")
    country_list = sorted(df_countries.index.tolist())
    default_countries = ['Argentina', 'Greece', 'Zambia', 'Iraq', 'Venezuela']
    selected_countries = st.multiselect("", options=country_list,
                                        default=[c for c in default_countries if c in country_list])
    st.divider()
    st.markdown("**Creditors to Show**")
    creditor_options = list(CREDITOR_COLORS.keys())
    selected_creditors = st.multiselect("", options=creditor_options,
                                        default=['Paris Club', 'China', 'FC Bonds', 'IMF', 'Other Official'])

y0, y1 = year_range
yr_slice = [y for y in years if y0 <= y <= y1]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🌍 Global Sovereign Defaults Dashboard")
st.caption(f"Showing data from **{y0}** to **{y1}** · {len(df_countries)} countries tracked")

# ── KPI Cards ────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
latest_year = max(y for y in yr_slice if not np.isnan(df_creditors.loc[y, 'Total']))
latest_total = df_creditors.loc[latest_year, 'Total']
peak_year = df_creditors.loc[yr_slice, 'Total'].idxmax()
peak_total = df_creditors.loc[peak_year, 'Total']
latest_rate = df_rates.loc[latest_year, '% of all Sovereigns']
latest_count = sov_in_default.loc[latest_year]

with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Total Debt in Default ({latest_year})</div>
        <div class="metric-value">${latest_total/1e6:.2f}T</div>
        <div class="metric-sub">US$ million basis</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Peak Default Debt</div>
        <div class="metric-value">${peak_total/1e6:.2f}T</div>
        <div class="metric-sub">in {peak_year}</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">% Sovereigns in Default ({latest_year})</div>
        <div class="metric-value">{latest_rate:.1f}%</div>
        <div class="metric-sub">of all sovereigns</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Countries in Default ({latest_year})</div>
        <div class="metric-value">{int(latest_count)}</div>
        <div class="metric-sub">sovereign defaulters</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tab Layout ───────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Total Debt in Default", "🥧 Creditor Breakdown", "🌐 Country Deep Dive"])

# ─── TAB 1: Total Debt Over Time ─────────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Total Sovereign Debt in Default Over Time")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yr_slice,
            y=df_creditors.loc[yr_slice, 'Total'] / 1e3,
            mode='lines+markers',
            name='Total (US$ bil)',
            line=dict(color='#4e9af1', width=2.5),
            marker=dict(size=4),
            fill='tozeroy',
            fillcolor='rgba(78,154,241,0.1)'
        ))
        fig.add_trace(go.Scatter(
            x=yr_slice,
            y=df_rates.loc[yr_slice, '% of all Sovereigns'],
            mode='lines',
            name='% of Sovereigns',
            yaxis='y2',
            line=dict(color='#f1c44e', width=1.8, dash='dot'),
        ))
        fig.update_layout(
            template='plotly_dark', height=380,
            legend=dict(orientation='h', y=1.08),
            yaxis=dict(title='Debt in Default (US$ billion)'),
            yaxis2=dict(title='% of Sovereigns', overlaying='y', side='right',
                        showgrid=False),
            margin=dict(l=50, r=50, t=20, b=40),
            hovermode='x unified'
        )
        show_plotly_chart_with_download(
            fig,
            "total_sovereign_debt_in_default.html",
            "download_fig_total_debt",
        )

    with col_right:
        st.subheader("By Debtor Group")
        debtor_cols = ['Advanced Economies', 'Emerging/Frontier', 'HIPC', 'Other Developing']
        fig2 = go.Figure()
        debtor_colors = ['#4e9af1', '#e87040', '#2ecc71', '#f1c44e']
        for col, color in zip(debtor_cols, debtor_colors):
            series = df_debtors.loc[yr_slice, col].dropna()
            fig2.add_trace(go.Scatter(
                x=series.index, y=series.values / 1e3,
                mode='lines', name=col,
                line=dict(color=color, width=2),
                stackgroup='one'
            ))
        fig2.update_layout(
            template='plotly_dark', height=380,
            legend=dict(orientation='h', y=1.08, font=dict(size=10)),
            yaxis=dict(title='US$ billion'),
            margin=dict(l=40, r=20, t=20, b=40),
            hovermode='x unified'
        )
        show_plotly_chart_with_download(
            fig2,
            "debtor_group_breakdown.html",
            "download_fig_debtor_group",
        )

    # Number of defaulters over time
    st.subheader("Number of Sovereigns in Default Over Time")
    fig3 = go.Figure()
    sov_slice = sov_in_default.loc[yr_slice].dropna()
    total_slice = total_sovereigns.loc[yr_slice].dropna()
    fig3.add_trace(go.Bar(
        x=sov_slice.index, y=sov_slice.values,
        name='Sovereigns in Default',
        marker_color='#e87040',
        opacity=0.85
    ))
    fig3.add_trace(go.Scatter(
        x=total_slice.index, y=total_slice.values,
        name='Total Sovereigns',
        mode='lines',
        line=dict(color='#9aa0b0', width=1.5, dash='dot')
    ))
    fig3.update_layout(
        template='plotly_dark', height=280,
        legend=dict(orientation='h'),
        yaxis=dict(title='Count'),
        margin=dict(l=40, r=20, t=10, b=40),
        hovermode='x unified'
    )
    show_plotly_chart_with_download(
        fig3,
        "sovereigns_in_default_count.html",
        "download_fig_default_count",
    )


# ─── TAB 2: Creditor Breakdown ───────────────────────────────────────────────
with tab2:
    if not selected_creditors:
        st.warning("Select at least one creditor in the sidebar.")
    else:
        col_l, col_r = st.columns([3, 2])

        with col_l:
            st.subheader("Creditor Breakdown Over Time (Stacked)")
            fig4 = go.Figure()
            for cred in selected_creditors:
                if cred in df_creditors.columns:
                    series = df_creditors.loc[yr_slice, cred].fillna(0)
                    fig4.add_trace(go.Bar(
                        x=yr_slice, y=series.values / 1e3,
                        name=cred,
                        marker_color=CREDITOR_COLORS.get(cred, '#aaa'),
                    ))
            fig4.update_layout(
                barmode='stack', template='plotly_dark', height=420,
                legend=dict(orientation='h', y=1.08, font=dict(size=11)),
                yaxis=dict(title='US$ billion'),
                margin=dict(l=40, r=20, t=20, b=40),
                hovermode='x unified'
            )
            show_plotly_chart_with_download(
                fig4,
                "creditor_breakdown_stacked.html",
                "download_fig_creditor_stacked",
            )

        with col_r:
            st.subheader(f"Composition in {latest_year}")
            pie_vals = {}
            for cred in selected_creditors:
                if cred in df_creditors.columns:
                    v = df_creditors.loc[latest_year, cred]
                    if pd.notna(v) and v > 0:
                        pie_vals[cred] = v
            if pie_vals:
                fig5 = go.Figure(go.Pie(
                    labels=list(pie_vals.keys()),
                    values=list(pie_vals.values()),
                    hole=0.45,
                    marker_colors=[CREDITOR_COLORS.get(k, '#aaa') for k in pie_vals],
                ))
                fig5.update_layout(
                    template='plotly_dark', height=420,
                    legend=dict(orientation='h', font=dict(size=10)),
                    margin=dict(l=10, r=10, t=20, b=40),
                    annotations=[dict(text=f'{latest_year}', x=0.5, y=0.5,
                                      font_size=18, showarrow=False, font_color='white')]
                )
                show_plotly_chart_with_download(
                    fig5,
                    "creditor_composition.html",
                    "download_fig_creditor_pie",
                )

        # China vs Paris Club comparison
        st.subheader("China vs. Paris Club: Creditor Default Amounts")
        fig6 = go.Figure()
        for cred, color in [('China', '#e74c3c'), ('Paris Club', '#2ecc71')]:
            if cred in df_creditors.columns:
                series = df_creditors.loc[yr_slice, cred].dropna()
                fig6.add_trace(go.Scatter(
                    x=series.index, y=series.values / 1e3,
                    mode='lines+markers', name=cred,
                    line=dict(color=color, width=2.5),
                    marker=dict(size=4)
                ))
        fig6.update_layout(
            template='plotly_dark', height=300,
            yaxis=dict(title='US$ billion'),
            legend=dict(orientation='h'),
            margin=dict(l=40, r=20, t=10, b=40),
            hovermode='x unified'
        )
        show_plotly_chart_with_download(
            fig6,
            "china_vs_paris_club.html",
            "download_fig_china_paris",
        )


# ─── TAB 3: Country Deep Dive ────────────────────────────────────────────────
with tab3:
    if not selected_countries:
        st.info("Select countries in the sidebar to explore their default history.")
    else:
        # Line chart: country default amounts over time
        st.subheader("Default Amount by Country Over Time")
        fig7 = go.Figure()
        palette = px.colors.qualitative.Plotly
        for i, country in enumerate(selected_countries):
            if country in df_countries.index:
                series = df_countries.loc[country, yr_slice].replace(0, np.nan).dropna()
                if not series.empty:
                    fig7.add_trace(go.Scatter(
                        x=series.index, y=series.values / 1e3,
                        mode='lines+markers', name=country,
                        line=dict(color=palette[i % len(palette)], width=2),
                        marker=dict(size=5)
                    ))
        fig7.update_layout(
            template='plotly_dark', height=400,
            yaxis=dict(title='Debt in Default (US$ billion)'),
            legend=dict(orientation='h', y=1.08),
            margin=dict(l=40, r=20, t=20, b=40),
            hovermode='x unified'
        )
        show_plotly_chart_with_download(
            fig7,
            "country_default_history.html",
            "download_fig_country_history",
        )

        # Top 15 defaulters bar chart
        st.subheader("Top 15 Countries by Total Default (All Time)")
        df_sum = df_countries.loc[:, yr_slice].sum(axis=1, skipna=True).nlargest(15)
        fig8 = go.Figure(go.Bar(
            x=df_sum.values / 1e6,
            y=df_sum.index,
            orientation='h',
            marker=dict(
                color=df_sum.values,
                colorscale='Reds',
                showscale=False
            ),
        ))
        # Highlight selected countries
        bar_colors = ['#f1c44e' if c in selected_countries else '#e87040'
                      for c in df_sum.index]
        fig8.update_traces(marker_color=bar_colors)
        fig8.update_layout(
            template='plotly_dark', height=420,
            xaxis=dict(title='Total Default (US$ trillion)'),
            margin=dict(l=150, r=40, t=10, b=40),
            yaxis=dict(autorange='reversed')
        )
        show_plotly_chart_with_download(
            fig8,
            "top_15_country_defaults.html",
            "download_fig_top_15",
        )

        # Heatmap: selected countries x decades
        if len(selected_countries) >= 2:
            st.subheader("Default Heatmap — Selected Countries")
            decade_years = {}
            for y in yr_slice:
                decade = f"{(y // 10) * 10}s"
                if decade not in decade_years:
                    decade_years[decade] = []
                decade_years[decade].append(y)

            heatmap_data = []
            for country in selected_countries:
                if country in df_countries.index:
                    row = []
                    for decade, dyears in decade_years.items():
                        vals = df_countries.loc[country, [y for y in dyears if y in df_countries.columns]]
                        row.append(vals.mean(skipna=True) / 1e3)
                    heatmap_data.append(row)

            if heatmap_data:
                fig9 = go.Figure(go.Heatmap(
                    z=heatmap_data,
                    x=list(decade_years.keys()),
                    y=[c for c in selected_countries if c in df_countries.index],
                    colorscale='YlOrRd',
                    hoverongaps=False,
                    colorbar=dict(title='Avg US$B')
                ))
                fig9.update_layout(
                    template='plotly_dark', height=max(250, len(selected_countries) * 45),
                    margin=dict(l=130, r=40, t=10, b=60),
                    xaxis=dict(side='bottom')
                )
                show_plotly_chart_with_download(
                    fig9,
                    "selected_country_default_heatmap.html",
                    "download_fig_heatmap",
                )

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption("Source: Database of Sovereign Defaults · Last Update: July 2025 · Built with Streamlit + Plotly")
