from main import parseCSV
import pandas as pd

"""#### Custom testing without comparision with Pandas"""

test_files = [
    "Testing_Datasets/Countries.csv",
    "Testing_Datasets/Countries_Mixed.csv",
    "Testing_Datasets/Countries_Boolean.csv",
    "Testing_Datasets/Countries_Dates.csv",
    "Testing_Datasets/Countries_BadRows.csv",
    "Testing_Datasets/Countries_NoComma.csv",
    "Testing_Datasets/Countries_Empty.csv",
    "Testing_Datasets/Countries_Header_only.csv"
]

def run_test(file_name):
    print(f"\n Testing file: {file_name}")
    try:
        df = parseCSV(file_name)
        print("Column 'Name' (if exists):", df['Name'] if 'Name' in df.columns else "N/A") # This should be changed afterwards, just kept it for testing purpose
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
    "Testing_Datasets/Countries_Dates.csv",
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

def run_filter_tests(file_name):
    print(f"\nRunning FILTER tests on: {file_name}")
    try:
        df = parseCSV(file_name)
    except Exception as e:
        print(f"Error loading {file_name}: {e}")
        return

    # 1. Bracket-style filter: Population > 1B
    print("\n[1] Bracket-style filter: Population > 1B")
    try:
        df[df['Population'] > 1_000_000_000].print()
    except Exception as e:
        print(" Failed: Population > 1B filter:", e)

    # 2. Bracket-style .isin(): Name in ['USA', 'Germany']
    print("\n[2] .isin(): Name in ['USA', 'Germany']")
    try:
        df[df['Name'].isin(['USA', 'Germany'])].print()
    except Exception as e:
        print(" Failed: .isin() filter:", e)

    # 3. .query(): Population < 500M and GNP > 100000
    print("\n[3] .query(): Population < 500M and GNP > 100000")
    try:
        df.query("Population < 500000000 and GNP > 100000").print()
    except Exception as e:
        print(" Failed: .query() filter:", e)

    # 4. Logical AND: GNP > 100000 and Population < 500M (manual zip)
    print("\n[4] Logical AND (manual zip): GNP > 100000 and Population < 500M")
    try:
        mask = [(a and b) for a, b in zip(df['GNP'] > 100000, df['Population'] < 500000000)]
        df[mask].print()
    except Exception as e:
        print(" Failed: Logical AND zip:", e)

    # 5. .loc[row_index, column_name]
    print("\n[5] .loc[row_index, column_name]: Access single cell")
    try:
        print("Row 1, 'Name':", df.loc[1, 'Name'])
    except Exception as e:
        print(" Failed: .loc[row_index, column_name]:", e)

    # 6. .loc[[row1, row2]]
    print("\n[6] .loc[[row1, row2]]: Select multiple rows")
    try:
        df.loc[[0, 2]].print()
    except Exception as e:
        print(" Failed: .loc[[row1, row2]]:", e)

    # 7. .loc[[row1, row2], ['col1', 'col2']]
    print("\n[7] .loc[[row1, row2], ['col1', 'col2']]: Select rows and columns")
    try:
        df.loc[[0, 2], ['Name', 'GNP']].print()
    except Exception as e:
        print(" Failed: .loc[[row], [col]]:", e)

    # 8. Predicate filtering via bracket-style logical chaining
    print("\n[8] Predicate filtering: GNP < 150000 and Population < 500M")
    try:
        df[(df['GNP'] < 150000) & (df['Population'] < 500_000_000)].print()
    except Exception as e:
        print(" Failed: Predicate filtering:", e)
    

run_filter_tests('Testing_Datasets/Countries.csv')