# dashboard.py
# Dashboard Streamlit untuk Proyek Analisis Data - E-commerce Public Dataset

import pandas as pd
import numpy as np
import streamlit as st

# ------------------------------------------------------
# Fungsi bantu
# ------------------------------------------------------
@st.cache_data
def load_data(path: str = "data_e-commerce.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    # Konversi kolom tanggal
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "shipping_limit_date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def compute_monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    # Agregasi di level order per bulan
    order_month = (
        df.groupby(
            ["order_id", pd.Grouper(key="order_purchase_timestamp", freq="ME")]
        )
        .agg(total_payment=("payment_value", "sum"))
        .reset_index()
    )

    monthly_sales = (
        order_month.groupby("order_purchase_timestamp")
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("total_payment", "sum"),
        )
        .reset_index()
        .sort_values("order_purchase_timestamp")
    )

    return monthly_sales


def compute_rfm(df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    # Data transaksi untuk RFM
    rfm_data = df[
        ["customer_unique_id", "order_purchase_timestamp", "payment_value"]
    ].dropna()

    rfm_data["order_purchase_timestamp"] = pd.to_datetime(
        rfm_data["order_purchase_timestamp"]
    )

    reference_date = rfm_data["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

    rfm = (
        rfm_data.groupby("customer_unique_id")
        .agg(
            last_purchase=("order_purchase_timestamp", "max"),
            frequency=("order_purchase_timestamp", "count"),
            monetary=("payment_value", "sum"),
        )
        .reset_index()
    )

    rfm["recency"] = (reference_date - rfm["last_purchase"]).dt.days

    # Buang monetary <= 0 (jaga-jaga)
    rfm = rfm[rfm["monetary"] > 0]

    # Skor R, F, M (1–4)
    rfm["R_score"] = pd.qcut(
        rfm["recency"],
        4,
        labels=[4, 3, 2, 1],  # recency makin kecil → skor makin besar
    )

    rfm["F_score"] = pd.qcut(
        rfm["frequency"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4],
        duplicates="drop",
    )

    rfm["M_score"] = pd.qcut(
        rfm["monetary"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4],
        duplicates="drop",
    )

    rfm["R_score"] = rfm["R_score"].astype(int)
    rfm["F_score"] = rfm["F_score"].astype(int)
    rfm["M_score"] = rfm["M_score"].astype(int)

    rfm["RFM_score"] = (
        rfm["R_score"].astype(str)
        + rfm["F_score"].astype(str)
        + rfm["M_score"].astype(str)
    )

    # Aturan segmentasi (sama seperti di notebook)
    def segment_rfm(row):
        if row["R_score"] >= 3 and row["F_score"] >= 3 and row["M_score"] >= 3:
            return "Loyal Customer"
        elif row["R_score"] >= 3 and row["F_score"] <= 2:
            return "New Customer"
        elif row["R_score"] <= 2 and row["F_score"] >= 3:
            return "Potential Loyalist"
        elif row["R_score"] <= 2 and row["F_score"] <= 2:
            return "At Risk"
        else:
            return "Others"

    rfm["Segment"] = rfm.apply(segment_rfm, axis=1)

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

    return rfm, segment_summary


# ------------------------------------------------------
# Layout Dashboard
# ------------------------------------------------------
st.set_page_config(
    page_title="E-commerce Sales & Customer Dashboard",
    layout="wide"
)

st.title("📊 E-commerce Sales & Customer Dashboard")
st.markdown(
    """
Dashboard ini dibuat untuk menjawab dua pertanyaan bisnis:

1. **Bagaimana performa penjualan dari waktu ke waktu (jumlah pesanan & total pembayaran)?**  
2. **Bagaimana karakteristik pelanggan berdasarkan analisis RFM (Recency, Frequency, Monetary)?**
"""
)

# Load data
df = load_data()

# ------------------------------------------------------
# Sidebar – filter global
# ------------------------------------------------------
st.sidebar.header("Filter")

# Filter tanggal
min_date = df["order_purchase_timestamp"].min()
max_date = df["order_purchase_timestamp"].max()

date_range = st.sidebar.date_input(
    "Rentang tanggal order",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    # fallback kalau user cuma pilih satu tanggal
    start_date, end_date = min_date, max_date

mask_date = (df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & (
    df["order_purchase_timestamp"] <= pd.to_datetime(end_date)
)
df_filtered = df[mask_date].copy()

st.sidebar.write(f"Jumlah baris setelah filter tanggal: **{len(df_filtered):,}**")

# ------------------------------------------------------
# Tabs untuk tiap pertanyaan
# ------------------------------------------------------
tab1, tab2 = st.tabs(
    ["📈 Performa Penjualan (Pertanyaan 1)", "🧩 Segmentasi Pelanggan RFM (Pertanyaan 2)"]
)

# ------------------------------------------------------
# Tab 1 – Performa Penjualan
# ------------------------------------------------------
with tab1:
    st.subheader("Performa Penjualan per Bulan")

    monthly_sales = compute_monthly_sales(df_filtered)

    # KPI singkat
    total_orders = int(monthly_sales["total_orders"].sum())
    total_revenue = float(monthly_sales["total_revenue"].sum())

    col1, col2 = st.columns(2)
    col1.metric("Total Orders (periode terpilih)", f"{total_orders:,}")
    col2.metric("Total Revenue (periode terpilih)", f"{total_revenue:,.2f}")

    # Line chart orders
    st.markdown("#### Tren Jumlah Pesanan per Bulan")
    chart_orders = monthly_sales.set_index("order_purchase_timestamp")[
        ["total_orders"]
    ]
    st.line_chart(chart_orders)

    # Line chart revenue
    st.markdown("#### Tren Total Revenue per Bulan")
    chart_revenue = monthly_sales.set_index("order_purchase_timestamp")[
        ["total_revenue"]
    ]
    st.line_chart(chart_revenue)

    # Bulan terbaik & terburuk
    if not monthly_sales.empty:
        best_month = monthly_sales.loc[monthly_sales["total_revenue"].idxmax()]
        worst_month = monthly_sales.loc[monthly_sales["total_revenue"].idxmin()]

        st.markdown("#### Ringkasan Bulan Terbaik & Terburuk (berdasarkan Revenue)")
        col3, col4 = st.columns(2)

        col3.write("**Bulan dengan revenue tertinggi**")
        col3.write(
            f"- Bulan: `{best_month['order_purchase_timestamp'].strftime('%Y-%m')}`  \n"
            f"- Orders: **{int(best_month['total_orders']):,}**  \n"
            f"- Revenue: **{best_month['total_revenue']:,.2f}**"
        )

        col4.write("**Bulan dengan revenue terendah**")
        col4.write(
            f"- Bulan: `{worst_month['order_purchase_timestamp'].strftime('%Y-%m')}`  \n"
            f"- Orders: **{int(worst_month['total_orders']):,}**  \n"
            f"- Revenue: **{worst_month['total_revenue']:,.2f}**"
        )

    st.markdown("##### Data agregasi bulanan")
    st.dataframe(monthly_sales)

# ------------------------------------------------------
# Tab 2 – Segmentasi Pelanggan RFM
# ------------------------------------------------------
with tab2:
    st.subheader("Analisis RFM (Recency, Frequency, Monetary)")

    rfm, segment_summary = compute_rfm(df_filtered)

    # Filter segmen di sidebar tab
    all_segments = list(segment_summary["Segment"].unique())
    selected_segments = st.multiselect(
        "Pilih segmen pelanggan yang ingin ditampilkan",
        options=all_segments,
        default=all_segments,
    )

    seg_summary_filtered = segment_summary[
        segment_summary["Segment"].isin(selected_segments)
    ]

    # KPI kecil: jumlah customer unik
    total_customers = int(rfm["customer_unique_id"].nunique())
    st.metric("Total pelanggan unik (periode terpilih)", f"{total_customers:,}")

    # Chart jumlah pelanggan per segmen
    st.markdown("#### Jumlah Pelanggan per Segmen RFM")
    seg_counts = seg_summary_filtered.set_index("Segment")["customers"]
    st.bar_chart(seg_counts)

    # Chart rata-rata monetari per segmen
    st.markdown("#### Rata-rata Nilai Pembelian per Segmen")
    seg_monetary = seg_summary_filtered.set_index("Segment")["avg_monetary"]
    st.bar_chart(seg_monetary)

    # Tabel ringkasan
    st.markdown("#### Ringkasan Statistik RFM per Segmen")
    st.dataframe(seg_summary_filtered)

    # Tabel sampel pelanggan
    st.markdown("#### Contoh Data RFM (5 baris pertama)")
    st.dataframe(rfm.head())

    st.markdown(
        """
**Interpretasi singkat:**

- **Loyal Customer** → frekuensi tinggi, pembelian besar, dan relatif baru bertransaksi.  
- **New Customer** → pelanggan baru dengan transaksi terkini namun frekuensi masih rendah.  
- **Potential Loyalist** → frekuensi mulai meningkat, berpotensi menjadi pelanggan loyal bila dijaga.  
- **At Risk** → sudah lama tidak bertransaksi dan frekuensi rendah, berisiko hilang.  
- **Others** → pelanggan dengan pola pembelian yang tidak terlalu menonjol.
"""
    )
