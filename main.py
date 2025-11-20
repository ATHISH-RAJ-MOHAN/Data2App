import streamlit as st
import tempfile
from DataGrid import *
from helper import *

st.title("Upload Multiple CSVs (Using Custom parseCSV + DataGrid)")

uploaded_files = st.file_uploader(
    "Upload CSV files",
    type=["csv"],
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"{len(uploaded_files)} file(s) uploaded")

    datagrids = {}

    for file in uploaded_files:
        st.write(f"## 📄 {file.name}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(file.read())
            temp_path = tmp.name

        dg = parseCSV(temp_path)
        datagrids[file.name] = dg

        st.write("#### Preview:")

        head_rows = dg.head()
        columns = list(head_rows.keys())

        table_data = [
            [head_rows[col][i] for col in columns]
            for i in range(min(5, dg.numberOfRows))
        ]

        st.table([columns] + table_data) 

        st.write(f"Rows: {dg.numberOfRows}, Columns: {len(dg.columns)}")
        st.write("---")

        