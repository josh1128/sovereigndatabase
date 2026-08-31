#!/usr/bin/env python3
"""
RECOVER + FIX dashboard.py

Use this after accidentally replacing dashboard.py with the map-only code.

What it does:
1. Searches Git history for the newest complete dashboard.py.
2. Restores that complete dashboard.
3. Applies the regional-map cleanup:
   - zoomed North America
   - correct Caribbean -> North America classification
   - fewer overlapping labels
   - preserves polygons, hover and table data
4. Syntax-checks the final dashboard.py.
5. Saves a backup of your currently broken dashboard.

Run from the repo root:

    python recover_and_fix_dashboard.py
"""

from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(__file__).resolve().parent
DASHBOARD = ROOT / "dashboard.py"
BROKEN_BACKUP = ROOT / "dashboard_broken_backup.py"


def run_git(*args):
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def looks_like_complete_dashboard(text):
    required = [
        "import streamlit as st",
        "def load_data",
        "def show_chart",
        "tab_a, tab_b, tab_c, tab_map = st.tabs",
        "with tab_map:",
        "COUNTRY_CENTROIDS",
        "df_countries",
    ]
    return (
        len(text.splitlines()) > 900
        and all(token in text for token in required)
    )


def find_complete_dashboard_in_git():
    code, stdout, stderr = run_git(
        "log",
        "--format=%H",
        "--all",
        "--",
        "dashboard.py",
    )

    if code != 0:
        raise RuntimeError(
            "Could not inspect Git history.\n"
            f"{stderr}"
        )

    commits = [
        line.strip()
        for line in stdout.splitlines()
        if line.strip()
    ]

    if not commits:
        raise RuntimeError(
            "No dashboard.py history was found in this Git repository."
        )

    print(f"Checking {len(commits)} dashboard.py revisions...")

    for commit in commits:
        code, content, _ = run_git(
            "show",
            f"{commit}:dashboard.py",
        )

        if code == 0 and looks_like_complete_dashboard(content):
            print(
                "✓ Found complete dashboard.py in commit "
                f"{commit[:8]}"
            )
            return content, commit

    raise RuntimeError(
        "Could not find a complete dashboard.py in Git history."
    )


def replace_once(text, old, new, label):
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"Could not safely replace {label}. "
            f"Expected 1 match, found {count}."
        )

    return text.replace(old, new, 1)


