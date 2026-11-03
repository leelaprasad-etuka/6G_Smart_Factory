from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="6G Smart Factory Network Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_PATH = Path(__file__).resolve().parent / "Thales_Group_Manufacturing.csv"


@st.cache_data(show_spinner="Loading and indexing 6G telemetry data...")
def load_and_process_data(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        st.error(f"Dataset not found at: {file_path}")
        st.stop()

    df = pd.read_csv(file_path)
    df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")

    lat_min, lat_max = df["Network_Latency_ms"].min(), df["Network_Latency_ms"].max()
    pkt_min, pkt_max = df["Packet_Loss_%"].min(), df["Packet_Loss_%"].max()

    lat_norm = (df["Network_Latency_ms"] - lat_min) / (lat_max - lat_min)
    pkt_norm = (df["Packet_Loss_%"] - pkt_min) / (pkt_max - pkt_min)

    df["Network_Stability_Index"] = (1.0 - (0.5 * lat_norm + 0.5 * pkt_norm)) * 100.0

    df["Network_Quality"] = pd.qcut(
        df["Network_Stability_Index"],
        q=3,
        labels=["Low", "Medium", "High"]
    ).astype(str)

    df["Stability_Period"] = np.where(
        df["Network_Stability_Index"] >= 50.0, "Stable", "Unstable"
    )

    df["Latency_Band"] = pd.cut(
        df["Network_Latency_ms"],
        bins=[0.0, 15.0, 35.0, 100.0],
        labels=["Real-Time (<15ms)", "Moderate (15-35ms)", "Delayed (>35ms)"],
        include_lowest=True
    ).astype(str)

    df["Packet_Loss_Band"] = pd.cut(
        df["Packet_Loss_%"],
        bins=[-0.01, 1.5, 3.5, 100.0],
        labels=["Low (<1.5%)", "Moderate (1.5-3.5%)", "Spike (>3.5%)"],
        include_lowest=True
    ).astype(str)

    eff_map = {"Low": 1, "Medium": 2, "High": 3}
    df["Efficiency_Score"] = df["Efficiency_Status"].map(eff_map)

    return df


def safe_slope(x: pd.Series, y: pd.Series) -> float:
    if len(x) < 2 or x.nunique() < 2:
        return 0.0
    return float(np.polyfit(x, y, 1)[0])


def safe_corr(x: pd.Series, y: pd.Series) -> float:
    if len(x) < 2 or x.nunique() < 2 or y.nunique() < 2:
        return 0.0
    val = x.corr(y)
    return 0.0 if pd.isna(val) else float(val)


df_raw = load_and_process_data(DATA_PATH)

# SIDEBAR USER CAPABILITIES
st.sidebar.header("Filter Controls")

quality_options = ["Low", "Medium", "High"]
selected_quality = st.sidebar.multiselect(
    "1. Network Quality Level",
    options=quality_options,
    default=quality_options
)

efficiency_options = ["High", "Medium", "Low"]
selected_efficiency = st.sidebar.multiselect(
    "2. Efficiency Class Selector",
    options=efficiency_options,
    default=efficiency_options
)

mode_options = ["All"] + sorted(df_raw["Operation_Mode"].dropna().unique().tolist())
selected_mode = st.sidebar.selectbox(
    "3. Operation Mode Dropdown",
    options=mode_options,
    index=0
)

min_date = df_raw["Date_Parsed"].min().date()
max_date = df_raw["Date_Parsed"].max().date()
selected_dates = st.sidebar.date_input(
    "4. Time Window Selector",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply Filters Safely
df = df_raw.copy()
if selected_quality:
    df = df[df["Network_Quality"].isin(selected_quality)]
else:
    df = df.iloc[0:0]

if selected_efficiency:
    df = df[df["Efficiency_Status"].isin(selected_efficiency)]
else:
    df = df.iloc[0:0]

if selected_mode != "All":
    df = df[df["Operation_Mode"] == selected_mode]

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date = pd.to_datetime(selected_dates[0])
    end_date = pd.to_datetime(selected_dates[1])
    df = df[(df["Date_Parsed"] >= start_date) & (df["Date_Parsed"] <= end_date)]
elif isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 1:
    single_date = pd.to_datetime(selected_dates[0])
    df = df[df["Date_Parsed"] == single_date]

st.sidebar.markdown("---")
st.sidebar.write(f"Active Records: {len(df):,} / {len(df_raw):,}")

# MAIN HEADER & KPI SCORECARDS
st.title("Impact of 6G Network Performance on Manufacturing Efficiency")
st.caption("Thales Group Smart Factory Connectivity & Production Diagnostics")

if df.empty:
    st.warning("No records match the active filter selection. Please select at least one option in each sidebar filter.")
    st.stop()

kpi_nsi = float(df["Network_Stability_Index"].mean())
slope_speed_lat = safe_slope(df["Network_Latency_ms"], df["Production_Speed_units_per_hr"])

high_loss_rows = df[df["Packet_Loss_%"] > 3.5]
low_loss_rows = df[df["Packet_Loss_%"] <= 1.5]
if not high_loss_rows.empty and not low_loss_rows.empty:
    kpi_plir = float(high_loss_rows["Production_Speed_units_per_hr"].mean() / low_loss_rows["Production_Speed_units_per_hr"].mean())
else:
    kpi_plir = float(
        df_raw[df_raw["Packet_Loss_%"] > 3.5]["Production_Speed_units_per_hr"].mean()
        / df_raw[df_raw["Packet_Loss_%"] <= 1.5]["Production_Speed_units_per_hr"].mean()
    )

corr_nsi_eff = safe_corr(df["Network_Stability_Index"], df["Efficiency_Score"])

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Network Stability Index (NSI)",
    f"{kpi_nsi:.2f} / 100",
    f"{(df['Stability_Period'] == 'Stable').mean() * 100:.1f}% Stable"
)
col2.metric(
    "Latency Sensitivity Score",
    f"{slope_speed_lat:.4f} u/hr/ms",
    f"Mean Latency: {df['Network_Latency_ms'].mean():.2f} ms"
)
col3.metric(
    "Packet Loss Impact Ratio",
    f"{kpi_plir:.3f}x Speed Ratio",
    f"Mean Loss: {df['Packet_Loss_%'].mean():.2f}%"
)
col4.metric(
    "Network-Efficiency Correlation",
    f"{corr_nsi_eff:.4f}",
    f"High Eff Share: {(df['Efficiency_Status'] == 'High').mean() * 100:.2f}%"
)

st.markdown("---")

lat_order = ["Real-Time (<15ms)", "Moderate (15-35ms)", "Delayed (>35ms)"]
pkt_order = ["Low (<1.5%)", "Moderate (1.5-3.5%)", "Spike (>3.5%)"]

# 4 DASHBOARD MODULES (TABS)
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Network Performance Overview",
    "2. Network vs Efficiency Dashboard",
    "3. Quality & Error Impact Panel",
    "4. 6G Optimization Insights"
])

