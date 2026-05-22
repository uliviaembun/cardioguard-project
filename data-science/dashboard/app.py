import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


# Mengubah working directory ke folder dashboard agar path dataset
APP_DIR = Path(__file__).resolve().parent
os.chdir(APP_DIR)

# Konfigurasi awal halaman Streamlit.
st.set_page_config(
    page_title="Dashboard Analisis Penyakit Kardiovaskular",
    layout="wide",
)

# Tema visual sederhana 
sns.set_theme(style="whitegrid")
PALETTE = {
    "primary": "#4C78A8",
    "secondary": "#F58518",
    "accent": "#54A24B",
    "muted": "#8F9AA7",
    "background": "#F6F8FB",
}
CARDIO_LABELS = {0: "Tidak Berisiko", 1: "Berisiko Cardio"}
GENDER_LABELS = {1: "Perempuan", 2: "Laki-laki"}
CHOLESTEROL_LABELS = {
    1: "Normal",
    2: "Di Atas Normal",
    3: "Jauh Di Atas Normal",
}
CARDIO_COLORS = {
    CARDIO_LABELS[0]: PALETTE["primary"],
    CARDIO_LABELS[1]: PALETTE["secondary"],
}

try:
    cache_data = st.cache_data
except AttributeError:
    cache_data = st.cache


@cache_data
def load_data():
    """Membaca dataset dan menyimpan hasilnya di cache agar dashboard lebih cepat."""
    df = pd.read_csv("../../data/processed/cardio_cleaned.csv")
    return df


def prepare_data(dataframe):
    """Menambahkan label yang lebih mudah dibaca untuk pemula."""
    df = dataframe.copy()
    df["gender_label"] = df["gender"].map(GENDER_LABELS).fillna("Tidak Diketahui")
    df["cholesterol_label"] = (
        df["cholesterol"].map(CHOLESTEROL_LABELS).fillna("Tidak Diketahui")
    )
    df["cardio_label"] = df["cardio"].map(CARDIO_LABELS).fillna("Tidak Diketahui")
    return df


def format_number(value):
    """Format angka agar lebih rapi saat ditampilkan sebagai metrik."""
    return f"{value:,.0f}".replace(",", ".")


def plot_status_distribution(dataframe):
    """Bar chart untuk melihat proporsi status cardio."""
    status_order = [CARDIO_LABELS[0], CARDIO_LABELS[1]]
    status_counts = (
        dataframe["cardio_label"].value_counts().reindex(status_order, fill_value=0)
    )
    status_df = status_counts.rename_axis("cardio_label").reset_index(name="count")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.barplot(
        data=status_df,
        x="cardio_label",
        y="count",
        hue="cardio_label",
        dodge=False,
        palette=CARDIO_COLORS,
        ax=ax,
    )
    if ax.get_legend() is not None:
        ax.get_legend().remove()
    ax.set_title("Distribusi Status Cardio", fontsize=13, weight="bold")
    ax.set_xlabel("Status Cardio")
    ax.set_ylabel("Jumlah Pasien")
    ax.tick_params(axis="x", rotation=8)
    plt.tight_layout()
    return fig, status_counts


def plot_age_distribution(dataframe):
    """Histogram umur dengan warna berbeda untuk tiap status cardio."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.histplot(
        data=dataframe,
        x="age_years",
        hue="cardio_label",
        hue_order=[CARDIO_LABELS[0], CARDIO_LABELS[1]],
        bins=15,
        multiple="stack",
        palette=CARDIO_COLORS,
        edgecolor="white",
        ax=ax,
    )
    ax.set_title("Distribusi Umur Berdasarkan Status Cardio", fontsize=13, weight="bold")
    ax.set_xlabel("Umur (tahun)")
    ax.set_ylabel("Jumlah Pasien")
    plt.tight_layout()
    return fig


def plot_bmi_comparison(dataframe):
    """Boxplot untuk membandingkan BMI antar status cardio."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.boxplot(
        data=dataframe,
        x="cardio_label",
        y="bmi",
        hue="cardio_label",
        order=[CARDIO_LABELS[0], CARDIO_LABELS[1]],
        hue_order=[CARDIO_LABELS[0], CARDIO_LABELS[1]],
        dodge=False,
        palette=CARDIO_COLORS,
        ax=ax,
    )
    if ax.get_legend() is not None:
        ax.get_legend().remove()
    ax.set_title("Perbandingan BMI terhadap Status Cardio", fontsize=13, weight="bold")
    ax.set_xlabel("Status Cardio")
    ax.set_ylabel("BMI")
    ax.tick_params(axis="x", rotation=8)
    plt.tight_layout()
    return fig


