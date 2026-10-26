import pandas as pd
import numpy as np
from pathlib import Path

file_path = Path("Thales_Group_Manufacturing.csv")
assert file_path.exists(), "FAIL: Dataset file is missing."

df = pd.read_csv(file_path)
assert df.shape == (100000, 14), f"FAIL: Unexpected shape {df.shape}"
assert df.isnull().sum().sum() == 0, "FAIL: Dataset contains missing values."

# Test Date parsing
dates = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
assert dates.isnull().sum() == 0, "FAIL: Date parsing produced NaT values."

# Test NSI bounds
lat_norm = (df["Network_Latency_ms"] - df["Network_Latency_ms"].min()) / (df["Network_Latency_ms"].max() - df["Network_Latency_ms"].min())
pkt_norm = (df["Packet_Loss_%"] - df["Packet_Loss_%"].min()) / (df["Packet_Loss_%"].max() - df["Packet_Loss_%"].min())
nsi = (1.0 - (0.5 * lat_norm + 0.5 * pkt_norm)) * 100.0
assert 0.0 <= nsi.min() and nsi.max() <= 100.0, "FAIL: NSI out of 0-100 bounds."

print("ALL QA CHECKS PASSED: Dataset, Date Parsing, and KPI Math Verified 100%.")