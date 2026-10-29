import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta, date

# -----------------------------------------------------------------------------
# PAGE CONFIG & CYBERPUNK HUD STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EXCHANGE RATES TERMINAL",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Rajdhani:wght@500;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at 15% 15%, #0d1527 0%, #050811 100%);
        color: #e2e8f0;
        font-family: 'JetBrains Mono', monospace;
    }

    h1, h2, h3, h4, h5 {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #070b14 !important;
        border-right: 1px solid rgba(0, 240, 255, 0.15) !important;
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.6);
    }

    /* Checkbox Glow */
    div[data-testid="stCheckbox"] label {
        font-family: 'JetBrains Mono', monospace;
        color: #94a3b8;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stCheckbox"]:hover label {
        color: #00f0ff !important;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
    }

    /* Dual-Conversion HUD Cards */
    .dual-hud-card {
        background: rgba(11, 19, 38, 0.7);
        border: 1px solid rgba(0, 240, 255, 0.25);
        border-radius: 8px;
        padding: 10px 16px;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.05);
        backdrop-filter: blur(12px);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .dual-side {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    .dual-side.right {
        text-align: right;
        align-items: flex-end;
    }
    .dual-side.left {
        text-align: left;
        align-items: flex-start;
    }
    .dual-divider {
        width: 1px;
        height: 52px;
        background: linear-gradient(180deg, transparent, rgba(0, 240, 255, 0.4), transparent);
        margin: 0 12px;
    }
    .pair-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: #cbd5e1;
        letter-spacing: 1px;
    }
    .pair-val {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.55rem;
        font-weight: 700;
        line-height: 1.1;
    }
    .wise-tag {
        font-size: 0.75rem;
        color: #94A3B8;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        margin-top: 2px;
    }
    .pair-delta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        margin-top: 3px;
        font-weight: 600;
    }
    .delta-pos { color: #10B981; }
    .delta-neg { color: #F43F5E; }

    /* Mini Cross-Rate Matrix Dashboard */
    .mini-matrix-container {
        background: rgba(9, 15, 30, 0.85);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-radius: 8px;
        padding: 8px 12px;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.08);
    }
    .mini-matrix-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        color: #00F0FF;
        letter-spacing: 1px;
        margin-bottom: 6px;
        text-align: center;
    }
    .mini-matrix-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.72rem;
        text-align: center;
    }
    .mini-matrix-table th {
        padding: 2px 4px;
        font-weight: 700;
        border-bottom: 1px solid rgba(0, 240, 255, 0.2);
        text-align: center !important;
    }
    .mini-matrix-table td {
        padding: 3px 4px;
        color: #e2e8f0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        text-align: center !important;
    }
    .matrix-diag { color: #475569 !important; }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.05rem !important;
        letter-spacing: 1px !important;
        color: #64748b !important;
        background-color: transparent !important;
        border-bottom: 2px solid transparent !important;
        padding-top: 4px !important;
        padding-bottom: 4px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00f0ff !important;
        border-bottom-color: #00f0ff !important;
        text-shadow: 0 0 12px rgba(0, 240, 255, 0.6) !important;
    }

    /* Plotly Containers */
    .stPlotlyChart {
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 6px;
        background: rgba(8, 14, 28, 0.4);
        padding: 2px;
        margin-bottom: 6px;
    }

    /* Futuristic Centered Data Table */
    .cyber-table-container {
        max-height: 460px;
        overflow-y: auto;
        overflow-x: auto;
        border: 1px solid rgba(0, 240, 255, 0.25);
        border-radius: 8px;
        background: rgba(8, 14, 28, 0.7);
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .cyber-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
    }
    .cyber-table th {
        position: sticky;
        top: 0;
        background: #0b1426 !important;
        color: #94a3b8;
        padding: 10px 14px;
        border-bottom: 2px solid rgba(0, 240, 255, 0.4);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        text-align: center !important;
        vertical-align: middle;
        white-space: nowrap;
        z-index: 2;
    }
    .cyber-table td {
        padding: 7px 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.03);
        color: #cbd5e1;
        text-align: center !important;
        vertical-align: middle;
        white-space: nowrap;
    }
    .cyber-table tr:hover td {
        background: rgba(0, 240, 255, 0.06);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CONSTANTS & PALETTE
# -----------------------------------------------------------------------------
ALL_CURRENCIES = ["EUR", "USD", "NOK", "BRL"]
# Added "1 Week" option
TIMEFRAMES = ["1 Week", "1 Month", "6 Months", "1 Year", "3 Years", "5 Years", "Custom"]

NEON_COLORS = {
    "EUR": "#00F0FF",  # Cyan
    "USD": "#10B981",  # Emerald
    "NOK": "#A855F7",  # Purple
    "BRL": "#F59E0B"   # Amber
}

WISE_FEES = {
    ("EUR", "USD"): 0.0038,
    ("USD", "EUR"): 0.0042,
    ("EUR", "NOK"): 0.0050,
    ("NOK", "EUR"): 0.0052,
    ("EUR", "BRL"): 0.0118,
    ("BRL", "EUR"): 0.0125,
    ("USD", "NOK"): 0.0052,
    ("NOK", "USD"): 0.0054,
    ("USD", "BRL"): 0.0122,
    ("BRL", "USD"): 0.0128,
    ("NOK", "BRL"): 0.0135,
    ("BRL", "NOK"): 0.0138,
}

def calc_wise_rate(series_or_val, from_c, to_c):
    fee = WISE_FEES.get((from_c, to_c), 0.0050)
    return series_or_val * (1.0 - fee)

# -----------------------------------------------------------------------------
# LEFT COLUMN (SIDEBAR CONTROLS)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
            <div style="width:8px; height:8px; background:#00f0ff; border-radius:50%; box-shadow:0 0 8px #00f0ff;"></div>
            <span style="font-size:0.75rem; color:#00f0ff; letter-spacing:1px; font-weight:700;">CONTROL PANEL</span>
        </div>
    """, unsafe_allow_html=True)

    # 1. Base Currency (DEFAULT: BRL)
    st.markdown("### // BASE CURRENCY")
    if "base_currency" not in st.session_state:
        st.session_state.base_currency = "BRL"
        for c in ALL_CURRENCIES:
            st.session_state[f"curr_{c}"] = (c == "BRL")

    def on_currency_change(selected_curr):
        if st.session_state[f"curr_{selected_curr}"]:
            st.session_state.base_currency = selected_curr
            for c in ALL_CURRENCIES:
                if c != selected_curr:
                    st.session_state[f"curr_{c}"] = False
        else:
            st.session_state[f"curr_{selected_curr}"] = True

    for c in ALL_CURRENCIES:
        st.checkbox(label=f"{c}", key=f"curr_{c}", on_change=on_currency_change, args=(c,))

    base_currency = st.session_state.base_currency
    target_currencies = [c for c in ALL_CURRENCIES if c != base_currency]

    st.markdown("<hr style='border: 0.5px solid rgba(0, 240, 255, 0.2);'>", unsafe_allow_html=True)

    # 2. Timescale (DEFAULT: 1 Month)
    st.markdown("### // TIMEFRAME")
    if "selected_tf" not in st.session_state:
        st.session_state.selected_tf = "1 Month"
        for tf in TIMEFRAMES:
            st.session_state[f"tf_{tf}"] = (tf == "1 Month")

    def on_timeframe_change(selected_tf):
        if st.session_state[f"tf_{selected_tf}"]:
            st.session_state.selected_tf = selected_tf
            for tf in TIMEFRAMES:
                if tf != selected_tf:
                    st.session_state[f"tf_{tf}"] = False
        else:
            st.session_state[f"tf_{selected_tf}"] = True

    for tf in TIMEFRAMES:
        st.checkbox(label=tf, key=f"tf_{tf}", on_change=on_timeframe_change, args=(tf,))

    timeframe = st.session_state.selected_tf
    today = date.today()

    # 3. Custom Date Range Slider / Predefined Calculations
    if timeframe == "Custom":
        st.markdown("#### // RANGE SELECTOR")
        slider_min = date(2010, 1, 1)
        slider_max = today
        default_start = today - timedelta(days=365)

        date_range = st.slider(
            "Time Horizon",
            min_value=slider_min,
            max_value=slider_max,
            value=(default_start, slider_max),
            format="YYYY-MM-DD",
            label_visibility="collapsed"
        )
        start_date, end_date = date_range
    else:
        end_date = today
        if timeframe == "1 Week":
            start_date = today - timedelta(days=7)
        elif timeframe == "1 Month":
            start_date = today - timedelta(days=30)
        elif timeframe == "6 Months":
            start_date = today - timedelta(days=180)
        elif timeframe == "1 Year":
            start_date = today - timedelta(days=365)
        elif timeframe == "3 Years":
            start_date = today - timedelta(days=365 * 3)
        elif timeframe == "5 Years":
            start_date = today - timedelta(days=365 * 5)

    st.markdown("<hr style='border: 0.5px solid rgba(0, 240, 255, 0.2);'>", unsafe_allow_html=True)

    # 4. Wise Benchmark Overlay Toggle
    st.markdown("### // BENCHMARKS")
    show_wise = st.checkbox("Overlay Wise Rates on Charts", value=True)

# -----------------------------------------------------------------------------
# DATA RETRIEVAL (BASE EUR → ALL CROSS RATES)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_all_rates(start_str, end_str):
    url = f"https://api.frankfurter.dev/v1/{start_str}..{end_str}"
    params = {"base": "EUR", "symbols": "USD,NOK,BRL"}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    data = response.json()
    df = pd.DataFrame.from_dict(data["rates"], orient="index")
    df.index = pd.to_datetime(df.index)
    df["EUR"] = 1.0
    return df.sort_index()

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

with st.spinner(">> SYNCING QUANTITATIVE FEED..."):
    df_raw = fetch_all_rates(start_str, end_str)

# -----------------------------------------------------------------------------
# MAIN PAGE
# -----------------------------------------------------------------------------
if df_raw is None or df_raw.empty:
    st.error("NO SIGNAL DETECTED FOR THE SELECTED PARAMETERS.")
else:
    # -------------------------------------------------------------------------
    # TOP HEADER & MINI DASHBOARD (ALL 12 PERMUTATIONS)
    # -------------------------------------------------------------------------
    head_left, head_right = st.columns([1.1, 1.3])

    with head_left:
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:12px; margin-top:2px;">
                <div style="
                    background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(168, 85, 247, 0.15));
                    border: 1px solid #00F0FF;
                    border-radius: 8px;
                    padding: 6px 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 0 12px rgba(0, 240, 255, 0.35);">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00F0FF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 7H4l4-4"/>
                        <path d="M4 17h16l-4 4"/>
                    </svg>
                </div>
                <div>
                    <h3 style="margin:0; font-family:'Rajdhani', sans-serif; letter-spacing:1.5px; color:#F1F5F9;">
                        EXCHANGE RATES // 1 {base_currency}
                    </h3>
                    <div style="font-size:0.75rem; color:#64748B;">
                        WINDOW: <span style="color:#00f0ff;">{start_str}</span> → <span style="color:#00f0ff;">{end_str}</span> | ECB REFERENCE
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with head_right:
        matrix_rows = []
        for r_curr in ALL_CURRENCIES:
            tds = [f"<td style='font-weight:700; color:{NEON_COLORS[r_curr]};'>{r_curr}</td>"]
            for c_curr in ALL_CURRENCIES:
                if r_curr == c_curr:
                    tds.append("<td class='matrix-diag'>—</td>")
                else:
                    val = df_raw[c_curr].iloc[-1] / df_raw[r_curr].iloc[-1]
                    tds.append(f"<td>{val:.4f}</td>")
            matrix_rows.append(f"<tr>{''.join(tds)}</tr>")

        header_th = "".join([f"<th style='color:{NEON_COLORS[c]};'>{c}</th>" for c in ALL_CURRENCIES])
        matrix_html = (
            "<div class='mini-matrix-container'>"
            "<div class='mini-matrix-title'>⚡ ALL PERMUTATIONS // CROSS-RATES (LATEST)</div>"
            "<table class='mini-matrix-table'>"
            f"<thead><tr><th style='color:#64748B;'>FROM \\ TO</th>{header_th}</tr></thead>"
            f"<tbody>{''.join(matrix_rows)}</tbody>"
            "</table>"
            "</div>"
        )
        st.markdown(matrix_html, unsafe_allow_html=True)

    st.write("")

    # -------------------------------------------------------------------------
    # DUAL-DIRECTION RATE BOXES (WITH WISE RATES IN PARENTHESES)
    # -------------------------------------------------------------------------
    cols_metrics = st.columns(3)
    for i, curr in enumerate(target_currencies):
        # Direct
        dir_series = df_raw[curr] / df_raw[base_currency]
        dir_latest = dir_series.iloc[-1]
        dir_wise_latest = calc_wise_rate(dir_latest, base_currency, curr)
        dir_first = dir_series.iloc[0]
        dir_delta = ((dir_latest - dir_first) / dir_first) * 100
        dir_class = "delta-pos" if dir_delta >= 0 else "delta-neg"
        dir_sym = "+" if dir_delta >= 0 else ""

        # Inverse
        inv_series = 1.0 / dir_series
        inv_latest = inv_series.iloc[-1]
        inv_wise_latest = calc_wise_rate(inv_latest, curr, base_currency)
        inv_first = inv_series.iloc[0]
        inv_delta = ((inv_latest - inv_first) / inv_first) * 100
        inv_class = "delta-pos" if inv_delta >= 0 else "delta-neg"
        inv_sym = "+" if inv_delta >= 0 else ""

        accent = NEON_COLORS.get(curr, "#00F0FF")

        with cols_metrics[i]:
            card_html = (
                "<div class='dual-hud-card'>"
                "<div class='dual-side left'>"
                f"<div class='pair-label'>{base_currency} / {curr}</div>"
                f"<div class='pair-val' style='color:{accent}; text-shadow:0 0 8px {accent}55;'>{dir_latest:.4f}</div>"
                f"<div class='wise-tag'>(Wise: <span style='color:#F1F5F9;'>{dir_wise_latest:.4f}</span>)</div>"
                f"<div class='pair-delta {dir_class}'>{dir_sym}{dir_delta:.2f}%</div>"
                "</div>"
                "<div class='dual-divider'></div>"
                "<div class='dual-side right'>"
                f"<div class='pair-label'>{curr} / {base_currency}</div>"
                f"<div class='pair-val' style='color:#F1F5F9; text-shadow:0 0 8px rgba(241,245,249,0.25);'>{inv_latest:.4f}</div>"
                f"<div class='wise-tag'>(Wise: <span style='color:#00F0FF;'>{inv_wise_latest:.4f}</span>)</div>"
                f"<div class='pair-delta {inv_class}'>{inv_sym}{inv_delta:.2f}%</div>"
                "</div>"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TABS
    # -------------------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs([
        "▣ EXCHANGE RATES", 
        "◈ NORMALIZED OVERLAY (%)", 
        "▤ RAW MATRIX"
    ])

    dark_layout_base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(7, 12, 22, 0.4)",
        font=dict(family="JetBrains Mono", color="#94A3B8", size=10),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0B132B",
            font_size=11,
            font_family="JetBrains Mono",
            font_color="#00F0FF",
            bordercolor="rgba(0,240,255,0.4)"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            zeroline=False,
            showline=True,
            linecolor="rgba(0,240,255,0.15)"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            zeroline=False,
            showline=True,
            linecolor="rgba(0,240,255,0.15)",
            autorange=True
        )
    )

    # --- TAB 1: EXCHANGE RATES (MARKET VS WISE HISTORICAL OVERLAY) ---
    with tab1:
        c1, c2, c3 = st.columns(3)
        cols_plot = [c1, c2, c3]

        for i, curr in enumerate(target_currencies):
            accent = NEON_COLORS.get(curr, "#00F0FF")
            dir_rates = df_raw[curr] / df_raw[base_currency]
            inv_rates = 1.0 / dir_rates

            with cols_plot[i]:
                # 1. Direct Rate Plot (Top)
                fig_dir = go.Figure()
                fig_dir.add_trace(go.Scatter(
                    x=df_raw.index,
                    y=dir_rates,
                    mode="lines",
                    name="ECB Rate",
                    line=dict(color=accent, width=2.0)
                ))
                if show_wise:
                    fig_dir.add_trace(go.Scatter(
                        x=df_raw.index,
                        y=calc_wise_rate(dir_rates, base_currency, curr),
                        mode="lines",
                        name="Wise Rate",
                        line=dict(color=accent, width=1.6, dash="dash")
                    ))
                fig_dir.update_layout(
                    **dark_layout_base,
                    title=dict(
                        text=f"<b style='color:{accent};'>{base_currency} / {curr}</b>" + (" <span style='font-size:10px; color:#94A3B8;'>vs Wise</span>" if show_wise else ""),
                        font=dict(family="Rajdhani", size=15)
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(size=9)
                    ) if show_wise else dict(visible=False),
                    margin=dict(l=6, r=6, t=28, b=6),
                    height=190
                )
                st.plotly_chart(fig_dir, use_container_width=True)

                # 2. Inverse Rate Plot (Underneath)
                fig_inv = go.Figure()
                fig_inv.add_trace(go.Scatter(
                    x=df_raw.index,
                    y=inv_rates,
                    mode="lines",
                    name="ECB Rate",
                    line=dict(color=accent, width=2.0)
                ))
                if show_wise:
                    fig_inv.add_trace(go.Scatter(
                        x=df_raw.index,
                        y=calc_wise_rate(inv_rates, curr, base_currency),
                        mode="lines",
                        name="Wise Rate",
                        line=dict(color=accent, width=1.6, dash="dash")
                    ))
                fig_inv.update_layout(
                    **dark_layout_base,
                    title=dict(
                        text=f"<b style='color:{accent};'>{curr} / {base_currency}</b> <span style='font-size:10px; color:#64748B;'>(INVERSE" + (" vs Wise" if show_wise else "") + ")</span>",
                        font=dict(family="Rajdhani", size=15)
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(size=9)
                    ) if show_wise else dict(visible=False),
                    margin=dict(l=6, r=6, t=28, b=6),
                    height=190
                )
                st.plotly_chart(fig_inv, use_container_width=True)

    # --- TAB 2: NORMALIZED DRIFT ---
    with tab2:
        st.markdown("<p style='letter-spacing:1px; color:#64748B; font-size:0.8rem; margin-bottom:4px;'>COMPARATIVE PERFORMANCE INDEX (BASE ZERO)</p>", unsafe_allow_html=True)
        
        df_base_rates = pd.DataFrame(index=df_raw.index)
        for curr in target_currencies:
            df_base_rates[curr] = df_raw[curr] / df_raw[base_currency]
            
        df_pct = ((df_base_rates / df_base_rates.iloc[0]) - 1.0) * 100.0

        fig_norm = go.Figure()
        for curr in target_currencies:
            accent = NEON_COLORS.get(curr, "#00F0FF")
            fig_norm.add_trace(go.Scatter(
                x=df_pct.index,
                y=df_pct[curr],
                mode="lines",
                name=f"{curr} (vs {base_currency})",
                line=dict(color=accent, width=2.2)
            ))

        fig_norm.update_layout(
            **dark_layout_base,
            title=dict(
                text="<b>RELATIVE ASSET DRIFT (%)</b>",
                font=dict(family="Rajdhani", size=17, color="#00F0FF")
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11)
            ),
            yaxis_ticksuffix="%",
            height=400
        )
        st.plotly_chart(fig_norm, use_container_width=True)

    # --- TAB 3: RAW MATRIX ---
    with tab3:
        permutations = [
            ("EUR", "USD"), ("USD", "EUR"),
            ("EUR", "NOK"), ("NOK", "EUR"),
            ("EUR", "BRL"), ("BRL", "EUR"),
            ("USD", "NOK"), ("NOK", "USD"),
            ("USD", "BRL"), ("BRL", "USD"),
            ("NOK", "BRL"), ("BRL", "NOK")
        ]

        th_cells = ["<th>DATE</th>"]
        for fc, tc in permutations:
            th_cells.append(
                f"<th><span style='color:{NEON_COLORS[fc]};font-weight:700;'>{fc}</span> / "
                f"<span style='color:{NEON_COLORS[tc]};font-weight:700;'>{tc}</span></th>"
            )
        thead_html = f"<thead><tr>{''.join(th_cells)}</tr></thead>"

        reversed_dates = df_raw.index[::-1]
        tbody_rows = []
        for d in reversed_dates:
            d_str = d.strftime("%Y-%m-%d")
            tds = [f"<td>{d_str}</td>"]
            for fc, tc in permutations:
                val = df_raw.loc[d, tc] / df_raw.loc[d, fc]
                tds.append(f"<td>{val:.4f}</td>")
            tbody_rows.append(f"<tr>{''.join(tds)}</tr>")
        
        tbody_html = f"<tbody>{''.join(tbody_rows)}</tbody>"

        raw_table_html = (
            "<div class='cyber-table-container'>"
            f"<table class='cyber-table'>{thead_html}{tbody_html}</table>"
            "</div>"
        )
        st.markdown(raw_table_html, unsafe_allow_html=True)