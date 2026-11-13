# World Bank & Human Development Index Analytics Dashboard

An interactive Streamlit dashboard for exploring economic and human development indicators using a custom-built, Pandas-style data engine.

The project processes World Bank and United Nations Development Programme (UNDP) datasets to help users explore GDP trends, GDP per capita, Human Development Index (HDI), and life expectancy across countries and regions.

## Features

- Explore GDP trends for a selected country over time.
- Compare countries by average GDP per capita.
- Examine HDI distributions across economic income groups.
- Compare average life expectancy across world regions.
- Filter, project, aggregate, group, and join tabular data using a custom data engine.
- Process CSV files in chunks to support datasets that may be too large to load all at once.

## Custom Data Engine

The project implements a Pandas-style data-processing engine directly in Python. Its `DataGrid` structure stores columns and supports core tabular operations, including:

- CSV parsing and type inference
- Boolean-mask filtering
- Column projection
- Aggregation and group-by operations
- Inner, left, right, and outer joins
- Chunk-based processing and result merging

The dashboard uses this engine for its data operations rather than relying on Pandas for those operations. Chunked workflows process data in batches and combine partial results.

## Datasets and Visualizations

The dashboard uses World Bank economic indicator data and UNDP Human Development Index data.

| Analysis | Visualization |
|---|---|
| GDP change for a selected country over time | Line chart |
| Countries with the highest average GDP per capita | Pie chart |
| HDI distribution by economic income group | Box plot |
| Average life expectancy by region | Bar chart |

## Technology

- Python
- Streamlit
- Custom `DataGrid` data-processing engine
- Matplotlib
- CSV datasets

## Run Locally

```bash
git clone -b dev --single-branch https://github.com/ATHISH-RAJ-MOHAN/Data2App.git
cd Data2App
python -m venv .venv
```

Activate the virtual environment, install the project dependencies, and launch the dashboard:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Make sure the datasets are available at the file paths configured by the application. If the repository uses a different dependency file or app entry point, update the commands above to match it.

## Team Contributions

This was a team project. My contributions included implementing the CSV parser, type inference, filtering, projection, and chunk-based parsing and merging. I also integrated the functions into the application and developed the GDP trend and GDP-per-capita visualizations.

Other team contributions included aggregation, group-by, and join operations, along with their chunk-based processing support. The team collaborated on dashboard integration, debugging, and testing.
