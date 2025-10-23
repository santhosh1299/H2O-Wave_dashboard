# Executive Intelligence Dashboard — Churn Management for AMEX

**Built with H2O Wave, H2O-3 & H2O-GPT.E**  
A smart, AI-powered dashboard delivering real-time churn insights and action plans for business leaders.

![Dashboard Preview](https://github.com/user-attachments/assets/0eaf8cf5-8644-413d-9d8c-80ca43bd7276)

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

## Data & Model

The dashboard is powered by a comprehensive dataset of customer information including:

- **Demographics**: Age, gender, education, marital status, income
- **Account Details**: Card category, months on book, credit limit
- **Transaction Behavior**: Revolving balance, transaction amounts and counts
- **Derived Features**: Utilization ratios, inactivity levels, relationship duration

The H2O-3 AutoML model predicts customer churn probability based on these features, with results displayed in real-time on the dashboard.

---

## Technical Implementation

### Tech Stack

- [H2O Wave](https://wave.h2o.ai/) – Real-time dashboard frontend  
- [H2O-3](https://docs.h2o.ai/h2o/latest-stable/h2o-docs/automl.html) – AutoML for churn prediction  
- [H2O GPT-E](https://h2o.ai/platform/enterprise-gpt/) – For AI insights  
- Python, Pandas, and more

### Project Structure

- `app.py` - Main Wave application with dashboard UI and logic
- `H2O3_Churn_Model_FIXED.ipynb` - Jupyter notebook with model development
- `data/dashboard.csv` - Dataset with customer information and churn predictions

---

## Getting Started

### Prerequisites

- Python 3.8+
- H2O Wave
- H2O-3
- H2O GPT-E API access

### Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables for H2O GPT-E API
4. Run the Wave app: `wave run app.py`

---

## Dashboard Sections

### 1. Executive Summary
High-level KPIs and churn metrics with AI-generated insights.

### 2. Customer Segments
Breakdown of churn risk by customer segments and attributes.

### 3. Action Recommendations
AI-generated recommendations for reducing churn across departments.

### 4. Trend Analysis
Historical patterns and projected churn rates.

---

## Future Enhancements

- Integration with real-time transaction data streams
- Expanded AI-driven scenario planning
- Mobile executive alerts for high-risk customer segments
- Automated intervention workflow triggers

---

## Contact

For questions or support, please contact the H2O.ai team.
