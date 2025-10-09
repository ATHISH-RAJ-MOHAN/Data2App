from main import parseCSV
import pandas as pd

"""#### Custom testing without comparision with Pandas"""

test_files = [
    "Testing_Datasets/Countries.csv",
    "Testing_Datasets/Countries_Mixed.csv",
    "Testing_Datasets/Countries_Boolean.csv",
    "Testing_Datasets/Countries_Date.csv",
    "Testing_Datasets/Countries_BadRows.csv",
    "Testing_Datasets/Countries_NoComma.csv",
    "Testing_Datasets/Countries_Empty.csv",
    "Testing_Datasets/Countries_Header_only.csv"
]

def run_test(file_name):
    print(f"\n Testing file: {file_name}")
    try:
        df = parseCSV(file_name)
        print("Column 'Name' (if exists):", df['Name'] if 'Name' in df.columns else "N/A") # This should be changed afterwards, just kept if for testing purpose
        print("Head (first 2 rows):", df.head(2))
        print("Full Data:")
        df.print()
    except Exception as e:
        print(f" Error: {e}")

# Run all tests
for file in test_files:
    run_test(file)

"""#### Custom testing with comparision to Pandas"""

test_files = [
    "Testing_Datasets/Countries.csv",
    "Testing_Datasets/Countries_Mixed.csv",
    "Testing_Datasets/Countries_Boolean.csv",
    "Testing_Datasets/Countries_Date.csv",
    "Testing_Datasets/Countries_BadRows.csv",
    "Testing_Datasets/Countries_NoComma.csv",
    "Testing_Datasets/Countries_Empty.csv",
    "Testing_Datasets/Countries_Header_only.csv"
]

def run_comparison(file_name):
    print(f"\nTesting file: {file_name}")

    # Try your custom parser
    try:
        df_custom = parseCSV(file_name)
        print("Custom Parser Output:")
        df_custom.print()
    except Exception as e:
        print(f"Custom Parser Error: {e}")
        df_custom = None

    # Try pandas
    try:
        df_pandas = pd.read_csv(file_name)
        print("\nPandas Output:")
        print(df_pandas.to_dict(orient='records'))
    except Exception as e:
        print(f"Pandas Error: {e}")
        df_pandas = None

    # Optional: Compare column names and head
    if df_custom and df_pandas is not None:
        print("\nColumn Comparison:")
        print("Custom:", df_custom.columns)
        print("Pandas:", list(df_pandas.columns))

        print("\nHead Comparison (first 2 rows):")
        print("Custom:", df_custom.head(2))
        print("Pandas:", df_pandas.head(2).to_dict(orient='list'))

# Run all comparisons
for file in test_files:
    run_comparison(file)

# Sample test of functions
df = parseCSV('Testing_Datasets/Countries.csv')
print(df['Name'])         # Access column
print(df.head(2))         # Preview first 2 rows
df.print()                # Print all rows

# Sample Projection
print(df[['Name', 'Code']].head(2))

#testing join
print("Testing JOIN")
dg1 = parseCSV("Testing_Datasets/Countries.csv")
dg2 = parseCSV("Testing_Datasets/Countries2.csv")
dg3 = dg1.merge(dg2,on="Name",how="outer")
dg3.print()