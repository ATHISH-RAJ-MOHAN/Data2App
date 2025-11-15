from datetime import datetime

class Column:
    def __init__(self, values):
        self.values = values

    # Comparison operators return Column of booleans
    def __gt__(self, other):
        return Column([v > other if v is not None else False for v in self.values])

    def __lt__(self, other):
        return Column([v < other if v is not None else False for v in self.values])

    def __eq__(self, other):
        return Column([v == other if v is not None else False for v in self.values])

    def __ge__(self, other):
        return Column([v >= other if v is not None else False for v in self.values])

    def __le__(self, other):
        return Column([v <= other if v is not None else False for v in self.values])

    def __ne__(self, other):
        return Column([v != other if v is not None else False for v in self.values])

    # Logical operators return Column of booleans
    def __and__(self, other):
        return Column([a and b for a, b in zip(self.values, other.values)])

    def __or__(self, other):
        return Column([a or b for a, b in zip(self.values, other.values)])

    def __invert__(self):
        return Column([not a for a in self.values])

    # Membership check
    def isin(self, values):
        return Column([v in values if v is not None else False for v in self.values])

    # Indexing and length
    def __getitem__(self, index):
        return self.values[index]

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return repr(self.values)
    
    def count(self):
        return sum(1 for v in self.values if v is not None)

    def min(self):
        validValues = [v for v in self.values if v is not None]
        if(validValues):
            return min(validValues)
        return None

    def max(self):
        validValues = [v for v in self.values if v is not None]
        if(validValues):
            return max(validValues)
        return None

    def sum(self):
        validValues = [v for v in self.values if isinstance(v, (int, float, bool))]
        if(validValues):
            return sum(validValues)
        return 0

    def avg(self):
        validValues = [v for v in self.values if isinstance(v, (int, float, bool))]
        if(validValues):
            return sum(validValues)/len(validValues)
        return None

    

class LocAccessor:
    def __init__(self, grid):
        self.grid = grid

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            row_key, col_key = key
            if isinstance(row_key, int) and isinstance(col_key, str):
                if col_key not in self.grid.columns:
                    raise KeyError(f"Column '{col_key}' not found")
                if not (0 <= row_key < self.grid.numberOfRows):
                    raise IndexError("Row index out of range")
                return self.grid.data[col_key][row_key]

            if isinstance(row_key, list) and isinstance(col_key, list):
                for i in row_key:
                    if not (0 <= i < self.grid.numberOfRows):
                        raise IndexError(f"Row index {i} out of range")
                for col in col_key:
                    if col not in self.grid.columns:
                        raise KeyError(f"Column '{col}' not found")
                filtered_data = {
                    col: [self.grid.data[col][i] for i in row_key]
                    for col in col_key
                }
                return DataGrid(filtered_data)

        elif isinstance(key, list) and all(isinstance(i, int) for i in key):
            for i in key:
                if not (0 <= i < self.grid.numberOfRows):
                    raise IndexError(f"Row index {i} out of range")
            filtered_data = {
                col: [self.grid.data[col][i] for i in key]
                for col in self.grid.columns
            }
            return DataGrid(filtered_data)

        raise TypeError("Use .loc[row_index, column_name] or .loc[[...]]")

class GroupBy:
    def __init__(self, dataGridObject, groupByColumns):
        self.dataGridObject = dataGridObject
        self.groupByColumns = groupByColumns

    def agg(self, aggregateDict):
        groups = {}
        nonGroupByColumns = [c for c in self.dataGridObject.columns if c not in self.groupByColumns]

        # Build groups
        for i in range(self.dataGridObject.numberOfRows):
            key = tuple(self.dataGridObject.data[c][i] for c in self.groupByColumns)
            groups.setdefault(key, {col: [] for col in nonGroupByColumns})
            for col in nonGroupByColumns:
                groups[key][col].append(self.dataGridObject.data[col][i])

        # Aggregate
        result = {col: [] for col in self.groupByColumns + list(aggregateDict.keys())}
        for key, valuesDict in groups.items():
            for i, col in enumerate(self.groupByColumns):
                result[col].append(key[i])
            for col, func in aggregateDict.items():
                vals = [v for v in valuesDict[col] if v is not None]
                if not vals:
                    result[col].append(None)
                elif func == 'sum':
                    result[col].append(sum(vals))
                elif func == 'avg':
                    result[col].append(sum(vals)/len(vals))
                elif func == 'min':
                    result[col].append(min(vals))
                elif func == 'max':
                    result[col].append(max(vals))
                elif func == 'count':
                    result[col].append(len(vals))
                else:
                    raise ValueError(f"Unsupported aggregation: {func}")

        return DataGrid(result)

