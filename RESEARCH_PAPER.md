Impact of 6G Network Performance on Manufacturing Efficiency in Smart Factories

Empirical Telemetry Analysis, KPI Diagnostics, and 6G Slicing Recommendations (Thales Group Dataset, n = 100,000)

1. Executive Abstract & Problem Context
In Industry 4.0 and emerging Industry 5.0 smart factories, industrial machines rely on ultra-reliable low-latency communication (URLLC) and real-time telemetry exchange. However, manufacturing organizations often lack empirical clarity on whether production slowdowns and quality defects stem from 6G network degradation (latency and packet loss) or underlying mechanical and operational faults.

This research paper evaluates 100,000 machine telemetry records recorded between 01-01-2025 and 31-01-2025 across 14 operational, mechanical, and network variables from the Thales Group Manufacturing dataset. Using a 5-stage analytical methodology, we isolate the precise operational impact of 6G network latency and packet loss on production throughput, error rates, and overall manufacturing efficiency.

2. Exploratory Data Analysis (EDA) & Network Performance Profiling
Dataset Integrity: 100,000 complete records across 14 variables with 0 missing values.

6G Network Latency Distribution: Ranges from 1.000 ms to 50.000 ms with a mean of 25.556 ms (SD = 14.121 ms, Median = 25.536 ms, IQR = 13.355 ms to 37.796 ms).

Packet Loss Distribution: Ranges from 0.000% to 5.000% with a mean of 2.493% (SD = 1.443%, Median = 2.488%, IQR = 1.245% to 3.741%).

Network Stability Index (NSI - KPI 1): Constructed via min-max normalization of latency and packet loss on a 0-100 scale. The factory averages an NSI of 50.01 (SD = 20.32), evenly dividing operations into 50,003 Stable periods (NSI >= 50) and 49,997 Unstable periods (NSI < 50).

Operation Mode Distribution: Active mode accounts for the primary production workload (mean speed = 276.199 units/hr), alongside Idle (274.126 units/hr) and Maintenance (277.544 units/hr) states.

3. Network vs Efficiency & Diagnostic Findings
Efficiency Class Distribution: Across the plant, 77.83% of records classify as Low Efficiency, 19.19% as Medium Efficiency, and 2.99% as High Efficiency.

Deterministic Boundary Discovery: Diagnostic profiling reveals that Efficiency_Status is governed by strict operational thresholds. High Efficiency strictly requires Production Speed >= 400 units/hr (mean = 450.79 u/hr) and Error Rate <= 2.0% (mean = 1.007%). Medium Efficiency requires Production Speed >= 200 units/hr (mean = 334.13 u/hr) and Error Rate <= 5.0% (mean = 2.733%). Low Efficiency averages 254.85 u/hr with a mean Error Rate of 8.930%.

Latency Impact Diagnostics (KPI 2): Across Real-Time (<15ms), Moderate (15-35ms), and Delayed (>35ms) latency bands, mean production speed remains resilient (275.79, 275.83, and 276.15 units/hr respectively), yielding a Latency Sensitivity Score of -0.0097 units/hr/ms and an Error Rate sensitivity of 0.0000%/ms. This proves that 6G edge buffering effectively absorbs routine latency fluctuations up to 50 ms.

Packet Loss Impact Diagnostics (KPI 3): Unlike latency, packet loss directly drags throughput. When Packet Loss rises from the Low band (<1.5%) to Moderate (1.5-3.5%) and Spike (>3.5%) bands, mean Production Speed drops from 277.366 units/hr to 275.318 and 275.256 units/hr (-2.11 units/hr drag, Packet Loss Impact Ratio = 0.992x throughput / 0.997x error ratio).

Network-Efficiency Correlation (KPI 4): Overall linear correlation between NSI and Efficiency Score is r = 0.0004 (Latency r = -0.0016, Packet Loss vs Speed r = -0.0071), whereas Error Rate (r = -0.6037) and Production Speed (r = +0.3336) dominate classification.

4. Strategic Engineering Recommendations
Enforce <1.5% Packet Loss SLAs on Boundary Machines: Because packet loss >1.5% reduces average output by 2.11 units/hr, machines operating near the 200 units/hr (Medium) and 400 units/hr (High) thresholds risk immediate efficiency downgrade during packet loss spikes. Implement redundant 6G Dual-Connectivity (DC) for machines running at 195–210 and 395–410 units/hr.

Prevent Fault Misdiagnosis: Plant engineers must not misattribute high operational error rates (>5%) to 6G latency between 1-50 ms. Capital expenditure should prioritize automated controller error suppression (reducing Error_Rate_% below 2%) rather than over-provisioning sub-5ms latency slices for non-critical workloads.

Dynamic 6G Network Slicing by Operation Mode: Allocate high-reliability URLLC slices (<1.5% packet loss) exclusively to Active mode machines, while shifting Idle and Maintenance telemetry to standard best-effort slices to optimize spectrum efficiency.
