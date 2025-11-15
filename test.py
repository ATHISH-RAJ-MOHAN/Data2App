from main import parseCSV, DataGrid, merge_chunks,merge_groupby_chunks
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
'''
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

print("TESTING COUNT")
print(type(dg1['GNP']))
print(dg1['GNP'].count())
print(dg1['GNP'].min())
print(dg1['GNP'].max())
print(dg1['GNP'].sum())
print(dg1['GNP'].avg())

print("TESTING GROUP BY")
dg1.groupby('Name').agg({'Population' : 'sum'}).print()
print()
dg1.groupby('Name').agg({'Population' : 'max'}).print()
print()
dg1.groupby('Name').agg({'Population' : 'min'}).print()
print()
dg1.groupby('Name').agg({'Population' : 'avg'}).print()
print()
dg1.groupby('Name').agg({'Population' : 'count'}).print()

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


print("\nGROUPBY Edge Cases")
dg1 = parseCSV("Testing_Datasets/Countries_BadRows.csv")
# 1. Group by column with all unique values
print("Group by 'Name' (unique keys):")
dg1.groupby('Name').agg({'GNP': 'sum'}).print()

# 2. Group by column with missing values
print("\nGroup by 'GNP' (includes None):")
if 'Population' in dg1.columns:
    dg1.groupby('GNP').agg({'Population': 'sum'}).print()
else:
    print("Column 'Population' not found — skipping aggregation.")

# 3. Group by float column
print("\nGroup by float GNP values:")
dg1.groupby('GNP').agg({'Name': 'count'}).print()

# 4. Group by derived column
# Create derived column
'''
'''
dg1.data['Size'] = ['Large' if p > 1e9 else 'Small' for p in dg1['Population']]
# Register the column in the schema
if 'Size' not in dg1.columns:
    dg1.columns.append('Size')
# Now group by it
print("Group by derived 'Size' column:")
dg1.groupby('Size').agg({'Name': 'count'}).print()


# Simulate parsed CSV data
dg1 = DataGrid({
    'Name': ['USA', 'India', 'Germany'],
    'Code': ['US', 'IN', 'DE'],
    'GNP': [200000, None, 120000],
    'Population': [None, None, 83000000]  # intentionally messy
})


# Derived column: classify countries as 'Large' or 'Small' population
dg1.data['Size'] = [None] * dg1.numberOfRows
for i in range(dg1.numberOfRows):
    pop = dg1.data.get('Population', [None]*dg1.numberOfRows)[i]
    if pop is None:
        dg1.data['Size'][i] = None
    elif pop > 1e8:
        dg1.data['Size'][i] = 'Large'
    else:
        dg1.data['Size'][i] = 'Small'

# Register the column
if 'Size' not in dg1.columns:
    dg1.columns.append('Size')

# Group by the derived column
print("Group by derived 'Size' column:")
dg1.groupby('Size').agg({'Name': 'count'}).print()



print("\nAGGREGATION Edge Cases")

# 1. Aggregating with None values
print("Aggregate GNP with missing values:")
print("Sum:", dg1['GNP'].sum())
print("Avg:", dg1['GNP'].avg())
print("Min:", dg1['GNP'].min())
print("Max:", dg1['GNP'].max())
print("Count:", dg1['GNP'].count())

# 2. Aggregating mixed types (GNP + Name)
print("\nMixed-type aggregation:")
print("GNP avg:", dg1['GNP'].avg())
print("Name count:", dg1['Name'].count())

# 3. Custom lambda aggregation
print("\nCustom aggregation: GNP > 100000")
filtered = [v for v in dg1['GNP'].values if v is not None and v > 100000]
print("Sum of GNP > 100K:", sum(filtered))



print("\nMERGE Edge Cases")

# 1. Outer join with missing keys
print("Outer join on 'Name':")
dg2 = parseCSV("Testing_Datasets/Countries2.csv")
dg1.merge(dg2, on="Name", how="outer").print()

# 2. Left join with unmatched rows
print("\nLeft join on 'Code':")
left = parseCSV("Testing_Datasets/Countries.csv")
right = DataGrid({'Code': ['US', 'IN'], 'Region': ['Americas', 'Asia']})
left.merge(right, on='Code', how='left').print()

# 3. Join with duplicate keys
print("\nJoin with duplicate keys:")
dup = DataGrid({'Name': ['India', 'India'], 'GNP': [80000, 85000]})
dg1.merge(dup, on='Name', how='inner').print()

# 4. Join with type mismatch
print("\nJoin with GNP as string:")
typed = DataGrid({'GNP': ['200000', '120000.5'], 'Label': ['Strong', 'Moderate']})
dg1.merge(typed, on='GNP', how='inner').print()  # Should return empty or fail gracefully


print("\nPARSING Edge Cases (Bad Rows)")

# parsing the malformed CSV
dg_bad = parseCSV("Testing_Datasets/Countries_BadRows.csv")

# Print parsed data to inspect what happened
dg_bad.print()

# Check if parser handled bad rows
print("\nCheck missing or extra columns:")
for col, values in dg_bad.data.items():
    print(f"{col}: {values}")

# Now, check for missing values
missing_counts = {col: sum(1 for v in vals if v is None) for col, vals in dg_bad.data.items()}
print("\nMissing value counts per column:")
print(missing_counts)

# merging dg_bad (from bad rows) with dg2 (normal one)
print("\nMerge with partially bad data:")
dg_bad.merge(dg2, on="Code", how="outer").print()

'''