class DataGrid:
    def __init__(self, dataDict):
        
        self.columns = list(dataDict.keys())
        self.numberOfRows = max((len(rows) for rows in dataDict.values()), default=0)
        self.loc = LocAccessor(self) # For loc method
        
        for col in self.columns:
            col_data = dataDict[col]
            if len(col_data) < self.numberOfRows:
                col_data += [None] * (self.numberOfRows - len(col_data))
            dataDict[col] = col_data
        self.data = dataDict

    def __getitem__(self, key):
      if isinstance(key, str):
          # Access a single column
          return Column(self.data.get(key, []))

      elif isinstance(key, list):
          # Case: Boolean mask
          if all(isinstance(k, bool) for k in key):
              return self.filter_by_mask(key)

          # Case: Column projection
          elif all(isinstance(k, str) for k in key):
              return DataGrid({col: self.data[col] for col in key})

          else:
              raise TypeError("Unsupported list type for __getitem__")

      elif isinstance(key, Column):
        # If values are booleans, use as mask
        if all(isinstance(k, bool) for k in key.values):
            return self.filter_by_mask(key.values)

        # If values are non-booleans, treat truthy values as True
        else:
            mask = [bool(v) for v in key.values]
            return self.filter_by_mask(mask)

      else:
          raise TypeError("Unsupported key type")

    def head(self, n=5):
        return {col: vals[:n] for col, vals in self.data.items()}

    def print(self):
        for i in range(self.numberOfRows):
            row = {col: self.data[col][i] for col in self.columns}
            print(row)
    
    def merge(self, dg2, on, how = "inner"):
        if not isinstance(dg2, DataGrid):
            raise TypeError("Passed parameter is not a DataGrid")
        if on not in self.columns or on not in dg2.columns:
            raise ValueError("The column to be joined on must exist in both the data grids")

        leftRows = []
        for i in range(self.numberOfRows):
            d = {}
            for col in self.columns:
               d[col] = self.data[col][i]
            leftRows.append(d)
            
        rightRows = []
        for i in range(dg2.numberOfRows):
            d = {}
            for col in dg2.columns:
               d[col] = dg2.data[col][i]
            rightRows.append(d)
            
        rightGridIndex = {}
        for row in rightRows:
            key = row[on]
            rightGridIndex.setdefault(key, []).append(row)
            
        mergedRows = []
        for lrow in leftRows:
            key = lrow[on]
            if key in rightGridIndex:
                for rrow in rightGridIndex[key]:
                    mergedRows.append({**lrow, **{f"{col}_2": v for col, v in rrow.items() if col != on}})
            elif how in ("left", "outer"):
                mergedRows.append({**lrow, **{f"{col}_2": None for col in dg2.columns if col != on}})
        
        if how in ("right", "outer"):
            leftGridkeys = {row[on] for row in leftRows}
            for rrow in rightRows:
                key = rrow[on]
                if key not in leftGridkeys:
                    mergedRows.append({**{col: None for col in self.columns}, on: key, **{f"{col}_2": v for col, v in rrow.items() if col != on}})
            
                    
        allColumns = set()
        for row in mergedRows:
            allColumns.update(row.keys())
        
        mergedData = {}
        for col in allColumns:
            mergedData[col] = []
        for row in mergedRows:
            for col in mergedData:
                mergedData[col].append(row[col])

        return DataGrid(mergedData)
    
    def filter(self, predicate):
      filtered_data = {col: [] for col in self.columns}
      for i in range(self.numberOfRows):
          row = {col: self.data[col][i] for col in self.columns}
          if predicate(row):
              for col in self.columns:
                  filtered_data[col].append(self.data[col][i])
      return DataGrid(filtered_data)

    def filter_by_mask(self, mask):
      if len(mask) != self.numberOfRows:
          raise ValueError("Mask length must match number of rows")
      filtered_data = {col: [] for col in self.columns}
      for i, keep in enumerate(mask):
          if keep:
              for col in self.columns:
                  filtered_data[col].append(self.data[col][i])
      return DataGrid(filtered_data)
    
    
    '''def loc(self, predicate, columns=None):
        selected_columns = columns if columns else self.columns
        filtered_data = {col: [] for col in selected_columns}
        for i in range(self.numberOfRows):
            row = {col: self.data[col][i] for col in self.columns}
            if predicate(row):
                for col in selected_columns:
                    filtered_data[col].append(self.data[col][i])
        return DataGrid(filtered_data)'''
    
    def isin(self, column, values):
        return self.filter(lambda row: row[column] in values)
    
    def query(self, expression):
        return self.filter(lambda row: eval(expression, {}, row))
    
    def groupby(self, columns):
        if isinstance(columns, str):
            columns = [columns]
        for c in columns:
            if c not in self.columns:
                raise KeyError(f"Column '{c}' not found")
        return GroupBy(self, columns)
    
    # For chunking - We can remove this is not required, Only added for testing.
    def project(self, selected_columns):
        for col in selected_columns:
            if col not in self.columns:
                raise KeyError(f"Column '{col}' not found in DataGrid")
        return DataGrid({col: self.data[col] for col in selected_columns})

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

