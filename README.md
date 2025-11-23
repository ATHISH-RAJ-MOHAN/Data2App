🌍 Custom DataGrid Library & World Bank Dashboard
This project implements a custom, lightweight data manipulation library (built from scratch in Python) designed to mimic core functionalities of Pandas. It demonstrates the library's capabilities through an interactive Streamlit Dashboard that analyzes World Bank GDP and Human Development Index (HDI) data.

📂 Project Structure
DataGrid.py: The core library containing the DataGrid class, Column class for operator overloading, and GroupBy logic.

helper.py: Utilities for parsing CSVs (including chunked reading), type inference, and logic for merging dataset chunks.

app.py: The main execution entry point. A Streamlit application that visualizes the data using Matplotlib and the custom DataGrid library.

🚀 Features
1. Custom DataGrid Library
Unlike standard data libraries, this project builds data structures from the ground up:

CSV Parsing: Includes robust error handling, automatic type inference (Integer, Float, Boolean, Date), and generator-based chunk processing for memory efficiency.

DataGrid Class:

Filtering: Supports boolean masking and query-like filtering (e.g., dg[dg["col"] > 5]).

Merging: Implements inner, left, right, and outer joins using hash-based indexing.

Grouping & Aggregation: Custom groupby() functionality supporting sum, avg, min, max, and count operations.

Loc Accessor: Row/Column slicing similar to Pandas .loc.

Operator Overloading: The Column class overrides operators (>, <, ==, &, |) to enable intuitive element-wise comparisons.

2. Interactive Dashboard
The dashboard (app.py) visualizes global economic and health metrics:

GDP Growth Trends: Line charts visualizing GDP changes over time for specific countries.

GDP per Capita Analysis: Pie charts highlighting the top 10 countries by average GDP per capita.

HDI Distribution: Box plots showing Human Development Index scores across different income groups (High, Upper Middle, Lower Middle, Low).

Life Expectancy: Bar charts comparing average life expectancy across global regions for a selected year.

🛠️ Installation & Requirements
Ensure you have Python 3.x installed. You will need the following external libraries for the interface and plotting:
pip install streamlit matplotlib
Note: The data manipulation logic (DataGrid and helper) relies only on the Python standard library.

▶️ Usage
Running the Dashboard
To launch the interactive dashboard, navigate to the project directory and run:
streamlit run app.py