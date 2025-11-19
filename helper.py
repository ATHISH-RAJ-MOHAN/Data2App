from DataGrid import DataGrid
from datetime import datetime

# def parseCSV(filePath, separator=',', parse_dates=True, auto_detect_separator=False):
def parseCSV(filePath, chunk_size=None):
    try:
        f = open(filePath, 'r')
    except FileNotFoundError:
        raise ValueError(f"File not found: {filePath}")

    header = f.readline().strip()
    if not header:
        raise ValueError("CSV file is empty")

    columns = header.split(",")
    numberOfColumns = len(columns)

    # Normal non-chunk behavior (same as before)
    if chunk_size is None:
        lines = [line.strip() for line in f if line.strip()]
        dataDict = {col: [] for col in columns}
        warnings = []

        for lineNumber, line in enumerate(lines, start=2):
            values = line.split(",")

            if len(values) < numberOfColumns:
                values += [None] * (numberOfColumns - len(values))
            elif len(values) > numberOfColumns:
                warnings.append(f"Line {lineNumber}: Extra values {values[numberOfColumns:]} ignored")
                values = values[:numberOfColumns]

            for i, value in enumerate(values):
                typed = inferType(value)
                dataDict[columns[i]].append(typed)

        if warnings:
            print("Parsing Warnings:")
            for w in warnings:
                print("  -", w)

        f.close()
        return DataGrid(dataDict)

    # Chunk mode: generator
    def chunk_generator():
        dataDict = {col: [] for col in columns}
        count = 0
        lineNumber = 1

        for line in f:
            lineNumber += 1
            line = line.strip()
            if not line:
                continue

            values = line.split(",")

            if len(values) < numberOfColumns:
                values += [None] * (numberOfColumns - len(values))
            elif len(values) > numberOfColumns:
                values = values[:numberOfColumns]

            for i, value in enumerate(values):
                typed = inferType(value)
                dataDict[columns[i]].append(typed)

            count += 1

            # Emit chunk when full
            if count >= chunk_size:
                yield DataGrid(dataDict)
                dataDict = {col: [] for col in columns}
                count = 0

        # Emit final partial chunk
        if count > 0:
            yield DataGrid(dataDict)

        f.close()

    return chunk_generator()

# def inferType(value, parse_dates=True):
def inferType(value):
    if value is None:
        return None

    value = value.strip()

    if value.lower() in ('', 'null', 'na', 'nan','None',None):
        return None
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return value

# merging of chunks - for filtering and projection
def merge_chunks(chunk_list):
    if not chunk_list:
        return DataGrid({})

    # Initialize combined dict
    combined = {col: [] for col in chunk_list[0].columns}

    # Append rows from all chunks
    for chunk in chunk_list:
        for col in chunk.columns:
            combined[col].extend(chunk.data[col])

    return DataGrid(combined)

#merging aggregation results for the chunks
def merge_simple_agg_chunks(partials, agg, column_name):
    if agg == "sum":
        val = sum(p for p in partials if p is not None)

    elif agg == "min":
        vals = [p for p in partials if p is not None]
        val = min(vals) if vals else None

    elif agg == "max":
        vals = [p for p in partials if p is not None]
        val = max(vals) if vals else None

    elif agg == "count":
        val = sum(p for p in partials if p is not None)

    elif agg == "avg":
        total = 0
        count = 0
        for p_total, p_count in partials:
            total += p_total
            count += p_count
        val = total / count if count > 0 else None
    else:
        raise ValueError("Unsupported aggregation")

    return DataGrid({column_name: [val]})


# merging of chunks - for group by and aggregation
def merge_groupby_chunks(chunk_list, group_cols, aggregateDict):
    if not chunk_list:
        return DataGrid({})

    merged = {}

    for chunk in chunk_list:
        for i in range(chunk.numberOfRows):
            key = tuple(chunk.data[col][i] for col in group_cols)

            if key not in merged:
                merged[key] = {}

                for col, agg in aggregateDict.items():
                    val = chunk.data[col][i]

                    if agg == "count":
                        merged[key][col] = 1

                    elif agg == "avg":
                        merged[key][col] = (val, 1)

                    else:
                        merged[key][col] = val

            else:
                for col, agg in aggregateDict.items():
                    val = chunk.data[col][i]

                    if agg == "sum":
                        merged[key][col] += val

                    elif agg == "count":
                        merged[key][col] += 1

                    elif agg == "min":
                        merged[key][col] = min(merged[key][col], val)

                    elif agg == "max":
                        merged[key][col] = max(merged[key][col], val)

                    elif agg == "avg":
                        s, c = merged[key][col]
                        merged[key][col] = (s + val, c + 1)

                    else:
                        raise ValueError(f"Unsupported aggregation: {agg}")

    final_data = {col: [] for col in group_cols + list(aggregateDict.keys())}

    for key, agg_values in merged.items():

        for idx, col in enumerate(group_cols):
            final_data[col].append(key[idx])

        for col, agg in aggregateDict.items():
            val = agg_values[col]

            if agg == "avg":
                s, c = val
                final_data[col].append(s / c)
            else:
                final_data[col].append(val)

    return DataGrid(final_data)

def merge_join_chunks(left_chunks, right_chunks, on, how="inner"):
    partial_results = []

    for left_chunk in left_chunks:
        unmatched_rows = [
            {col: left_chunk.data[col][i] for col in left_chunk.columns}
            for i in range(left_chunk.numberOfRows)
        ]
        matched_flags = [False] * left_chunk.numberOfRows

        for right_chunk in right_chunks:
            merged = left_chunk.merge(right_chunk, on=on, how="inner")
            partial_results.append(merged)

            right_keys = {right_chunk.data[on][i] for i in range(right_chunk.numberOfRows)}
            for i, row in enumerate(unmatched_rows):
                if row[on] in right_keys:
                    matched_flags[i] = True

        if how in ("left", "outer"):
            if any(not m for m in matched_flags):
                left_only_rows = []
                right_cols = [c for c in right_chunks[0].columns if c != on]
                for i, matched in enumerate(matched_flags):
                    if not matched:
                        row = unmatched_rows[i].copy()
                        for col in right_cols:
                            row[f"{col}_2"] = None
                        left_only_rows.append(row)

                if left_only_rows:
                    all_cols = set(left_chunk.columns)
                    all_cols.update(f"{c}_2" for c in right_cols)
                    left_only_dg = {col: [] for col in all_cols}
                    for row in left_only_rows:
                        for col in all_cols:
                            left_only_dg[col].append(row.get(col, None))
                    partial_results.append(DataGrid(left_only_dg))

    if not partial_results:
        return DataGrid({})

    all_cols = set()
    for dg in partial_results:
        all_cols.update(dg.columns)

    final = {col: [] for col in all_cols}
    for dg in partial_results:
        for col in all_cols:
            if col in dg.data:
                final[col].extend(dg.data[col])
            else:
                final[col].extend([None] * dg.numberOfRows)

    return DataGrid(final)



