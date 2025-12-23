# E-commerce Sales & Customer Dashboard

An interactive **E-commerce analytics dashboard** built with **Streamlit** to analyze sales performance and customer behavior.
This project focuses on transforming transactional data into **actionable business insights** through time-based sales analysis and **RFM (Recency, Frequency, Monetary) customer segmentation**.

**Live Demo:**
[E-Commerce Analytics Dashboard](https://e-commerce-sales-customer.streamlit.app/)

## Key Features

* **Sales Performance Analysis**
  Analyze monthly trends in order volume and total revenue.

* **Customer Segmentation using RFM**
  Segment customers based on Recency, Frequency, and Monetary value to identify loyal, new, and at-risk customers.

* **Interactive Filters**
  Filter analysis by selected time periods.

* **Optimized for Deployment**
  Uses preprocessed and aggregated data for fast performance and cloud deployment readiness.

## Business Questions Addressed

1. How does e-commerce sales performance change over time in terms of order volume and revenue?
2. What are the characteristics of customers based on RFM analysis, and how can they be grouped into meaningful segments?


## Dashboard Overview

The dashboard consists of two main sections:

### Sales Performance

* Monthly total orders
* Monthly total revenue
* Best and worst performing months based on revenue

### Customer Segmentation (RFM)

* Customer distribution across RFM segments
* Average recency, frequency, and monetary value per segment
* Summary statistics for each customer group

## Tech Stack

* **Python**
* **Pandas**
* **Streamlit**
* **NumPy**
* **Matplotlib / Streamlit Charts**

## Project Structure

```
E-commerce-Sales-Customer/
│
├── dashboard.py          # Streamlit dashboard app
├── preprocessing.py     # Data preprocessing & aggregation
├── requirements.txt     # Project dependencies
├── data/
│   ├── monthly_sales.csv
│   └── rfm.csv
└── README.md
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## Deployment

This application is deployed using **Streamlit Community Cloud** and is publicly accessible:

[E-Commerce Analytics Dashboard](https://e-commerce-sales-customer.streamlit.app/)

## Notes

* The dashboard uses **aggregated and preprocessed data** for efficiency.
* Raw transactional data is excluded to optimize performance and comply with repository size limits.
* RFM segmentation is performed during preprocessing to keep the dashboard lightweight.

## Optional Improvements

Future enhancements may include:

* Additional customer segmentation techniques
* Interactive KPI growth metrics (MoM / YoY)
* Integration with real-time data sources
* Advanced visualizations using Plotly

---
If you find this project useful, feel free to give it a star!
---


