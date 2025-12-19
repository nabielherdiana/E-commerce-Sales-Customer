# ======================================================
# E-commerce Sales & Customer Dashboard
# Data Source: Preprocessed CSV (monthly_sales & RFM)
# ======================================================

import pandas as pd
import streamlit as st

# ------------------------------------------------------
# Page config
# ------------------------------------------------------
st.set_page_config(
    page_title="E-commerce Sales & Customer Dashboard",
    layout="wide"
)

# ------------------------------------------------------
# Load data (LIGHT & DEPLOYABLE)
# ------------------------------------------------------
@st.cache_data
def load_monthly_sales():
    return pd.read_csv(
        "data/monthly_sales.csv",
        parse_dates=["order_purchase_timestamp"]
    )

@st.cache_data
def load_rfm():
    return pd.read_csv("data/rfm.csv")

monthly_sales = load_monthly_sales()
rfm = load_rfm()

# ------------------------------------------------------
# Title & Description
# ------------------------------------------------------
st.title("📊 E-commerce Sales & Customer Dashboard")
st.markdown(
    """
This dashboard addresses two key business questions:

1. **How does sales performance evolve over time (order volume & total revenue)?**  
2. **What are the characteristics of customers based on RFM analysis (Recency, Frequency, Monetary)?**
"""
)

# ------------------------------------------------------
# Sidebar – Global Filter
# ------------------------------------------------------
st.sidebar.header("📅 Filter")

min_date = monthly_sales["order_purchase_timestamp"].min()
max_date = monthly_sales["order_purchase_timestamp"].max()

date_range = st.sidebar.date_input(
    "Select period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

start_date, end_date = date_range

monthly_filtered = monthly_sales[
    (monthly_sales["order_purchase_timestamp"] >= pd.to_datetime(start_date)) &
    (monthly_sales["order_purchase_timestamp"] <= pd.to_datetime(end_date))
]

st.sidebar.write(
    f"📌 Records selected: **{len(monthly_filtered):,} months**"
)

# ------------------------------------------------------
# Tabs
# ------------------------------------------------------
tab1, tab2 = st.tabs(
    ["📈 Sales Performance", "🧩 Customer Segmentation (RFM)"]
)

# ======================================================
# TAB 1 — SALES PERFORMANCE
# ======================================================
with tab1:
    st.subheader("📈 Monthly Sales Performance")

    total_orders = int(monthly_filtered["total_orders"].sum())
    total_revenue = float(monthly_filtered["total_revenue"].sum())

    col1, col2 = st.columns(2)
    col1.metric("Total Orders", f"{total_orders:,}")
    col2.metric("Total Revenue", f"{total_revenue:,.2f}")

    st.markdown("### 📊 Order Volume Trend")
    st.line_chart(
        monthly_filtered.set_index("order_purchase_timestamp")[["total_orders"]]
    )

    st.markdown("### 💰 Revenue Trend")
    st.line_chart(
        monthly_filtered.set_index("order_purchase_timestamp")[["total_revenue"]]
    )

    if not monthly_filtered.empty:
        best_month = monthly_filtered.loc[
            monthly_filtered["total_revenue"].idxmax()
        ]
        worst_month = monthly_filtered.loc[
            monthly_filtered["total_revenue"].idxmin()
        ]

        st.markdown("### 🏆 Best & Worst Month (Revenue-Based)")
        col3, col4 = st.columns(2)

        col3.write("**Best Month**")
        col3.write(
            f"- Period: `{best_month['order_purchase_timestamp'].strftime('%Y-%m')}`  \n"
            f"- Orders: **{int(best_month['total_orders']):,}**  \n"
            f"- Revenue: **{best_month['total_revenue']:,.2f}**"
        )

        col4.write("**Worst Month**")
        col4.write(
            f"- Period: `{worst_month['order_purchase_timestamp'].strftime('%Y-%m')}`  \n"
            f"- Orders: **{int(worst_month['total_orders']):,}**  \n"
            f"- Revenue: **{worst_month['total_revenue']:,.2f}**"
        )

    st.markdown("### 📋 Monthly Aggregated Data")
    st.dataframe(monthly_filtered, use_container_width=True)

# ======================================================
# TAB 2 — RFM SEGMENTATION
# ======================================================
with tab2:
    st.subheader("🧩 Customer Segmentation using RFM")

    segment_summary = (
        rfm.groupby("Segment")
        .agg(
            customers=("customer_unique_id", "nunique"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
        )
        .reset_index()
        .sort_values("customers", ascending=False)
    )

    all_segments = segment_summary["Segment"].tolist()
    selected_segments = st.multiselect(
        "Select customer segments",
        options=all_segments,
        default=all_segments,
    )

    seg_filtered = segment_summary[
        segment_summary["Segment"].isin(selected_segments)
    ]

    total_customers = int(rfm["customer_unique_id"].nunique())
    st.metric("Total Unique Customers", f"{total_customers:,}")

    st.markdown("### 👥 Number of Customers per Segment")
    st.bar_chart(
        seg_filtered.set_index("Segment")["customers"]
    )

    st.markdown("### 💵 Average Monetary Value per Segment")
    st.bar_chart(
        seg_filtered.set_index("Segment")["avg_monetary"]
    )

    st.markdown("### 📊 RFM Statistics Summary")
    st.dataframe(seg_filtered, use_container_width=True)

    st.markdown("### 🔍 Sample RFM Data")
    st.dataframe(rfm.head(), use_container_width=True)

    st.markdown(
        """
**Interpretation Guide:**

- **Loyal Customer** → High purchase frequency, high spending, and recent activity.  
- **New Customer** → Recently acquired customers with limited transaction history.  
- **Potential Loyalist** → Growing frequency, strong potential to become loyal customers.  
- **At Risk** → Long inactivity period with low engagement.  
- **Others** → Customers with moderate or mixed purchasing behavior.
"""
    )