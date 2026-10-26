import pandas as pd

df = pd.read_csv("Thales_Group_Manufacturing.csv")

print("--- FULL PRODUCTION SPEED & SENSOR BREAKDOWN BY EFFICIENCY ---")
cols = [
    "Production_Speed_units_per_hr",
    "Error_Rate_%",
    "Quality_Control_Defect_Rate_%",
    "Temperature_C",
    "Vibration_Hz",
    "Power_Consumption_kW",
    "Predictive_Maintenance_Score"
]
print(df.groupby("Efficiency_Status")[cols].agg(["min", "mean", "max"]).round(2))

print("\n--- CORRELATION MATRIX WITH EFFICIENCY & SPEED ---")
eff_map = {"Low": 1, "Medium": 2, "High": 3}
df["Efficiency_Score"] = df["Efficiency_Status"].map(eff_map)
num_cols = cols + ["Network_Latency_ms", "Packet_Loss_%", "Efficiency_Score"]
print(df[num_cols].corr()[["Efficiency_Score", "Production_Speed_units_per_hr", "Error_Rate_%"]].round(4))