def apply_map_changes(text):
    # ------------------------------------------------------------------
    # 1. Zoom North America
    # ------------------------------------------------------------------
    old_bounds = """    REGION_BOUNDS = {
        'World': None,
        'Africa': dict(lon=(-20, 55), lat=(-36, 38)),
        'Asia': dict(lon=(25, 180), lat=(-12, 78)),
        'Europe': dict(lon=(-13, 43), lat=(34, 72)),
        'North America': dict(lon=(-170, -50), lat=(5, 82)),
        'South America': dict(lon=(-83, -32), lat=(-58, 14)),
    }
"""

    new_bounds = """    REGION_BOUNDS = {
        'World': None,
        'Africa': dict(lon=(-20, 55), lat=(-36, 38)),
        'Asia': dict(lon=(25, 180), lat=(-12, 78)),
        'Europe': dict(lon=(-13, 43), lat=(34, 72)),

        # Tighter view: emphasizes the continental US, southern Canada,
        # Mexico, Central America and the Caribbean.
        'North America': dict(lon=(-130, -55), lat=(5, 55)),

        'South America': dict(lon=(-83, -32), lat=(-58, 14)),
    }
"""

    text = replace_once(
        text,
        old_bounds,
        new_bounds,
        "REGION_BOUNDS",
    )

    # ------------------------------------------------------------------
    # 2. Correct regional classification
    # ------------------------------------------------------------------
    old_region = """    REGION_OVERRIDES = {
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
"""

    new_region = """    REGION_OVERRIDES = {
        'Europe': {'GBR', 'IRL', 'ISL', 'PRT', 'ESP', 'FRA', 'BEL', 'NLD', 'LUX', 'DEU',
                   'CHE', 'AUT', 'ITA', 'MLT', 'DNK', 'NOR', 'SWE', 'FIN', 'EST', 'LVA',
                   'LTU', 'POL', 'CZE', 'SVK', 'HUN', 'SVN', 'HRV', 'BIH', 'SRB', 'MNE',
                   'MKD', 'ALB', 'GRC', 'BGR', 'ROU', 'MDA', 'UKR', 'BLR'},

        'Asia': {'RUS', 'TUR', 'GEO', 'ARM', 'AZE', 'CYP', 'KAZ'},

        # Explicit membership prevents Caribbean countries from being
        # classified as South America because of overlapping map bounds.
        'North America': {
            'CAN', 'USA', 'MEX',
            'BLZ', 'GTM', 'HND', 'SLV', 'NIC', 'CRI', 'PAN',
            'BHS', 'CUB', 'JAM', 'HTI', 'DOM', 'PRI',
            'ABW', 'AIA', 'ATG', 'BRB', 'CUW', 'DMA', 'GRD',
            'KNA', 'LCA', 'SXM', 'TTO', 'VCT',
        },

        'South America': {
            'ARG', 'BOL', 'BRA', 'CHL', 'COL', 'ECU',
            'GUY', 'PRY', 'PER', 'SUR', 'URY', 'VEN',
        },
    }

    def country_region(code, lat, lon):
        # Explicit membership takes priority.
        for rg in ['Europe', 'Asia', 'North America', 'South America']:
            if code in REGION_OVERRIDES.get(rg, set()):
                return rg

        # Geographic fallback for countries not explicitly listed above.
        for rg in ['Africa', 'South America', 'North America', 'Europe', 'Asia']:
            b = REGION_BOUNDS[rg]
            if b['lon'][0] <= lon <= b['lon'][1] and b['lat'][0] <= lat <= b['lat'][1]:
                return rg

        return 'Other'
"""

    text = replace_once(
        text,
        old_region,
        new_region,
        "REGION_OVERRIDES / country_region",
    )

    # ------------------------------------------------------------------
    # 3. Update user-facing caption
    # ------------------------------------------------------------------
    old_caption = """    st.caption(
        "Country polygons are always shown. Labels adapt to the view: the world map "
        "uses selective labels to avoid crowding, while regional extracts show all "
        "country names. Exact values and ranking are available in the table below."
    )
"""

    new_caption = """    st.caption(
        "Country polygons are always shown. The world view uses continent names, "
        "while regional extracts automatically suppress crowded labels. "
        "Hidden country names remain available through hover and the table below."
    )
"""

    text = replace_once(
        text,
        old_caption,
        new_caption,
        "map caption",
    )

    # ------------------------------------------------------------------
    # 4. Add label suppression / anchor rules
    # ------------------------------------------------------------------
    old_sizes = """    REGION_LABEL_SIZE = {
        'World': 7.5,
        'Africa': 9,
        'Asia': 8,
        'Europe': 7,
        'North America': 8,
        'South America': 9,
    }

"""

    new_sizes = """    REGION_LABEL_SIZE = {
        'World': 7.5,
        'Africa': 9,
        'Asia': 8,
        'Europe': 7,
        'North America': 9,
        'South America': 9,
    }

    # Suppress tiny labels that overlap heavily. These countries remain
    # visible as polygons and through hover/table data.
    REGION_HIDE_LABELS = {
        'North America': {
            'ABW', 'AIA', 'ATG', 'BHS', 'BRB', 'CUW',
            'DMA', 'GRD', 'KNA', 'LCA', 'PRI', 'SXM',
            'TTO', 'VCT',
        },
        'South America': set(),
    }

    # Large geographic reference countries stay labelled even if their
    # selected-year default value is zero.
    REGION_ANCHOR_LABELS = {
        'North America': {'CAN', 'USA', 'MEX'},
        'South America': {'BRA', 'ARG', 'CHL', 'COL', 'PER'},
        'Europe': {'GBR', 'FRA', 'DEU', 'ESP', 'ITA'},
        'Africa': {'ZAF', 'NGA', 'EGY', 'DZA', 'ETH'},
        'Asia': {'CHN', 'IND', 'JPN', 'IDN', 'SAU'},
    }

    # Prevent a high-default year from creating another wall of text.
    REGION_MAX_LABELS = {
        'North America': 13,
        'South America': 12,
        'Europe': 18,
        'Africa': 24,
        'Asia': 22,
    }

"""

    text = replace_once(
        text,
        old_sizes,
        new_sizes,
        "REGION_LABEL_SIZE",
    )

    # ------------------------------------------------------------------
    # 5. Replace the regional "label everything" behavior
    # ------------------------------------------------------------------
    old_labels = """    elif not view_df.empty:
        # Regional extracts show every country name, with offsets for crowded areas.
        label_df = view_df.copy()

        label_df['plot_lon'] = label_df['lon']
        label_df['plot_lat'] = label_df['lat']

        region_offsets = LABEL_OFFSETS.get(region, {})
        for idx, row in label_df.iterrows():
            if row['code'] in region_offsets:
                dx, dy = region_offsets[row['code']]
                label_df.at[idx, 'plot_lon'] += dx
                label_df.at[idx, 'plot_lat'] += dy

        label_df['map_text'] = label_df.apply(format_country_label, axis=1)

        fig_map.add_trace(go.Scattergeo(
            lon=label_df['plot_lon'],
            lat=label_df['plot_lat'],
            text=label_df['map_text'],
            mode='text',
            showlegend=False,
            hoverinfo='skip',
            textfont=dict(
                color='#333333',
                size=REGION_LABEL_SIZE.get(region, 8),
                family='Arial'
            )
        ))
"""

    new_labels = """    elif not view_df.empty:
        # Regional extracts use selective labels instead of printing every
        # country name. Polygons, hover information and table rows are unchanged.
        label_df = view_df.copy()

        hidden_codes = REGION_HIDE_LABELS.get(region, set())
        anchor_codes = REGION_ANCHOR_LABELS.get(region, set())

        label_df['has_default'] = label_df['value'].fillna(0) > 0
        label_df['is_anchor'] = label_df['code'].isin(anchor_codes)

        # Keep actual defaulting countries plus a few large orientation labels.
        label_df = label_df[
            label_df['has_default'] | label_df['is_anchor']
        ].copy()

        # Remove tiny/clumped labels.
        label_df = label_df[
            ~label_df['code'].isin(hidden_codes)
        ].copy()

        # If there are still many labels, prioritize the largest defaults.
        label_df['_label_value'] = label_df['value'].fillna(0)

        label_df = label_df.sort_values(
            ['has_default', '_label_value', 'is_anchor', 'country'],
            ascending=[False, False, False, True],
        )

        label_df = label_df.head(
            REGION_MAX_LABELS.get(region, 20)
        ).copy()

        label_df['plot_lon'] = label_df['lon']
        label_df['plot_lat'] = label_df['lat']

        # Canada's centroid is too far north for the tighter view.
        # Put the major North American anchor labels in readable locations.
        if region == 'North America':
            manual_positions = {
                'CAN': (-106.0, 51.0),
                'USA': (-98.0, 38.0),
                'MEX': (-102.0, 23.5),
            }

            for idx, row in label_df.iterrows():
                if row['code'] in manual_positions:
                    label_df.at[idx, 'plot_lon'] = manual_positions[row['code']][0]
                    label_df.at[idx, 'plot_lat'] = manual_positions[row['code']][1]

        region_offsets = LABEL_OFFSETS.get(region, {})

        for idx, row in label_df.iterrows():
            # Do not offset the three exact North America anchor positions.
            if (
                region == 'North America'
                and row['code'] in {'CAN', 'USA', 'MEX'}
            ):
                continue

            if row['code'] in region_offsets:
                dx, dy = region_offsets[row['code']]
                label_df.at[idx, 'plot_lon'] += dx
                label_df.at[idx, 'plot_lat'] += dy

        label_df['map_text'] = label_df.apply(
            format_country_label,
            axis=1,
        )

        if not label_df.empty:
            fig_map.add_trace(go.Scattergeo(
                lon=label_df['plot_lon'],
                lat=label_df['plot_lat'],
                text=label_df['map_text'],
                mode='text',
                showlegend=False,
                hoverinfo='skip',
                textfont=dict(
                    color='#333333',
                    size=REGION_LABEL_SIZE.get(region, 8),
                    family='Arial'
                )
            ))
"""

    text = replace_once(
        text,
        old_labels,
        new_labels,
        "regional label rendering",
    )

    return text


