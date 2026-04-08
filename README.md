# Operational Bottleneck Analysis: Global Supply Chain Audit
> **An End-to-End Case Study in Logistics Integrity & Fulfillment Recovery**

[View Notebook](supply-chain-audit.ipynb) | [SQL Queries](SQL Queries.txt) | [Data Source](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)

---

## Executive Summary
Premium shipping tiers exhibit a ~95% SLA breach rate, driven by a consistent ~2-day fulfillment delay. This analysis demonstrates that by aligning delivery expectations with actual logistics velocity via a Dynamic Delivery Estimate (DDE), the company can restore fulfillment success to 100% without increasing operational overhead.

---

## Project Overview
This project is an end-to-end data audit of a global supply chain dataset (180,000+ records). The objective was to investigate systemic failures in delivery performance and design a data-driven recovery strategy grounded in realistic operational constraints.

> **Note:** Failure rate is defined as deliveries exceeding the promised shipping duration (late_delivery_risk flag).

---

## Core Findings
| Shipping Tier | Promised Days | Actual Days | Latency Gap | SLA Success |
| :--- | :---: | :---: | :---: | :---: |
| **First Class** | 1 | 3.01 | **+2.01 Days Late** | 4.7% |
| **Second Class** | 2 | 3.12 | **+1.12 Days Late** | 24.2% |
| **Standard Class**| 4 | 3.85 | **-0.15 Days (Early)** | 98.2% |

---

## Business Impact
* **Revenue Protection:** Isolated systemic SLA failures impacting High-LTV (Platinum) customer segments.
* **Customer Experience Risk:** Confirmed that uniform delay rates across all tiers increase churn risk for high-priority users.
* **Low-Cost Solution:** Modeled a simulation-based recovery that aligns checkout promises with logistics reality.
* **Technical Scale:** Processed and validated 180k+ records, resolving encoding inconsistencies (ISO-8859-1).

---

## Data Validation (DVL)
Before analysis, a Data Validation Layer was implemented to ensure mathematical soundness:
* **Null Handling:** Removed records missing critical SLA fields (shipping days, customer ID).
* **Deduplication:** Verified uniqueness of 180,000+ order IDs.
* **Financial Filtering:** Excluded invalid transactions (order value ≤ $0).
* **Anomaly Detection:** Outlier removal for extreme logistics timestamps to prevent skewed averages.

---

## Toolset & Application
* **Python (Pandas, NumPy):** Used for vectorized data cleaning, preprocessing, and rule-based simulation.
* **SQL (SQLite):** Leveraged CTEs (Common Table Expressions) and complex joins for multi-tier customer segmentation.
* **Analytical Framework:** Quantified "Time Leakage" within the fulfillment funnel to identify the 2.01-day bottleneck.

---

## The 5-Stage Analytical Framework

### Stage 1: Data Integrity Audit
Handled international encoding (ISO-8859-1) and performed a cleanliness check to ensure SLA metrics were computed on reliable data.

### Stage 2: SLA Performance (The Promise Test)
Benchmarked success using Strict Success (on-time) vs. Buffered Success (1-day grace period). Findings showed that even with buffering, premium tiers failed significantly.

### Stage 3: Fulfillment Funnel (The Latency Gap)
Modeled delivery as a funnel to quantify delay:
* **Definition:** Latency Gap = Actual Days − Promised Days.
* **Insight:** A consistent ~2.01-day delay suggested a systemic bottleneck rather than random variation.

### Stage 4: Customer Segmentation (Value at Risk)
Linked failures to customer spending tiers using SQL. 
* **Result:** High-value customers experienced the same 95% delay rate as standard users, identifying a major churn risk.

### Stage 5: A/B Test Simulation (Success Recovery)
Modeled a rule-based simulation comparing:
* **Control:** 1-day promise.
* **Variant:** 4-day realistic estimate (Dynamic Delivery Estimate).
* **Result:** Fulfillment success recovered from ~5% to 100% by managing expectations.

---

## Key Recommendations

### Short-Term (Customer Experience)
* Update checkout UI to reflect realistic delivery windows (e.g., 4-day estimate).
* Align customer expectations with actual fulfillment capabilities immediately to halt churn.

### Operational (Logistics Optimization)
* Investigate Standard Class routes showing negative latency (arriving early) for potential resource reallocation to premium lanes.

---

## Limitations
* Analysis is based on a historical dataset, not real-time streaming data.
* The A/B test is a rule-based simulation, serving as a theoretical upper bound for recovery.

---

## How to Run
```bash
# 1. Clone the repository
git clone [https://github.com/your-username/Supply-Chain-Audit.git](https://github.com/your-username/Supply-Chain-Audit.git)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the audit
jupyter notebook
