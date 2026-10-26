# Impact of 6G Network Performance on Manufacturing Efficiency in Smart Factories

Empirical telemetry analysis, KPI diagnostics, and 6G network slicing optimization built for the [Thales Group Manufacturing](https://projects.unifiedmentor.com/project_instructions?id=14189) smart factory dataset ($n = 100,000$).

---

## Project Overview
This project investigates whether manufacturing slowdowns and quality defects in Industry 4.0/5.0 environments stem from 6G network degradation (latency and packet loss) or underlying mechanical and operational faults. Using a 100,000-record dataset spanning January 2025, we evaluate network performance, calculate four core KPIs, and build an interactive web dashboard using Python and Streamlit.

---

## Repository File Structure
- `Thales_Group_Manufacturing.csv`: Primary dataset containing 100,000 rows and 14 operational/network variables.
- `analysis.py`: Core data science script executing the 5-stage analytical methodology and computing KPIs.
- `deep_down_diagnostic.py`: Diagnostic script uncovering deterministic thresholds governing efficiency classes.
- `app.py`: Production-ready interactive Streamlit web application with sidebar filters, scorecards, and 4 modular tabs.
- `test_app.py`: Automated QA script verifying data integrity, date parsing, and KPI score bounds.
- `requirements.txt`: Python package dependency manifest.
- `README.md`: Project documentation and execution guide.

---

## Key Performance Indicators (KPIs)
1. **Network Stability Index (NSI):** Min-max normalized composite score (0–100) combining latency and packet loss (Factory Mean: `50.01 / 100`).
2. **Latency Sensitivity Score:** Linear regression slope measuring throughput change per 1 ms of latency (`-0.0097 units/hr/ms`).
3. **Packet Loss Impact Ratio:** Throughput and error rate degradation during packet loss spikes (`>3.5%` vs `<1.5%`).
4. **Network-Efficiency Correlation:** Pearson correlation measuring the alignment between network stability and factory efficiency (`r = 0.0004`).

---

## How to Run the Project Locally

### 1. Prerequisites
Ensure Python (version 3.10+) is installed on your system.

### 2. Install Dependencies
Open your terminal inside the project folder and run:
```bash
pip install -r requirements.txt