def main():
    if DASHBOARD.exists():
        shutil.copy2(
            DASHBOARD,
            BROKEN_BACKUP,
        )
        print(
            f"✓ Saved current dashboard as {BROKEN_BACKUP.name}"
        )

    complete_text, commit = find_complete_dashboard_in_git()

    print(
        f"Restoring complete dashboard from {commit[:8]}..."
    )

    fixed = apply_map_changes(
        complete_text
    )

    # Verify the critical dependency exists before the map block.
    tab_definition = fixed.find(
        "tab_a, tab_b, tab_c, tab_map = st.tabs"
    )
    map_usage = fixed.find(
        "with tab_map:"
    )

    if tab_definition == -1:
        raise RuntimeError(
            "Final file is missing the tab_map definition."
        )

    if map_usage == -1:
        raise RuntimeError(
            "Final file is missing the map tab."
        )

    if tab_definition > map_usage:
        raise RuntimeError(
            "tab_map is still being used before it is defined."
        )

    # Python syntax check.
    compile(
        fixed,
        str(DASHBOARD),
        "exec",
    )

    DASHBOARD.write_text(
        fixed,
        encoding="utf-8",
    )

    print("")
    print("✓ dashboard.py successfully recovered and fixed")
    print(
        f"✓ Final file: {len(fixed.splitlines())} lines"
    )
    print("✓ Python syntax check passed")
    print("✓ tab_map is defined before with tab_map")
    print("")
    print("Regional changes applied:")
    print("  - North America zoomed in")
    print("  - Caribbean assigned to North America")
    print("  - tiny overlapping labels hidden")
    print("  - major anchor countries retained")
    print("  - high-default years capped to readable label counts")
    print("")
    print("Next:")
    print("  git add dashboard.py")
    print('  git commit -m "Fix regional map labels and zoom"')
    print("  git push")


if __name__ == "__main__":
    main()
