import streamlit as st
import matplotlib.pyplot as plt
from helper import *
from DataGrid import *

# App Setup
st.set_page_config(page_title="World Bank GDP Dashboard", layout="wide")
st.title("🌍 World Bank GDP Dashboard")
st.write("Built using our custom CSV parser and DataGrid framework with chunking support")

# Load dataset in chunks
@st.cache_data
def load_chunks():
    # Adjust chunk_size depending on dataset size
    return list(parseCSV("Testing_Datasets/WorldBank.csv", chunk_size=5000))

chunks = load_chunks()

# 1) GDP Growth Over Time
st.header("1️⃣ GDP Growth Over Time")
st.markdown("**Question:** How has GDP changed for a selected country over the years?")

# Merge chunks into one DataGrid for country-level filtering
dg = merge_chunks(chunks)

# Collect raw country names (skip None)
raw_names = [c for c in dg["Country Name"].values if c is not None]
countries = []
for c in raw_names:
    if c not in countries:
        countries.append(c)

# Dropdown for country selection
country = st.selectbox("Select a country", countries)

# Filter using pandas-style mask
gdp_filtered = dg[dg["Country Name"] == country]

# Extract columns
years = gdp_filtered["Year"].values
gdp_values = gdp_filtered["GDP (USD)"].values

# Plot GDP trend
if any(v is not None for v in gdp_values):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years, gdp_values, marker="o", linestyle="-", color="green", label="GDP (USD)")
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("GDP (USD)", fontsize=12)
    ax.set_title(f"GDP Trend for {country}", fontsize=14)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", fontsize=10)
    fig.tight_layout()

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.pyplot(fig)
else:
    st.warning(f"No GDP data available for {country}.")

st.markdown("---")

# 2)  GDP per Capita Breakdown (Chunking)
st.header("2️⃣ GDP per Capita Breakdown")
st.markdown("**Question:** Which countries have the highest average GDP per capita?")

# Step 1: Group + aggregate per chunk
partial_results = []
for chunk in chunks:
    wb_filtered = chunk[chunk["GDP per capita (USD)"] != None]
    grouped = wb_filtered.groupby("Country Name").agg({
        "GDP per capita (USD)": "avg"
    })
    partial_results.append(grouped)

# Step 2: Merge groupby results across chunks
result_country = merge_groupby_chunks(
    partial_results,
    group_cols=["Country Name"],
    aggregateDict={"GDP per capita (USD)": "avg"}
)

# Pie Chart: Top 10 Countries by Avg GDP per Capita
st.subheader(" Top 10 Countries by Avg GDP per Capita")
if result_country.numberOfRows > 0:
    sorted_data = sorted(
        zip(result_country["Country Name"].values,
            result_country["GDP per capita (USD)"].values),
        key=lambda x: x[1] if x[1] is not None else 0,
        reverse=True
    )
    top_countries = sorted_data[:10]
    labels = [c[0] for c in top_countries]
    values = [c[1] for c in top_countries]

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    wedges, _, autotexts = ax2.pie(
        values,
        labels=None,
        autopct="%1.1f%%",
        startangle=60
    )
    ax2.set_title("Top 10 Countries by Avg GDP per Capita", fontsize=14)
    ax2.legend(wedges, labels, title="Countries", loc="center left", bbox_to_anchor=(1, 0.5))
    fig2.tight_layout()
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.pyplot(fig2)
else:
    st.info("No data available for Country-level view.")

st.markdown("---")
st.caption("All visualizations powered by chunked parsing and DataGrid aggregation.")