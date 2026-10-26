import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("Thales_Group_Manufacturing.csv")

print("--- DATASET SUMMARY ---")
print(f"Shape: {df.shape}")
print(f"Date Range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Missing Values: {df.isnull().sum().sum()}\n")

# Step 1: Network Performance Profiling
lat_min, lat_max = df["Network_Latency_ms"].min(), df["Network_Latency_ms"].max()
pkt_min, pkt_max = df["Packet_Loss_%"].min(), df["Packet_Loss_%"].max()

lat_norm = (df["Network_Latency_ms"] - lat_min) / (lat_max - lat_min)
pkt_norm = (df["Packet_Loss_%"] - pkt_min) / (pkt_max - pkt_min)

df["Network_Stability_Index"] = (1 - (0.5 * lat_norm + 0.5 * pkt_norm)) * 100
df["Network_Quality"] = pd.qcut(df["Network_Stability_Index"], q=3, labels=["Low", "Medium", "High"])
df["Stability_Period"] = np.where(df["Network_Stability_Index"] >= 50, "Stable", "Unstable")

print("--- STEP 1: NETWORK PROFILING ---")
print(df[["Network_Latency_ms", "Packet_Loss_%", "Network_Stability_Index"]].describe().round(3))
print("\nStability Period Counts:")
print(df["Stability_Period"].value_counts(), "\n")

# Step 2: Network vs Efficiency Analysis
print("--- STEP 2: NETWORK VS EFFICIENCY ---")
print(df.groupby("Efficiency_Status")[
    ["Network_Latency_ms", "Packet_Loss_%", "Production_Speed_units_per_hr", "Error_Rate_%", "Quality_Control_Defect_Rate_%"]
].mean().round(3))

print("\nEfficiency Distribution by Network Quality (%):")
quality_eff_table = pd.crosstab(df["Network_Quality"], df["Efficiency_Status"], normalize="index") * 100
print(quality_eff_table.round(2), "\n")

# Step 3 & 4: Latency and Packet Loss Diagnostics
df["Latency_Band"] = pd.cut(
    df["Network_Latency_ms"],
    bins=[0, 15, 35, 100],
    labels=["Real-Time (<15ms)", "Moderate (15-35ms)", "Delayed (>35ms)"]
)
df["Packet_Loss_Band"] = pd.cut(
    df["Packet_Loss_%"],
    bins=[-0.1, 1.5, 3.5, 100],
    labels=["Low (<1.5%)", "Moderate (1.5-3.5%)", "Spike (>3.5%)"]
)

print("--- STEP 3: LATENCY DIAGNOSTICS ---")
print(df.groupby("Latency_Band", observed=False)[
    ["Production_Speed_units_per_hr", "Error_Rate_%", "Quality_Control_Defect_Rate_%"]
].mean().round(3), "\n")

print("--- STEP 4: PACKET LOSS DIAGNOSTICS ---")
print(df.groupby("Packet_Loss_Band", observed=False)[
    ["Production_Speed_units_per_hr", "Error_Rate_%", "Quality_Control_Defect_Rate_%"]
].mean().round(3), "\n")

# Step 5: Operation Mode Interaction Analysis
print("--- STEP 5: OPERATION MODE ANALYSIS ---")
print(df.groupby("Operation_Mode")[
    ["Network_Latency_ms", "Packet_Loss_%", "Production_Speed_units_per_hr", "Error_Rate_%"]
].mean().round(3), "\n")

# KPI Calculations
eff_map = {"Low": 1, "Medium": 2, "High": 3}
df["Efficiency_Score"] = df["Efficiency_Status"].map(eff_map)

kpi_nsi = df["Network_Stability_Index"].mean()
slope_speed_lat = np.polyfit(df["Network_Latency_ms"], df["Production_Speed_units_per_hr"], 1)[0]
slope_err_lat = np.polyfit(df["Network_Latency_ms"], df["Error_Rate_%"], 1)[0]

high_loss_err = df[df["Packet_Loss_%"] > 3.5]["Error_Rate_%"].mean()
low_loss_err = df[df["Packet_Loss_%"] <= 1.5]["Error_Rate_%"].mean()
kpi_plir = high_loss_err / low_loss_err if low_loss_err != 0 else np.nan

corr_nsi_eff = df["Network_Stability_Index"].corr(df["Efficiency_Score"])
corr_lat_eff = df["Network_Latency_ms"].corr(df["Efficiency_Score"])
corr_pkt_eff = df["Packet_Loss_%"].corr(df["Efficiency_Score"])

print("--- KEY PERFORMANCE INDICATORS ---")
print(f"Network Stability Index (Mean): {kpi_nsi:.2f}")
print(f"Latency Sensitivity Score (Speed/ms): {slope_speed_lat:.4f}")
print(f"Latency Sensitivity Score (Error/ms): {slope_err_lat:.4f}")
print(f"Packet Loss Impact Ratio: {kpi_plir:.3f}")
print(f"Correlation (NSI vs Efficiency): {corr_nsi_eff:.4f}")
print(f"Correlation (Latency vs Efficiency): {corr_lat_eff:.4f}")
print(f"Correlation (Packet Loss vs Efficiency): {corr_pkt_eff:.4f}")