def plot_systolic_comparison(dataframe):
    """Boxplot untuk membandingkan tekanan darah sistolik antar status cardio."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.boxplot(
        data=dataframe,
        x="cardio_label",
        y="ap_hi",
        hue="cardio_label",
        order=[CARDIO_LABELS[0], CARDIO_LABELS[1]],
        hue_order=[CARDIO_LABELS[0], CARDIO_LABELS[1]],
        dodge=False,
        palette=CARDIO_COLORS,
        ax=ax,
    )
    if ax.get_legend() is not None:
        ax.get_legend().remove()
    ax.set_title(
        "Perbandingan Tekanan Darah Sistolik terhadap Status Cardio",
        fontsize=13,
        weight="bold",
    )
    ax.set_xlabel("Status Cardio")
    ax.set_ylabel("Tekanan Darah Sistolik (ap_hi)")
    ax.tick_params(axis="x", rotation=8)
    plt.tight_layout()
    return fig


def plot_correlation_heatmap(dataframe):
    """Heatmap korelasi antar variabel numerik."""
    numeric_columns = [
        "age_years",
        "height",
        "weight",
        "bmi",
        "ap_hi",
        "ap_lo",
        "cholesterol",
        "gluc",
        "smoke",
        "alco",
        "active",
        "cardio",
    ]
    correlation_matrix = dataframe[numeric_columns].corr(numeric_only=True).fillna(0)

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(
        correlation_matrix,
        cmap="YlGnBu",
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        cbar=True,
        ax=ax,
    )
    ax.set_title("Korelasi Antar Variabel", fontsize=13, weight="bold")
    plt.tight_layout()
    return fig, correlation_matrix


def build_insight_cardio(status_counts):
    """Menyusun insight singkat dari chart distribusi cardio."""
    total = int(status_counts.sum())
    cardio_count = int(status_counts.get(CARDIO_LABELS[1], 0))
    cardio_percentage = (cardio_count / total * 100) if total else 0
    dominant_status = status_counts.idxmax() if total else "Tidak Ada Data"
    return (
        f"Insight: Dari {format_number(total)} pasien pada filter saat ini, "
        f"{cardio_percentage:.1f}% termasuk kategori berisiko cardio. "
        f"Status yang paling dominan adalah {dominant_status}."
    )


def build_insight_age(dataframe):
    """Insight berdasarkan rata-rata umur tiap status cardio."""
    age_means = dataframe.groupby("cardio_label")["age_years"].mean()
    if len(age_means) < 2:
        return "Insight: Data pada filter saat ini hanya menampilkan satu kelompok status cardio, sehingga perbandingan umur belum terlihat penuh."

    risk_age = age_means.get(CARDIO_LABELS[1], 0)
    non_risk_age = age_means.get(CARDIO_LABELS[0], 0)
    difference = risk_age - non_risk_age
    return (
        f"Insight: Rata-rata umur pasien berisiko cardio adalah {risk_age:.1f} tahun, "
        f"sekitar {difference:.1f} tahun lebih tinggi dibanding kelompok tidak berisiko."
    )


def build_insight_bmi(dataframe):
    """Insight dari perbedaan rata-rata BMI."""
    bmi_means = dataframe.groupby("cardio_label")["bmi"].mean()
    if len(bmi_means) < 2:
        return "Insight: Perbandingan BMI belum lengkap karena data hasil filter hanya berisi satu status cardio."

    risk_bmi = bmi_means.get(CARDIO_LABELS[1], 0)
    non_risk_bmi = bmi_means.get(CARDIO_LABELS[0], 0)
    difference = risk_bmi - non_risk_bmi
    return (
        f"Insight: Kelompok berisiko cardio memiliki rata-rata BMI {risk_bmi:.2f}, "
        f"lebih tinggi {difference:.2f} poin dibanding kelompok tidak berisiko."
    )


def build_insight_ap_hi(dataframe):
    """Insight dari perbedaan tekanan darah sistolik."""
    ap_hi_means = dataframe.groupby("cardio_label")["ap_hi"].mean()
    if len(ap_hi_means) < 2:
        return "Insight: Perbandingan tekanan darah sistolik belum lengkap karena hanya ada satu kelompok status cardio dalam filter."

    risk_ap_hi = ap_hi_means.get(CARDIO_LABELS[1], 0)
    non_risk_ap_hi = ap_hi_means.get(CARDIO_LABELS[0], 0)
    difference = risk_ap_hi - non_risk_ap_hi
    return (
        f"Insight: Rata-rata tekanan darah sistolik pasien berisiko cardio adalah {risk_ap_hi:.1f}, "
        f"lebih tinggi {difference:.1f} poin dari kelompok tidak berisiko."
    )


def build_insight_correlation(correlation_matrix):
    """Insight dari variabel yang paling berkorelasi dengan cardio."""
    cardio_correlation = correlation_matrix["cardio"].drop("cardio")
    if cardio_correlation.abs().sum() == 0:
        return "Insight: Korelasi belum terlalu informatif karena data pada filter saat ini sangat sedikit atau terlalu seragam."

    top_feature = cardio_correlation.abs().idxmax()
    top_value = cardio_correlation[top_feature]
    direction = "positif" if top_value >= 0 else "negatif"
    return (
        f"Insight: Pada data yang sedang difilter, variabel yang paling kuat hubungannya dengan status cardio "
        f"adalah {top_feature} dengan korelasi {top_value:.2f} ({direction})."
    )


# Membaca dan menyiapkan data sekali di awal aplikasi.
df = prepare_data(load_data())

# Bagian judul dan penjelasan singkat project.
st.title("Dashboard Interaktif Analisis Penyakit Kardiovaskular")
st.write(
    """
    Dashboard ini membantu eksplorasi faktor-faktor yang berhubungan dengan risiko penyakit
    kardiovaskular berdasarkan dataset `cardio_cleaned.csv`. Gunakan filter pada sidebar
    untuk melihat perubahan pola data secara interaktif.
    """
)

# Sidebar berisi filter utama agar pengguna bisa fokus pada kelompok pasien tertentu.
st.sidebar.header("Filter Data")
age_min = int(df["age_years"].min())
age_max = int(df["age_years"].max())
selected_age = st.sidebar.slider(
    "Filter umur (age_years)",
    min_value=age_min,
    max_value=age_max,
    value=(age_min, age_max),
)

available_genders = [GENDER_LABELS[value] for value in sorted(df["gender"].unique())]
selected_genders = st.sidebar.multiselect(
    "Filter gender",
    options=available_genders,
    default=available_genders,
)

available_cholesterol = [
    CHOLESTEROL_LABELS[value] for value in sorted(df["cholesterol"].unique())
]
selected_cholesterol = st.sidebar.multiselect(
    "Filter cholesterol",
    options=available_cholesterol,
    default=available_cholesterol,
)

# Filter diterapkan ke dataframe utama sehingga semua komponen ikut berubah otomatis.
filtered_df = df[
    (df["age_years"].between(selected_age[0], selected_age[1]))
    & (df["gender_label"].isin(selected_genders))
    & (df["cholesterol_label"].isin(selected_cholesterol))
].copy()

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan filter saat ini. Silakan ubah pilihan filter.")
    st.stop()

# Menampilkan metrik utama pada baris terpisah agar cepat dibaca.
total_patients = len(filtered_df)
cardio_patients = int(filtered_df["cardio"].sum())
average_bmi = filtered_df["bmi"].mean()
average_ap_hi = filtered_df["ap_hi"].mean()

metric_columns = st.columns(4)
metric_columns[0].metric("Total Data Pasien", format_number(total_patients))
metric_columns[1].metric("Pasien Berisiko Penyakit Kardiovaskular", format_number(cardio_patients))
metric_columns[2].metric("Rata-rata BMI", f"{average_bmi:.2f}")
metric_columns[3].metric("Rata-rata Sistolik (ap_hi)", f"{average_ap_hi:.1f}")

st.markdown("---")

# Baris pertama visualisasi menggunakan dua kolom agar tampilan lebih rapi.
chart_col_1, chart_col_2 = st.columns(2)

with chart_col_1:
    fig_status, status_counts = plot_status_distribution(filtered_df)
    st.pyplot(fig_status, use_container_width=True)
    plt.close(fig_status)
    st.caption(build_insight_cardio(status_counts))

with chart_col_2:
    fig_age = plot_age_distribution(filtered_df)
    st.pyplot(fig_age, use_container_width=True)
    plt.close(fig_age)
    st.caption(build_insight_age(filtered_df))

# Baris kedua visualisasi membandingkan BMI dan tekanan darah sistolik.
chart_col_3, chart_col_4 = st.columns(2)

with chart_col_3:
    fig_bmi = plot_bmi_comparison(filtered_df)
    st.pyplot(fig_bmi, use_container_width=True)
    plt.close(fig_bmi)
    st.caption(build_insight_bmi(filtered_df))

with chart_col_4:
    fig_ap_hi = plot_systolic_comparison(filtered_df)
    st.pyplot(fig_ap_hi, use_container_width=True)
    plt.close(fig_ap_hi)
    st.caption(build_insight_ap_hi(filtered_df))

st.markdown("---")

# Heatmap korelasi dibuat full width agar label variabel tetap mudah terbaca.
fig_heatmap, correlation_matrix = plot_correlation_heatmap(filtered_df)
st.pyplot(fig_heatmap, use_container_width=True)
plt.close(fig_heatmap)
st.caption(build_insight_correlation(correlation_matrix))

st.markdown("---")

# Preview data memudahkan pengguna melihat contoh data mentah setelah filter diterapkan.
st.subheader("Preview Data")
st.write("Menampilkan 20 baris pertama dari data yang sudah difilter.")
st.dataframe(
    filtered_df[
        [
            "age_years",
            "gender_label",
            "height",
            "weight",
            "bmi",
            "ap_hi",
            "ap_lo",
            "cholesterol_label",
            "cardio_label",
        ]
    ]
    .head(20)
    .rename(
        columns={
            "age_years": "Umur",
            "gender_label": "Gender",
            "height": "Tinggi",
            "weight": "Berat",
            "bmi": "BMI",
            "ap_hi": "Sistolik",
            "ap_lo": "Diastolik",
            "cholesterol_label": "Cholesterol",
            "cardio_label": "Status Cardio",
        }
    ),
    use_container_width=True,
)