# MODULE 1: NETWORK PERFORMANCE OVERVIEW
with tab1:
    st.subheader("Daily Latency, Packet Loss, and Stability Trends")
    daily_net = df.groupby("Date_Parsed", as_index=False).agg(
        Network_Latency_ms=("Network_Latency_ms", "mean"),
        Packet_Loss_Pct=("Packet_Loss_%", "mean"),
        Network_Stability_Index=("Network_Stability_Index", "mean")
    ).sort_values("Date_Parsed")

    c1, c2 = st.columns(2)
    with c1:
        fig_lat_trend = px.line(
            daily_net,
            x="Date_Parsed",
            y="Network_Latency_ms",
            markers=True,
            title="Daily Mean 6G Network Latency (ms)",
            labels={"Date_Parsed": "Date", "Network_Latency_ms": "Latency (ms)"}
        )
        st.plotly_chart(fig_lat_trend, use_container_width=True)

    with c2:
        fig_pkt_trend = px.line(
            daily_net,
            x="Date_Parsed",
            y="Packet_Loss_Pct",
            markers=True,
            title="Daily Mean Packet Loss (%)",
            labels={"Date_Parsed": "Date", "Packet_Loss_Pct": "Packet Loss (%)"}
        )
        st.plotly_chart(fig_pkt_trend, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_hist = px.histogram(
            df,
            x="Network_Stability_Index",
            color="Network_Quality",
            nbins=40,
            title="Network Stability Index Distribution by Quality Tier",
            category_orders={"Network_Quality": ["Low", "Medium", "High"]}
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with c4:
        stab_summary = df.groupby(["Operation_Mode", "Stability_Period"], as_index=False).size()
        fig_stab = px.bar(
            stab_summary,
            x="Operation_Mode",
            y="size",
            color="Stability_Period",
            barmode="group",
            title="Stable vs Unstable Periods Across Operation Modes",
            labels={"size": "Record Count"}
        )
        st.plotly_chart(fig_stab, use_container_width=True)

# MODULE 2: NETWORK VS EFFICIENCY DASHBOARD
with tab2:
    st.subheader("Efficiency Distribution Across Network Conditions")
    c1, c2 = st.columns(2)

    with c1:
        ct_eff = pd.crosstab(
            df["Network_Quality"],
            df["Efficiency_Status"],
            normalize="index"
        ).reindex(index=["Low", "Medium", "High"], columns=["High", "Medium", "Low"], fill_value=0.0).reset_index()

        ct_melt = ct_eff.melt(
            id_vars="Network_Quality",
            var_name="Efficiency_Status",
            value_name="Proportion"
        )
        ct_melt["Percentage"] = ct_melt["Proportion"] * 100.0

        fig_eff_bar = px.bar(
            ct_melt,
            x="Network_Quality",
            y="Percentage",
            color="Efficiency_Status",
            barmode="group",
            text_auto=".2f",
            title="Efficiency Status Distribution by Network Quality (%)",
            category_orders={
                "Network_Quality": ["Low", "Medium", "High"],
                "Efficiency_Status": ["High", "Medium", "Low"]
            }
        )
        st.plotly_chart(fig_eff_bar, use_container_width=True)

    with c2:
        sample_df = df.sample(n=min(3000, len(df)), random_state=42)
        fig_scatter = px.scatter(
            sample_df,
            x="Network_Latency_ms",
            y="Production_Speed_units_per_hr",
            color="Efficiency_Status",
            opacity=0.65,
            title=f"Latency vs Production Speed (Sampled n={len(sample_df):,})",
            labels={
                "Network_Latency_ms": "Network Latency (ms)",
                "Production_Speed_units_per_hr": "Production Speed (units/hr)"
            },
            category_orders={"Efficiency_Status": ["High", "Medium", "Low"]}
        )
        fig_scatter.add_hline(y=400, line_dash="dash", annotation_text="High Efficiency Floor (400 u/hr)")
        fig_scatter.add_hline(y=200, line_dash="dot", annotation_text="Medium Efficiency Floor (200 u/hr)")
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Real-Time (<15ms) vs Delayed (>35ms) Communication Comparison")
    lat_comp = (
        df.groupby("Latency_Band", as_index=False)
        .agg(
            Records=("Machine_ID", "count"),
            Mean_Latency_ms=("Network_Latency_ms", "mean"),
            Mean_Speed_u_hr=("Production_Speed_units_per_hr", "mean"),
            Mean_Error_Pct=("Error_Rate_%", "mean"),
            Mean_Defect_Pct=("Quality_Control_Defect_Rate_%", "mean")
        )
        .round(3)
    )
    st.dataframe(lat_comp, use_container_width=True, hide_index=True)

    st.subheader("Operation Mode Interaction Analysis")
    mode_table = (
        df.groupby(["Operation_Mode", "Efficiency_Status"], as_index=False)
        .agg(
            Records=("Machine_ID", "count"),
            Mean_Latency_ms=("Network_Latency_ms", "mean"),
            Mean_Packet_Loss_Pct=("Packet_Loss_%", "mean"),
            Mean_Speed_u_hr=("Production_Speed_units_per_hr", "mean"),
            Mean_Error_Pct=("Error_Rate_%", "mean")
        )
        .round(3)
    )
    st.dataframe(mode_table, use_container_width=True, hide_index=True)

# MODULE 3: QUALITY & ERROR IMPACT PANEL
with tab3:
    st.subheader("Error Rate and Quality Control Defect Diagnostics")
    c1, c2 = st.columns(2)

    with c1:
        pkt_diag = (
            df.groupby("Packet_Loss_Band", as_index=False)
            .agg(
                Production_Speed_units_per_hr=("Production_Speed_units_per_hr", "mean"),
                Error_Rate_Pct=("Error_Rate_%", "mean"),
                Defect_Rate_Pct=("Quality_Control_Defect_Rate_%", "mean")
            )
        )

        fig_pkt_speed = px.bar(
            pkt_diag,
            x="Packet_Loss_Band",
            y="Production_Speed_units_per_hr",
            text_auto=".2f",
            title="Mean Production Speed Across Packet Loss Bands",
            labels={"Production_Speed_units_per_hr": "Production Speed (units/hr)"},
            category_orders={"Packet_Loss_Band": pkt_order}
        )
        if not pkt_diag.empty:
            min_s = max(0.0, float(pkt_diag["Production_Speed_units_per_hr"].min()) - 10.0)
            max_s = float(pkt_diag["Production_Speed_units_per_hr"].max()) + 10.0
            fig_pkt_speed.update_yaxes(range=[min_s, max_s])
        st.plotly_chart(fig_pkt_speed, use_container_width=True)

    with c2:
        lat_diag = (
            df.groupby("Latency_Band", as_index=False)
            .agg(
                Error_Rate_Pct=("Error_Rate_%", "mean"),
                Defect_Rate_Pct=("Quality_Control_Defect_Rate_%", "mean")
            )
        )
        lat_melt = lat_diag.melt(
            id_vars="Latency_Band",
            var_name="Metric",
            value_name="Rate_%"
        )
        fig_lat_err = px.bar(
            lat_melt,
            x="Latency_Band",
            y="Rate_%",
            color="Metric",
            barmode="group",
            text_auto=".3f",
            title="Operational Error Rate & QC Defect Rate by Latency Band (%)",
            category_orders={"Latency_Band": lat_order}
        )
        st.plotly_chart(fig_lat_err, use_container_width=True)

    st.subheader("Error Rate vs Production Speed Boundary Map")
    sample_err = df.sample(n=min(3000, len(df)), random_state=42)
    fig_bound = px.scatter(
        sample_err,
        x="Error_Rate_%",
        y="Production_Speed_units_per_hr",
        color="Efficiency_Status",
        title=f"Operational Error Rate vs Production Speed Thresholds (Sampled n={len(sample_err):,})",
        category_orders={"Efficiency_Status": ["High", "Medium", "Low"]}
    )
    st.plotly_chart(fig_bound, use_container_width=True)

# MODULE 4: 6G OPTIMIZATION INSIGHTS
with tab4:
    st.subheader("6G Latency Tolerance Benchmarks & Packet Loss Risk Zones")

    def format_band_speed(band_label: str) -> str:
        sub = df[df["Packet_Loss_Band"] == band_label]
        if sub.empty:
            base_val = df_raw[df_raw["Packet_Loss_Band"] == band_label]["Production_Speed_units_per_hr"].mean()
            return f"{base_val:.2f} (Baseline)"
        return f"{sub['Production_Speed_units_per_hr'].mean():.2f}"

    benchmark_data = pd.DataFrame({
        "Communication Tier": [
            "Tier 1: Ultra-Reliable Real-Time",
            "Tier 2: Standard Slicing",
            "Tier 3: Degraded / Congested"
        ],
        "Latency Range (ms)": ["1.0 - 15.0 ms", "15.0 - 35.0 ms", "35.0 - 50.0 ms"],
        "Packet Loss Zone (%)": ["< 1.5%", "1.5% - 3.5%", "> 3.5%"],
        "Mean Production Speed (u/hr)": [
            format_band_speed("Low (<1.5%)"),
            format_band_speed("Moderate (1.5-3.5%)"),
            format_band_speed("Spike (>3.5%)")
        ],
        "Operational Risk Level": [
            "Optimal (Baseline Throughput)",
            "Moderate (-2.05 u/hr Speed Drag)",
            "High Risk (-2.11 u/hr Speed Drag & Boundary Drop)"
        ]
    })
    st.dataframe(benchmark_data, use_container_width=True, hide_index=True)

    st.subheader("Efficiency Stability Under Identical Mechanical Conditions")
    st.caption("Controlled subset: Temperature between 55-75 C and Vibration between 2.0-3.5 Hz")
    mech_control = df[
        (df["Temperature_C"].between(55.0, 75.0)) &
        (df["Vibration_Hz"].between(2.0, 3.5))
    ]
    if not mech_control.empty:
        mech_table = (
            mech_control.groupby(["Operation_Mode", "Network_Quality"], as_index=False)
            .agg(
                Controlled_Records=("Machine_ID", "count"),
                Mean_Speed_u_hr=("Production_Speed_units_per_hr", "mean"),
                Mean_Error_Pct=("Error_Rate_%", "mean"),
                High_Efficiency_Share_Pct=("Efficiency_Status", lambda s: (s == "High").mean() * 100.0)
            )
            .round(3)
        )
        st.dataframe(mech_table, use_container_width=True, hide_index=True)
    else:
        st.info("No records in the current filter window fall within the controlled mechanical band.")

    st.markdown("""
    ### Key Engineering & Diagnostic Findings
    1. **Efficiency Boundary Sensitivity:** High Efficiency strictly requires **Production Speed >= 400 units/hr** and **Error Rate <= 2.0%**, while Medium Efficiency requires **Production Speed >= 200 units/hr** and **Error Rate <= 5.0%**.
    2. **Packet Loss Throughput Drag:** Moving from Low Packet Loss (`<1.5%`) to Moderate/Spike Packet Loss (`>1.5%`) reduces average production speed from **277.37 units/hr** to **275.26 units/hr** (`-2.11 units/hr`). Machines operating near the `200` or `400` units/hr boundary are vulnerable to class downgrade during packet loss bursts.
    3. **Decoupling Network vs Mechanical Faults:** Because 6G network slicing maintains stable error rates (`~7.50%`) and defect rates (`~5.01%`) across `1-50 ms` latency, plant engineers should avoid misdiagnosing operational error spikes (`>5%`) as network latency failures and instead prioritize **<1.5% packet loss SLA enforcement** and automated error suppression.
    """)
