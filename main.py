from datetime import datetime

class DataGrid:
    def __init__(self, dataDict):
        
        self.columns = list(dataDict.keys())
        self.numberOfRows = max((len(rows) for rows in dataDict.values()), default=0)
        
        for col in self.columns:
            col_data = dataDict[col]
            if len(col_data) < self.numberOfRows:
                col_data += [None] * (self.numberOfRows - len(col_data))
            dataDict[col] = col_data
        self.data = dataDict

    def __getitem__(self, key):
        if isinstance(key, list):
            return DataGrid({col: self.data[col] for col in key})
        else:
            return self.data.get(key, [])

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
        

# def parseCSV(filePath, separator=',', parse_dates=True, auto_detect_separator=False):
def parseCSV(filePath):
    try:
        with open(filePath, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        raise ValueError(f"File not found: {filePath}")

    if not lines:
        raise ValueError("CSV file is empty")

    # if auto_detect_separator:
    #     for sep in [',', ';', '\t', '|']:
    #         if sep in lines[0]:
    #             separator = sep
    #             break

    # columns = lines[0].split(separator)
    columns = lines[0].split(",")
    numberOfColumns = len(columns)
    dataDict = {col: [] for col in columns}
    warnings = []

    for lineNumber, line in enumerate(lines[1:], start=2):
        # values = line.split(separator)
        values = line.split(",")

        if len(values) != numberOfColumns:
            warnings.append(f"Line {lineNumber}: Expected {numberOfColumns} values, got {len(values)}. Skipping.")
            continue

        for i, value in enumerate(values):
            # typedValue = inferType(value, parse_dates=parse_dates)
            typedValue = inferType(value)
            dataDict[columns[i]].append(typedValue)

    if warnings:
        print("Parsing Warnings:")
        for w in warnings:
            print("  -", w)

    return DataGrid(dataDict)

# def inferType(value, parse_dates=True):
def inferType(value):
    value = value.strip()

    if value.lower() in ('', 'null', 'na', 'nan'):
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

