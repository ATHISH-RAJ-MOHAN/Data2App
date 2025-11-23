import streamlit as st
import matplotlib.pyplot as plt
from helper import *
from DataGrid import *

st.cache_data.clear()

st.set_page_config(page_title="World Bank GDP and Human Development Index Dashboard", layout="wide")
st.title("🌍 World Bank and Human Development Index Data Analysis Dashboard")

@st.cache_data
def load_data():
    return parseCSV("Testing_Datasets/WorldBank.csv")

@st.cache_data
def load_chunks():
    # Adjust chunk_size depending on dataset size
    return list(parseCSV("Testing_Datasets/WorldBank.csv", chunk_size=5000))

dg = load_data()

# 1) GDP Growth Over Time
st.header("1️⃣ GDP Growth Over Time")
st.markdown("**Question:** How has GDP changed for a selected country over the years?")

raw_names = [c for c in dg["Country Name"].values if c is not None]
countries = []
for c in raw_names:
    if c not in countries:
        countries.append(c)

country = st.selectbox("Select a country", countries, index = countries.index("Albania"))

gdp_filtered = dg[dg["Country Name"] == country]

years = gdp_filtered["Year"].values
gdp_values = gdp_filtered["GDP (USD)"].values

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

# # 2) GDP per Capita Breakdown
# st.header("2️⃣ GDP per Capita Breakdown")
# st.markdown("**Question:** Which countries have the highest average GDP per capita?")

# wb_filtered = dg[dg["GDP per capita (USD)"] != None]

# grouped_country = wb_filtered.groupby("Country Name").agg({
#     "GDP per capita (USD)": "avg"
# })
# result_country = grouped_country[["Country Name", "GDP per capita (USD)"]]

# st.subheader(" Top 10 Countries by Avg GDP per Capita")
# if result_country.numberOfRows > 0:
#     sorted_data = sorted(
#         zip(result_country["Country Name"].values,
#             result_country["GDP per capita (USD)"].values),
#         key=lambda x: x[1] if x[1] is not None else 0,
#         reverse=True
#     )
#     top_countries = sorted_data[:10]
#     labels = [c[0] for c in top_countries]
#     values = [c[1] for c in top_countries]

#     fig2, ax2 = plt.subplots(figsize=(10, 5))
#     wedges, _, autotexts = ax2.pie(
#         values,
#         labels=None,
#         autopct="%1.1f%%",
#         startangle=60
#     )
#     ax2.set_title("Top 10 Countries by Avg GDP per Capita", fontsize=14)
#     ax2.legend(wedges, labels, title="Countries", loc="center left", bbox_to_anchor=(1, 0.5))
#     fig2.tight_layout()
#     left, center, right = st.columns([1, 2, 1])
#     with center:
#         st.pyplot(fig2)
# else:
#     st.info("No data available for Country-level view.")


# 2)  GDP per Capita Breakdown (Chunking)
st.header("2️⃣ GDP per Capita Breakdown")
st.markdown("**Question:** Which countries have the highest average GDP per capita?")

chunks = load_chunks()
partial_results = []
for chunk in chunks:
    wb_filtered = chunk[chunk["GDP per capita (USD)"] != None]
    grouped = wb_filtered.groupby("Country Name").agg({
        "GDP per capita (USD)": "avg"
    })
    partial_results.append(grouped)

result_country = merge_groupby_chunks(
    partial_results,
    group_cols=["Country Name"],
    aggregateDict={"GDP per capita (USD)": "avg"}
)

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

# 3) Human Development by Economic Class
st.header("3️⃣ Human Development by Economic Class")
st.markdown("**Question:** How is the Human Development Index (HDI) distributed across different economic income groups in 2018?")

wb_dg = parseCSV("Testing_Datasets/WorldBank.csv")
hdi_dg = parseCSV("Testing_Datasets/HDI.csv")

wb_2018 = wb_dg[wb_dg["Year"] == 2018]

merged_dg = wb_2018.merge(hdi_dg, on="Country Code", how="inner")

income_groups = merged_dg["IncomeGroup"].values
for i in range(len(income_groups)):
    if "High income" in income_groups[i]:
        income_groups[i] = "High income"
    
hdi_scores = merged_dg["hdi_2018_2"].values 

plot_data_map = {}
desired_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']

for inc, score in zip(income_groups, hdi_scores):
    if inc and score is not None:
        if inc not in plot_data_map:
            plot_data_map[inc] = []
        plot_data_map[inc].append(score)

plot_values = [plot_data_map.get(group, []) for group in desired_order]

fig3, ax3 = plt.subplots(figsize=(10, 10))

box = ax3.boxplot(plot_values, labels=desired_order, patch_artist=True)

colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)

ax3.set_title("Distribution of HDI by Income Group", fontsize=14)
ax3.set_ylabel("HDI Score", fontsize=12)
ax3.set_xlabel("Income Group", fontsize=12)
ax3.grid(True, linestyle="--", alpha=0.5)

left, center, right = st.columns([1, 2, 1])
with center:
    st.pyplot(fig3)



# 4) Average Life Expectancy by Region (with Year Dropdown)
st.header("4️⃣ Average Life Expectancy by Region")
st.markdown("**Question:** How does life expectancy vary across different parts of the world?")

all_years = wb_dg["Year"].values

unique_years = sorted(list(set(y for y in all_years if y is not None)), reverse=True)

selected_year = st.selectbox("Select Year", unique_years, index = unique_years.index(2017))

wb_year_filtered = wb_dg[wb_dg["Year"] == selected_year]

grouped_life = wb_year_filtered.groupby("Region").agg({
    "Life expectancy at birth (years)": "avg"
})

regions = grouped_life["Region"].values
life_expectancies = grouped_life["Life expectancy at birth (years)"].values

clean_data = []
for r, l in zip(regions, life_expectancies):
    if r is not None and l is not None:
        clean_data.append((r, l))

clean_data.sort(key=lambda x: x[1], reverse=True)
plot_regions = [x[0] for x in clean_data]
plot_values = [x[1] for x in clean_data]

if plot_regions:
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    bars = ax4.bar(plot_regions, plot_values, color="#5f9e6e")
    
    ax4.set_title(f"Average Life Expectancy by Region", fontsize=14)
    ax4.set_ylabel("Life Expectancy)", fontsize=12)
    ax4.set_xlabel("Region", fontsize=12)
    
    ax4.set_ylim(0, 100)
    
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.1f}', ha='center', va='bottom')

    plt.xticks(rotation=45, ha='right')
    ax4.grid(axis='y', linestyle="--", alpha=0.5)
    
    fig4.tight_layout()
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.pyplot(fig4)
else:
    st.warning(f"No Life Expectancy data available for the year {selected_year}.")


# ───────────────────────────────────────────────
st.markdown("---")
st.caption("All visualizations powered by our custom CSV parser and DataGrid class.")