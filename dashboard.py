# ═══ MAP: Global debt in default ═════════════════════════════════════════════
# Replace your current map section with this entire block.
# It assumes these objects already exist earlier in dashboard.py:
#   st, pd, np, go
#   tab_map
#   df_countries
#   ISO3_MAP
#   COUNTRY_CENTROIDS
#   span()
#   years
#   LAST_OBS
#   show_chart()

with tab_map:
    st.subheader("Figure A-1: Global debt in default")

    # ─────────────────────────────────────────────────────────────────────────
    # Debt bands / map colours
    # ─────────────────────────────────────────────────────────────────────────
    MAP_BINS = [0, 100, 1_000, 10_000, 25_000, 50_000, np.inf]

    MAP_LABELS = [
        "0 - 100",
        "100 - 1,000",
        "1,000 - 10,000",
        "10,000 - 25,000",
        "25,000 - 50,000",
        "50,000+",
    ]

    MAP_COLORS = {
        "0 - 100": "#fff200",
        "100 - 1,000": "#f5a623",
        "1,000 - 10,000": "#d98100",
        "10,000 - 25,000": "#ed1c24",
        "25,000 - 50,000": "#b5121b",
        "50,000+": "#7a0000",
    }

    def debt_band(value):
        if pd.isna(value) or value <= 0:
            return None

        for low, high, label in zip(
            MAP_BINS[:-1],
            MAP_BINS[1:],
            MAP_LABELS,
        ):
            if low < value <= high:
                return label

        return MAP_LABELS[-1]

    # ─────────────────────────────────────────────────────────────────────────
    # Regional map extents
    #
    # IMPORTANT CHANGE:
    # North America is deliberately tighter than before.
    # The previous 5°–82° latitude view spent most of the map on northern
    # Canada/Arctic areas, making Central America and the Caribbean tiny.
    # ─────────────────────────────────────────────────────────────────────────
    REGION_BOUNDS = {
        "World": None,
        "Africa": {
            "lon": (-20, 55),
            "lat": (-36, 38),
        },
        "Asia": {
            "lon": (25, 180),
            "lat": (-12, 78),
        },
        "Europe": {
            "lon": (-13, 43),
            "lat": (34, 72),
        },

        # Zoomed North America.
        # Includes the continental US, southern Canada, Mexico,
        # Central America and the Caribbean.
        "North America": {
            "lon": (-130, -55),
            "lat": (5, 55),
        },

        "South America": {
            "lon": (-83, -32),
            "lat": (-58, 14),
        },
    }

    REGION_HEIGHTS = {
        "World": 780,
        "Africa": 900,
        "Asia": 760,
        "Europe": 720,
        "North America": 820,
        "South America": 900,
    }

    # ─────────────────────────────────────────────────────────────────────────
    # Region membership
    #
    # IMPORTANT CHANGE:
    # North/South America are explicitly defined.
    #
    # Previously, overlapping latitude/longitude boxes could classify Caribbean
    # countries such as Aruba, Barbados, Trinidad & Tobago, etc. as South
    # America. That is why the South America screenshot contained a large clump
    # of Caribbean labels above Venezuela.
    # ─────────────────────────────────────────────────────────────────────────
    REGION_MEMBERS = {
        "Europe": {
            "GBR", "IRL", "ISL", "PRT", "ESP", "FRA", "BEL", "NLD", "LUX",
            "DEU", "CHE", "AUT", "ITA", "MLT", "DNK", "NOR", "SWE", "FIN",
            "EST", "LVA", "LTU", "POL", "CZE", "SVK", "HUN", "SVN", "HRV",
            "BIH", "SRB", "MNE", "MKD", "ALB", "GRC", "BGR", "ROU", "MDA",
            "UKR", "BLR",
        },

        "Asia": {
            "RUS", "TUR", "GEO", "ARM", "AZE", "CYP", "KAZ",
        },

        "North America": {
            # Main countries
            "CAN", "USA", "MEX",

            # Central America
            "BLZ", "GTM", "HND", "SLV", "NIC", "CRI", "PAN",

            # Caribbean
            "BHS", "CUB", "JAM", "HTI", "DOM", "PRI",
            "ABW", "AIA", "ATG", "BRB", "CUW", "DMA", "GRD",
            "KNA", "LCA", "SXM", "TTO", "VCT",

            # Other Caribbean / North Atlantic territories if present
            "BMU", "TCA", "VGB", "VIR",
        },

        "South America": {
            "ARG", "BOL", "BRA", "CHL", "COL", "EC",
            "ECU", "GUY", "PRY", "PER", "SUR", "URY", "VEN",
        },
    }

    def country_region(code, lat, lon):
        # Explicit memberships take priority.
        # This prevents overlapping bounding boxes from misclassifying countries.
        for region_name in (
            "Europe",
            "Asia",
            "North America",
            "South America",
        ):
            if code in REGION_MEMBERS.get(region_name, set()):
                return region_name

        # Preserve the existing broad geographic fallback for countries that are
        # not explicitly assigned above.
        for region_name in (
            "Africa",
            "South America",
            "North America",
            "Europe",
            "Asia",
        ):
            bounds = REGION_BOUNDS[region_name]

            inside_lon = bounds["lon"][0] <= lon <= bounds["lon"][1]
            inside_lat = bounds["lat"][0] <= lat <= bounds["lat"][1]

            if inside_lon and inside_lat:
                return region_name

        return "Other"

    # ─────────────────────────────────────────────────────────────────────────
    # Controls
    # ─────────────────────────────────────────────────────────────────────────
    available_years = span() or years

    control_left, control_right = st.columns([2.5, 1.5])

    with control_left:
        map_year = st.select_slider(
            "Map year",
            options=available_years,
            value=(
                LAST_OBS
                if LAST_OBS in available_years
                else available_years[-1]
            ),
            key="map_year",
        )

    with control_right:
        region = st.selectbox(
            "Regional extract",
            list(REGION_BOUNDS.keys()),
            index=0,
            key="map_region",
        )

    st.caption(
        "Country polygons are always shown. Regional labels are simplified "
        "automatically so small or crowded countries do not overlap. "
        "Countries without visible labels remain available through hover "
        "and in the table below."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Build country-level map data
    # ─────────────────────────────────────────────────────────────────────────
    map_rows = []

    for source_country in df_countries.index:
        iso3 = ISO3_MAP.get(source_country)

        if not iso3:
            continue

        centroid = COUNTRY_CENTROIDS.get(iso3)

        if centroid is None:
            continue

        latitude, longitude, display_name = centroid

        raw_value = df_countries.loc[source_country, map_year]

        value = (
            np.nan
            if pd.isna(raw_value)
            else float(raw_value)
        )

        map_rows.append(
            {
                "source_name": source_country,
                "country": display_name.title(),
                "label": display_name.upper(),
                "code": iso3,
                "lat": float(latitude),
                "lon": float(longitude),
                "value": value,
                "band": debt_band(value),
                "region": country_region(
                    iso3,
                    float(latitude),
                    float(longitude),
                ),
            }
        )

    map_df = pd.DataFrame(map_rows)

    if region == "World":
        view_df = map_df.copy()
    else:
        view_df = map_df[
            map_df["region"] == region
        ].copy()

    # ─────────────────────────────────────────────────────────────────────────
    # Rank defaulting countries in the selected view
    # ─────────────────────────────────────────────────────────────────────────
    positive = view_df[
        view_df["value"].fillna(0) > 0
    ].copy()

    positive = positive.sort_values(
        ["value", "country"],
        ascending=[False, True],
    )

    positive["rank"] = np.arange(
        1,
        len(positive) + 1,
    )

    rank_lookup = dict(
        zip(
            positive["code"],
            positive["rank"],
        )
    )

    view_df["rank"] = view_df["code"].map(
        rank_lookup
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Base choropleth
    # ─────────────────────────────────────────────────────────────────────────
    fig_map = go.Figure()

    for band_name in MAP_LABELS:
        band_df = view_df[
            view_df["band"] == band_name
        ].copy()

        if band_df.empty:
            continue

        custom_data = np.column_stack(
            [
                band_df["value"].map(
                    lambda x: f"${x:,.0f}M"
                ),
                band_df["rank"].map(
                    lambda x: (
                        ""
                        if pd.isna(x)
                        else f"#{int(x)}"
                    )
                ),
            ]
        )

        fig_map.add_trace(
            go.Choropleth(
                locations=band_df["code"],
                locationmode="ISO-3",
                z=np.ones(len(band_df)),
                text=band_df["country"],
                customdata=custom_data,
                colorscale=[
                    [0, MAP_COLORS[band_name]],
                    [1, MAP_COLORS[band_name]],
                ],
                showscale=False,
                marker_line_color="#8c8c8c",
                marker_line_width=0.75,
                name=band_name,
                showlegend=True,
                legendgroup=band_name,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Debt in default: %{customdata[0]}<br>"
                    "Regional order: %{customdata[1]}"
                    "<extra></extra>"
                ),
            )
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Label formatting
    # ─────────────────────────────────────────────────────────────────────────
    SHORT_LABELS = {
        "United Kingdom": "UK",
        "United States": "USA",
        "Central African Republic": "CENTRAL AFRICAN<br>REPUBLIC",
        "Democratic Republic Of The Congo": "DR CONGO",
        "Congo [Drc]": "DR CONGO",
        "Congo [Republic]": "CONGO",
        "Bosnia And Herzegovina": "BOSNIA &<br>HERZ.",
        "North Macedonia": "N. MACEDONIA",
        "Papua New Guinea": "PAPUA NEW<br>GUINEA",
        "Equatorial Guinea": "EQUATORIAL<br>GUINEA",
        "Guinea-Bissau": "GUINEA-<br>BISSAU",
        "South Africa": "SOUTH AFRICA",
        "South Sudan": "SOUTH SUDAN",
        "Saudi Arabia": "SAUDI ARABIA",
        "North Korea": "NORTH KOREA",
        "South Korea": "SOUTH KOREA",
        "New Zealand": "NEW ZEALAND",
    }

    # Fine positioning for labels that are worth showing but sit in dense areas.
    LABEL_OFFSETS = {
        "Africa": {
            "GMB": (-2.5, 0.5),
            "GNB": (-2.3, -0.7),
            "SLE": (-1.6, -0.8),
            "LBR": (-1.4, -1.0),
            "TGO": (0.0, -1.2),
            "BEN": (0.8, 1.0),
            "RWA": (1.4, 0.5),
            "BDI": (1.5, -0.8),
            "UGA": (0.8, 1.2),
            "MWI": (1.1, -0.4),
            "SWZ": (1.0, -0.8),
            "LSO": (0.0, -1.4),
            "DJI": (1.4, 0.4),
            "ERI": (0.7, 1.0),
        },

        "Europe": {
            "BEL": (-1.7, 0.7),
            "NLD": (0.0, 1.3),
            "LUX": (1.3, -0.4),
            "CHE": (-1.1, -0.8),
            "AUT": (1.0, 0.3),
            "SVN": (-0.8, -0.7),
            "HRV": (1.0, -0.5),
            "BIH": (1.5, 0.2),
            "MNE": (0.5, -0.8),
            "SRB": (1.2, 0.4),
            "MKD": (0.8, -0.9),
            "ALB": (-0.6, -0.7),
            "SVK": (0.7, 0.7),
            "CZE": (-0.5, 0.8),
            "MDA": (1.1, 0.3),
        },

        "Asia": {
            "LBN": (-1.5, 0.7),
            "ISR": (-1.5, -0.5),
            "PSE": (1.5, -0.7),
            "JOR": (1.5, 0.4),
            "KWT": (1.3, 0.8),
            "QAT": (1.4, -0.4),
            "BHR": (1.4, 0.5),
            "SGP": (1.5, -0.8),
            "BRN": (1.5, 0.5),
        },

        "North America": {
            # Central America
            "BLZ": (-1.2, 0.8),
            "GTM": (-1.0, 0.3),
            "HND": (0.8, 0.9),
            "SLV": (-1.4, -0.7),
            "NIC": (0.9, -0.3),
            "CRI": (-0.8, -0.8),
            "PAN": (1.2, -0.7),

            # Larger Caribbean countries
            "CUB": (0.0, 1.2),
            "JAM": (0.0, -1.1),
            "HTI": (-0.9, 0.7),
            "DOM": (1.0, 0.5),
        },

        "South America": {
            "URY": (1.3, -0.5),
            "PRY": (1.0, 0.8),
            "ECU": (-1.0, 0.5),
            "GUY": (1.0, 0.8),
            "SUR": (1.2, -0.5),
        },
    }

    # Force a few large reference-country labels into readable locations.
    # This is especially helpful because Canada's geographic centroid is very far
    # north and would otherwise sit outside the tighter North America view.
    LABEL_POSITIONS = {
        "North America": {
            "CAN": (-106.0, 51.0),
            "USA": (-98.0, 38.0),
            "MEX": (-102.0, 23.5),
        }
    }

    REGION_LABEL_SIZE = {
        "Africa": 9,
        "Asia": 8,
        "Europe": 7,
        "North America": 9,
        "South America": 9,
    }

    # ─────────────────────────────────────────────────────────────────────────
    # Label suppression
    #
    # These countries remain fully available on hover and in the table.
    # Only their always-visible map text is removed.
    # ─────────────────────────────────────────────────────────────────────────
    HIDE_LABELS = {
        "North America": {
            # Tiny Caribbean islands / territories that produce the clumped text
            # seen in the screenshot.
            "ABW",
            "AIA",
            "ATG",
            "BHS",
            "BRB",
            "CUW",
            "DMA",
            "GRD",
            "KNA",
            "LCA",
            "PRI",
            "SXM",
            "TTO",
            "VCT",
            "TCA",
            "VGB",
            "VIR",
        },

        # Caribbean countries are no longer in this view, so South America
        # generally does not require manual suppression.
        "South America": set(),
    }

    # Large countries that are useful as geographic reference points even when
    # their debt-in-default value is zero.
    ANCHOR_LABELS = {
        "Africa": {
            "ZAF",
            "NGA",
            "EGY",
            "DZA",
            "ETH",
        },

        "Asia": {
            "CHN",
            "IND",
            "JPN",
            "IDN",
            "SAU",
        },

        "Europe": {
            "GBR",
            "FRA",
            "DEU",
            "ESP",
            "ITA",
        },

        "North America": {
            "CAN",
            "USA",
            "MEX",
        },

        "South America": {
            "BRA",
            "ARG",
            "CHL",
            "COL",
            "PER",
        },
    }

    # Hard cap prevents a dense year from filling a region with dozens of names.
    # Defaulting countries receive priority over zero/default-free anchor labels.
    MAX_LABELS = {
        "Africa": 24,
        "Asia": 22,
        "Europe": 18,
        "North America": 13,
        "South America": 12,
    }

    def format_country_label(row):
        country = row["country"]

        name = SHORT_LABELS.get(
            country,
            country.upper(),
        )

        if "<br>" not in name and len(name) > 15:
            words = name.split()

            if len(words) >= 2:
                midpoint = len(words) // 2

                name = (
                    " ".join(words[:midpoint])
                    + "<br>"
                    + " ".join(words[midpoint:])
                )

        # Only major default values are printed directly on the map.
        if (
            pd.notna(row["value"])
            and row["value"] >= 10_000
        ):
            return (
                f"<b>{name}</b><br>"
                f"${row['value'] / 1_000:,.1f}B"
            )

        return name

    # ─────────────────────────────────────────────────────────────────────────
    # Map text
    # ─────────────────────────────────────────────────────────────────────────
    if region == "World":
        # World view: continent names only.
        continent_labels = pd.DataFrame(
            [
                {
                    "name": "<b>NORTH<br>AMERICA</b>",
                    "lat": 48,
                    "lon": -108,
                },
                {
                    "name": "<b>SOUTH<br>AMERICA</b>",
                    "lat": -21,
                    "lon": -61,
                },
                {
                    "name": "<b>EUROPE</b>",
                    "lat": 54,
                    "lon": 16,
                },
                {
                    "name": "<b>AFRICA</b>",
                    "lat": 3,
                    "lon": 20,
                },
                {
                    "name": "<b>ASIA</b>",
                    "lat": 39,
                    "lon": 91,
                },
                {
                    "name": "<b>OCEANIA</b>",
                    "lat": -25,
                    "lon": 135,
                },
            ]
        )

        fig_map.add_trace(
            go.Scattergeo(
                lon=continent_labels["lon"],
                lat=continent_labels["lat"],
                text=continent_labels["name"],
                mode="text",
                showlegend=False,
                hoverinfo="skip",
                textfont={
                    "color": "#243447",
                    "size": 15,
                    "family": "Arial",
                },
            )
        )

    elif not view_df.empty:
        label_df = view_df.copy()

        hidden_codes = HIDE_LABELS.get(
            region,
            set(),
        )

        anchor_codes = ANCHOR_LABELS.get(
            region,
            set(),
        )

        # Show labels only when they have useful information:
        #   - country currently has debt in default, or
        #   - country is a large geographic anchor.
        label_df["has_default"] = (
            label_df["value"].fillna(0) > 0
        )

        label_df["is_anchor"] = (
            label_df["code"].isin(anchor_codes)
        )

        label_df = label_df[
            label_df["has_default"]
            | label_df["is_anchor"]
        ].copy()

        # Remove known tiny/cluttered labels.
        label_df = label_df[
            ~label_df["code"].isin(hidden_codes)
        ].copy()

        # If there are still too many labels, retain the most important ones.
        # Defaulting countries rank first, then highest debt values, then anchors.
        label_df["_value_for_sort"] = (
            label_df["value"]
            .fillna(0)
        )

        label_df = label_df.sort_values(
            [
                "has_default",
                "_value_for_sort",
                "is_anchor",
                "country",
            ],
            ascending=[
                False,
                False,
                False,
                True,
            ],
        )

        label_limit = MAX_LABELS.get(
            region,
            20,
        )

        label_df = label_df.head(
            label_limit
        ).copy()

        label_df["plot_lon"] = label_df["lon"]
        label_df["plot_lat"] = label_df["lat"]

        # First apply any exact label position overrides.
        exact_positions = LABEL_POSITIONS.get(
            region,
            {},
        )

        for idx, row in label_df.iterrows():
            if row["code"] in exact_positions:
                exact_lon, exact_lat = exact_positions[
                    row["code"]
                ]

                label_df.at[idx, "plot_lon"] = exact_lon
                label_df.at[idx, "plot_lat"] = exact_lat

        # Then apply small offsets to the remaining labels.
        region_offsets = LABEL_OFFSETS.get(
            region,
            {},
        )

        for idx, row in label_df.iterrows():
            if row["code"] in exact_positions:
                continue

            if row["code"] in region_offsets:
                delta_lon, delta_lat = region_offsets[
                    row["code"]
                ]

                label_df.at[idx, "plot_lon"] += delta_lon
                label_df.at[idx, "plot_lat"] += delta_lat

        label_df["map_text"] = label_df.apply(
            format_country_label,
            axis=1,
        )

        if not label_df.empty:
            fig_map.add_trace(
                go.Scattergeo(
                    lon=label_df["plot_lon"],
                    lat=label_df["plot_lat"],
                    text=label_df["map_text"],
                    mode="text",
                    showlegend=False,
                    hoverinfo="skip",
                    textfont={
                        "color": "#333333",
                        "size": REGION_LABEL_SIZE.get(
                            region,
                            8,
                        ),
                        "family": "Arial",
                    },
                )
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Geographic appearance
    # ─────────────────────────────────────────────────────────────────────────
    geo_layout = {
        "showframe": False,
        "showcoastlines": True,
        "coastlinecolor": "#8c8c8c",
        "coastlinewidth": 0.75,
        "showland": True,
        "landcolor": "#f2f2f2",
        "showocean": True,
        "oceancolor": "#a9c7e8",
        "showlakes": True,
        "lakecolor": "#a9c7e8",
        "showcountries": True,
        "countrycolor": "#8c8c8c",
        "countrywidth": 0.75,
        "bgcolor": "white",
        "projection_type": (
            "natural earth"
            if region == "World"
            else "mercator"
        ),
    }

    if region == "World":
        geo_layout.update(
            lataxis_range=[-58, 85]
        )

    else:
        bounds = REGION_BOUNDS[region]

        geo_layout.update(
            lonaxis={
                "range": list(bounds["lon"]),
                "showgrid": False,
            },
            lataxis={
                "range": list(bounds["lat"]),
                "showgrid": False,
            },
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Legend / layout
    # ─────────────────────────────────────────────────────────────────────────
    legend_title = (
        f"<b>{map_year} total debt in default"
        f"<br>by country (US$ millions)</b>"
        if region != "World"
        else "<b>US$ millions</b>"
    )

    fig_map.update_layout(
        height=REGION_HEIGHTS.get(
            region,
            780,
        ),

        geo=geo_layout,

        title=(
            None
            if region != "World"
            else {
                "text": (
                    f"Total debt in default by country, "
                    f"{map_year} (US$ millions)"
                ),
                "x": 0.01,
                "font": {
                    "size": 14,
                    "color": "#222222",
                },
            }
        ),

        legend={
            "title": {
                "text": legend_title,
                "font": {
                    "size": 13,
                    "color": "#111111",
                },
            },
            "x": 0.02,
            "y": 0.03,
            "xanchor": "left",
            "yanchor": "bottom",
            "bgcolor": "rgba(255,255,255,0.95)",
            "bordercolor": "#c7c7c7",
            "borderwidth": 1,
            "font": {
                "size": 11,
                "color": "#111111",
            },
            "itemsizing": "constant",
            "traceorder": "normal",
        },

        margin={
            "l": 0,
            "r": 0,
            "t": (
                20
                if region != "World"
                else 45
            ),
            "b": 0,
        },

        paper_bgcolor="white",
    )

    show_chart(
        fig_map,
        (
            "debt_default_map_"
            f"{region.lower().replace(' ', '_')}_"
            f"{map_year}.html"
        ),
        "cmap",
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Regional / country extract table
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()

    st.markdown(
        f"### {region} country order — {map_year}"
    )

    table_df = view_df.copy()

    table_df["Debt in default (US$M)"] = (
        table_df["value"]
    )

    table_df["Debt in default (US$B)"] = (
        table_df["value"] / 1_000
    )

    table_df["Order"] = table_df["rank"]

    table_df["Band"] = (
        table_df["band"]
        .fillna("No default / no data")
    )

    table_df["_sort_group"] = np.where(
        table_df["rank"].notna(),
        0,
        1,
    )

    table_df["_sort_rank"] = (
        table_df["rank"]
        .fillna(10_000)
    )

    table_df = table_df.sort_values(
        [
            "_sort_group",
            "_sort_rank",
            "country",
        ],
        ascending=[
            True,
            True,
            True,
        ],
    )

    display_df = table_df[
        [
            "Order",
            "country",
            "code",
            "Debt in default (US$M)",
            "Debt in default (US$B)",
            "Band",
        ]
    ].rename(
        columns={
            "country": "Country",
            "code": "ISO3",
        }
    )

    display_df["Order"] = (
        display_df["Order"]
        .apply(
            lambda x: (
                ""
                if pd.isna(x)
                else int(x)
            )
        )
    )

    metric_1, metric_2, metric_3 = st.columns(3)

    metric_1.metric(
        "Countries shown",
        f"{len(view_df):,}",
    )

    metric_2.metric(
        "Countries with debt in default",
        f"{len(positive):,}",
    )

    metric_3.metric(
        "Debt in default",
        f"${positive['value'].sum() / 1_000:,.1f}B",
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Order": st.column_config.NumberColumn(
                "Order",
                format="%d",
            ),
            "Debt in default (US$M)": (
                st.column_config.NumberColumn(
                    format="$%,.0f"
                )
            ),
            "Debt in default (US$B)": (
                st.column_config.NumberColumn(
                    format="$%,.1f"
                )
            ),
        },
        height=min(
            700,
            38 + 35 * min(
                len(display_df),
                18,
            ),
        ),
    )

    st.caption(
        f"{len(view_df)} countries shown in {region} · "
        f"{len(positive)} have debt in default in {map_year}. "
        "Order ranks defaulting countries from highest to lowest debt in default."
    )


# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()

st.caption(
    "Source: BoC–BoE Sovereign Default Database · "
    "Last update: July 22, 2026 · "
    f"Last observation: {LAST_OBS} · "
    "Built with Streamlit + Plotly"
)