#--------------------- Tests for Chunking ------------------------

# Test-1
'''
print("\n\n===== TESTING CHUNKED PARSER =====")

for file in test_files:
    for i, chunk in enumerate(parseCSV(file, chunk_size=2), start=1):
        print(file)
        print(f"\n=== Chunk {i} ===")
        chunk.print()
'''

#--------------------- Chunking + Projection ------------------------
print("--------------------- Chunking + Projection ------------------------")
test_file = "Testing_Datasets/Countries.csv"

# Choose the columns you want to select
selected_columns = ["Name", "Population"]

# Chunk size 
chunk_size = 2

selected_chunks = []

# Step 1: Iterate through chunked CSV
for i, chunk in enumerate(parseCSV(test_file, chunk_size=chunk_size), start=1):
    print(f"\n=== INPUT CHUNK {i} ===")
    chunk.print()

    # Step 2: Select columns using pandas-style []
    selected_chunk = chunk[selected_columns]

    print(f"\n=== SELECTED CHUNK {i} ===")
    selected_chunk.print()

    selected_chunks.append(selected_chunk)

# Step 3: Merge chunks into final output
final_result = merge_chunks(selected_chunks)

print("\n======== FINAL MERGED RESULT ========")
final_result.print()


# --------------------- Chunking + Filtering ------------------------
print("--------------------- Chunking + Filtering ------------------------")
test_file = "Testing_Datasets/Countries.csv"

# Chunk size 
chunk_size = 2

filtered_chunks = []

# Step 1: Iterate through chunked CSV
for i, chunk in enumerate(parseCSV(test_file, chunk_size=chunk_size), start=1):
    print(f"\n=== INPUT CHUNK {i} ===")
    chunk.print()

    # Step 2: Filter rows using boolean expressions
    # Example: Population > 100_000_000
    filtered_chunk = chunk[chunk["Population"] > 100_000_000]

    print(f"\n=== FILTERED CHUNK {i} ===")
    filtered_chunk.print()

    filtered_chunks.append(filtered_chunk)

# Step 3: Merge chunks into final filtered output
final_result = merge_chunks(filtered_chunks)

print("\n======== FINAL MERGED FILTERED RESULT ========")
final_result.print()


print("--------------------- Chunking + GroupBy ------------------------")
def run_groupby_chunk_tests(file_name, chunk_size=2):
    print(f"\nTESTING GROUP BY WITH CHUNKING on {file_name}")

    # Run the same tests you did without chunking
    tests = [
        ("sum",   {"Population": "sum"}),
        ("max",   {"Population": "max"}),
        ("min",   {"Population": "min"}),
        ("avg",   {"Population": "avg"}),
        ("count", {"Population": "count"}),
    ]

    for test_name, aggDict in tests:
        print(f"\n==== TEST: Population {test_name.upper()} ====\n")

        chunk_results = []

        # 1. Process each chunk
        for i, chunk in enumerate(parseCSV(file_name, chunk_size=chunk_size), start=1):
            print(f"\n--- INPUT CHUNK {i} ---")
            chunk.print()

            g = chunk.groupby(["Name"]).agg(aggDict)


            print(f"\n--- GROUPED CHUNK {i} ---")
            g.print()

            chunk_results.append(g)

        # 2. Merge results
        final = merge_groupby_chunks(chunk_results, ["Name"], aggDict)

        print("\n--- FINAL MERGED RESULT ---")
        final.print()

test_file = "Testing_Datasets/Countries.csv"
run_groupby_chunk_tests(test_file)      



