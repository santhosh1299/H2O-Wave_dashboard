# Executive Intelligence Dashboard — Churn Management for AMEX

**Built with H2O Wave, H2O-3 & H2O-GPT.E**  
A smart, AI-powered dashboard delivering real-time churn insights and action plans for business leaders.

![Dashboard Preview](https://raw.githubusercontent.com/santhosh1299/H2O-Wave_dashboard/main/Dashboard.png)

## AI-generated report based on the Dashboard

![AI Report](https://github.com/user-attachments/assets/ed173ac8-f912-472c-b2b6-7dcf542cc533)

---

## Overview

The **Executive Intelligence Dashboard** is designed for senior decision-makers at American Express to:
- Monitor **customer churn risk** in real-time
- Identify **behavioral patterns** driving attrition
- Generate **actionable insights** using AI for engagement, marketing, and risk management

This system combines the power of H2O-3 machine learning models with H2OGPTe-driven executive summarization for intelligent, contextual decision support.

---

## Key Features

- **Single-Page Executive Dashboard**  
  Streamlined layout showing only the most critical churn KPIs and visualizations.

- **AI-Generated Action Plans**  
  H2O-GPTE interprets churn patterns and provides department-specific interventions.

- **Segmented Risk Analytics**  
  View churn distribution by tenure, transaction activity, card category, and more.

- **Market-Aware Insights**  
  External factors like economic shifts and regulatory events are embedded into recommendations.

---

## Technical Implementation

### Data Pipeline

1. **Data Source**: Customer transaction and demographic data from AMEX systems
2. **Preprocessing**: Handled in the H2O3_Churn_Model_FIXED.ipynb notebook
3. **Model Training**: H2O-3 AutoML for churn prediction
4. **Dashboard Integration**: Processed data served through H2O Wave

### Dashboard Components

- **KPI Cards**: Real-time metrics showing churn rate, retention cost, and at-risk revenue
- **Segmentation Charts**: Interactive visualizations of customer segments and risk factors
- **AI Insight Panel**: H2OGPTe-powered analysis and recommendations
- **Executive Report**: One-click generation of comprehensive churn analysis

---

## Tech Stack

- [H2O Wave](https://wave.h2o.ai/) – Real-time dashboard frontend  
- [H2O-3](https://docs.h2o.ai/h2o/latest-stable/h2o-docs/automl.html) – AutoML for churn prediction  
- [H2O GPT-E](https://h2o.ai/platform/enterprise-gpt/) – For AI insights  
- Python, Pandas, and more

---

## Getting Started

### Prerequisites

- Python 3.8+
- H2O Wave
- H2O-3
- H2OGPTe API access

### Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `wave run app.py`

---

## How to Use

1. **Dashboard View**: The main interface displays key metrics and visualizations
2. **Generate Report**: Click the "Generate Report" button for AI-powered analysis
3. **Export Insights**: Download the full report for offline review

---

## Future Enhancements

- Real-time API integration with AMEX customer database
- Expanded segmentation options for deeper customer analysis
- Mobile-optimized view for executives on the go
- Integration with intervention tracking systems
