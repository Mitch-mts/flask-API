import pandas as pd
import numpy as np
import seaborn as sn
import matplotlib.pyplot as plt
import plotly.express as px
import warnings
from flask import jsonify

warnings.filterwarnings("ignore")
import os
import re

def get_csv_data(data_set_path):
    return pd.read_csv(data_set_path)


def get_excel_data(data_set_path):
    return pd.read_excel(data_set_path)

def rename_column(data, old_column_name, new_column_name):
    renamed_column_data = data.rename(columns={old_column_name: new_column_name})
    return renamed_column_data

def rename_column_names(data, old_column_names, new_column_names):
    """
    Rename multiple columns in a DataFrame.

    Parameters:
    - data: pandas DataFrame
    - old_column_names: list of old column names to be renamed
    - new_column_names: list of new column names corresponding to the old names

    Returns:
    - pandas DataFrame with renamed columns
    """
    if len(old_column_names) != len(new_column_names):
        raise ValueError("The length of old_column_names and new_column_names must be the same.")

    rename_dict = dict(zip(old_column_names, new_column_names))
    renamed_data = data.rename(columns=rename_dict)
    return renamed_data

def combine_data_sets(data1, data2):
    """
    Combine two DataFrames by concatenating them vertically.

    Parameters:
    - data1: First pandas DataFrame
    - data2: Second pandas DataFrame

    Returns:
    - Combined pandas DataFrame
    """
    combined_data = pd.concat([data1, data2], ignore_index=True)
    return combined_data

def median_of_column(data, column_name):
    """
    Calculate the median of a specific column in a DataFrame.

    Parameters:
    - data: pandas DataFrame
    - column_name: Name of the column for which to calculate the median

    Returns:
    - Median value of the specified column
    """
    if column_name not in data.columns:
        raise ValueError(f"Column '{column_name}' not found in the DataFrame.")

    return data.column_name.median()


def get_data(data_set_path):
    """
    Dynamically loads data from a CSV or Excel file based on the file extension in dataSetPath.
    Returns a pandas DataFrame.
    """
    if not isinstance(data_set_path, str):
        raise ValueError("DataSetPath must be a string representing the file path.")

    _, ext = os.path.splitext(data_set_path.lower())
    if ext in ['.csv']:
        return get_csv_data(data_set_path)
    elif ext in ['.xls', '.xlsx']:
        return get_excel_data(data_set_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


class ServiceFunctions:
    @staticmethod
    def get_head_data_info(data_set_path, number_of_records):
        try:
            data = get_data(data_set_path)
            data.head(number_of_records)
            return jsonify({
                "data": data
            })
        except Exception as e:
            return jsonify({
                "data": [],
                "message": f"Error: File not found: {data_set_path}, Reason: {e}"
            })

    @staticmethod
    def get_tail_data_info(data_set_path, number_of_records):
        try:
            data = get_data(data_set_path)
            data.tail(number_of_records)
            return jsonify({
                "data": data
            })
        except Exception as e:
            return jsonify({
                "data": [],
                "message": f"Error: File not found: {data_set_path}, Reason: {e}"
            })

    @staticmethod
    def hello_world():
        return "Hello World!"

    @staticmethod
    def get_data_set_shape(data_set_path):
        try:
            data = get_data(data_set_path)
            return data.shape
        except Exception as e:
            print(f"Error getting dataset shape: {e}")
            return None

    # data set column information
    @staticmethod
    def get_column_info(data_set_path):
        try:
            data = get_data(data_set_path)
            return data.info()
        except Exception as e:
            print(f"Error getting column info: {e}")
            return None

    # data set unique values
    @staticmethod
    def get_unique_column_values(data_set_path, column_name):
        """
        Get unique values from a specific column in the dataset
        
        Args:
            data_set_path (str): Path to the dataset file
            column_name (str): Name of the column to get unique values from
            
        Returns:
            numpy.ndarray: Array of unique values from the specified column
            None: If an error occurs
        """
        try:
            data = get_data(data_set_path)
            
            # Validate that the column exists
            if column_name not in data.columns:
                print(f"Error: Column '{column_name}' not found in dataset. Available columns: {list(data.columns)}")
                return None
                
            return data[column_name].unique()
        except Exception as e:
            print(f"Error getting unique values from column '{column_name}': {e}")
            return None

    # data set value count for a column
    @staticmethod
    def get_column_value_count(data_set_path, column_name):
        """
        Get value counts for a specific column in the dataset
        
        Args:
            data_set_path (str): Path to the dataset file
            column_name (str): Name of the column to count values for
            
        Returns:
            pandas.Series: Series with value counts for the specified column
            None: If an error occurs
        """
        try:
            data = get_data(data_set_path)
            
            # Validate that the column exists
            if column_name not in data.columns:
                print(f"Error: Column '{column_name}' not found in dataset. Available columns: {list(data.columns)}")
                return None
                
            return data.column_name.value_counts()
        except Exception as e:
            print(f"Error getting column value count for '{column_name}': {e}")
            return None

    # combining columns
    @staticmethod
    def combine_data_set_columns(data_set_path, column1, column2, separator=" | "):
        """
        Combine two columns from the dataset into a single series
        
        Args:
            data_set_path (str): Path to the dataset file
            column1 (str): Name of the first column to combine
            column2 (str): Name of the second column to combine
            separator (str): String to use as separator between column values (default: " | ")
            
        Returns:
            pandas.Series: Combined column values as strings
            None: If an error occurs
        """
        try:
            data = get_data(data_set_path)
            
            # Validate that both columns exist
            if column1 not in data.columns:
                print(f"Error: Column '{column1}' not found in dataset. Available columns: {list(data.columns)}")
                return None
            if column2 not in data.columns:
                print(f"Error: Column '{column2}' not found in dataset. Available columns: {list(data.columns)}")
                return None
                
            return data[column1].astype(str) + separator + data[column2].astype(str)
        except Exception as e:
            print(f"Error combining columns '{column1}' and '{column2}': {e}")
            return None

    # grouping data
    @staticmethod
    def group_data_by_column_and_count(data_set_path, column_name):
        """
        Group data by a specific column and count occurrences
        
        Args:
            data_set_path (str): Path to the dataset file
            column_name (str): Name of the column to group by
            
        Returns:
            pandas.Series: Count of occurrences for each group
            None: If an error occurs
        """
        try:
            data = get_data(data_set_path)
            
            # Validate that the column exists
            if column_name not in data.columns:
                print(f"Error: Column '{column_name}' not found in dataset. Available columns: {list(data.columns)}")
                return None
                
            return data.groupby(column_name)[column_name].count()
        except Exception as e:
            print(f"Error grouping data by column '{column_name}': {e}")
            return None

    @staticmethod
    def group_data_by_two_columns_and_count(data_set_path, column1, column2):
        """
        Group data by two columns and count occurrences
        
        Args:
            data_set_path (str): Path to the dataset file
            column1 (str): Name of the first column to group by
            column2 (str): Name of the second column to group by
            
        Returns:
            pandas.Series: Count of occurrences for each group combination
            None: If an error occurs
        """
        try:
            data = get_data(data_set_path)
            
            # Validate that both columns exist
            if column1 not in data.columns:
                print(f"Error: Column '{column1}' not found in dataset. Available columns: {list(data.columns)}")
                return None
            if column2 not in data.columns:
                print(f"Error: Column '{column2}' not found in dataset. Available columns: {list(data.columns)}")
                return None
                
            return data.groupby([column1, column2])[column1].value_counts()
        except Exception as e:
            print(f"Error grouping data by columns '{column1}' and '{column2}': {e}")
            return None

    # ordering data based on alphabetical order and column specific
    @staticmethod
    def ordering_data(data_set_path, columns, ascending=True):
        """
        Sort data by specified columns
        
        Args:
            data_set_path (str): Path to the dataset file
            columns (list or str): Column name(s) to sort by
            ascending (bool): Sort order - True for ascending, False for descending
            
        Returns:
            pandas.DataFrame: Sorted DataFrame
            None: If an error occurs
        """
        try:
            data = get_data(data_set_path)
            
            # Convert single column to list if needed
            if isinstance(columns, str):
                columns = [columns]
            
            # Validate that all columns exist
            for column in columns:
                if column not in data.columns:
                    print(f"Error: Column '{column}' not found in dataset. Available columns: {list(data.columns)}")
                    return None
                    
            return data.sort_values(by=columns, ascending=ascending)
        except Exception as e:
            print(f"Error ordering data by columns {columns}: {e}")
            return None

    # ------------------------------------------------------------------
    # Data Studio inspect helpers
    # These run the same ideas as the file-path methods above, but on an
    # already-loaded DataFrame so the dashboard can open a job's Excel
    # contents and inspect them one method / one row at a time.
    # ------------------------------------------------------------------

    @staticmethod
    def frame_shape(data):
        """Return (row_count, column_count) for the current sheet."""
        return data.shape

    @staticmethod
    def frame_columns(data):
        """Return column names and pandas dtypes as strings."""
        return {
            "columns": [str(column) for column in data.columns],
            "dtypes": {str(column): str(dtype) for column, dtype in data.dtypes.items()},
        }

    @staticmethod
    def frame_head(data, number_of_records=10):
        """First n rows — same intent as get_head_data_info."""
        return data.head(int(number_of_records)).copy()

    @staticmethod
    def frame_tail(data, number_of_records=10):
        """Last n rows — same intent as get_tail_data_info."""
        return data.tail(int(number_of_records)).copy()

    @staticmethod
    def frame_unique_values(data, column_name):
        """Unique values in one column — same as get_unique_column_values."""
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found. Available: {list(data.columns)}")
        return data[column_name].dropna().unique()

    @staticmethod
    def frame_value_counts(data, column_name):
        """How often each value appears — same as get_column_value_count."""
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found. Available: {list(data.columns)}")
        return data[column_name].value_counts(dropna=False)

    @staticmethod
    def frame_group_count(data, column_name):
        """Group by one column and count rows — same as group_data_by_column_and_count."""
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found. Available: {list(data.columns)}")
        return data.groupby(column_name, dropna=False).size().sort_values(ascending=False)

    @staticmethod
    def frame_group_count_two(data, column1, column2):
        """Group by two columns and count rows — same as group_data_by_two_columns_and_count."""
        for column_name in (column1, column2):
            if column_name not in data.columns:
                raise ValueError(f"Column '{column_name}' not found. Available: {list(data.columns)}")
        return data.groupby([column1, column2], dropna=False).size().sort_values(ascending=False)

    @staticmethod
    def frame_sort(data, columns, ascending=True):
        """Sort rows — same as ordering_data."""
        if isinstance(columns, str):
            columns = [columns]
        for column_name in columns:
            if column_name not in data.columns:
                raise ValueError(f"Column '{column_name}' not found. Available: {list(data.columns)}")
        return data.sort_values(by=columns, ascending=ascending)

    @staticmethod
    def frame_combine_columns(data, column1, column2, separator=" | "):
        """Join two columns into one series — same as combine_data_set_columns."""
        for column_name in (column1, column2):
            if column_name not in data.columns:
                raise ValueError(f"Column '{column_name}' not found. Available: {list(data.columns)}")
        return data[column1].astype(str) + separator + data[column2].astype(str)

    @staticmethod
    def frame_median(data, column_name):
        """Median of a numeric column — same as median_of_column."""
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found. Available: {list(data.columns)}")
        return data[column_name].median()

    # ------------------------------------------------------------------
    # Data cleaning — these are the methods Data Studio calls when you
    # tick cleaning steps. apply_cleaning_operations() runs them in order.
    # ------------------------------------------------------------------

    @staticmethod
    def clean_normalize_column_names(data):
        """Lowercase names and replace spaces/hyphens with underscores."""
        renamed = {}
        used = set()
        for column in data.columns:
            name = str(column).strip().lower()
            name = re.sub(r"[^\w]+", "_", name)
            name = re.sub(r"_+", "_", name).strip("_") or "column"
            candidate = name
            index = 2
            while candidate in used:
                candidate = f"{name}_{index}"
                index += 1
            used.add(candidate)
            renamed[column] = candidate
        return data.rename(columns=renamed)

    @staticmethod
    def clean_strip_whitespace(data):
        """Trim text cells and treat blank strings as missing."""
        cleaned = data.copy()
        for column in cleaned.select_dtypes(include=["object", "string"]).columns:
            cleaned[column] = cleaned[column].apply(
                lambda value: value.strip() if isinstance(value, str) else value
            )
            cleaned[column] = cleaned[column].replace("", pd.NA)
        return cleaned

    @staticmethod
    def clean_infer_numeric_types(data):
        """Convert columns that are mostly numeric text into numbers."""
        cleaned = data.copy()
        for column in cleaned.columns:
            if pd.api.types.is_numeric_dtype(cleaned[column]):
                continue
            converted = pd.to_numeric(cleaned[column], errors="coerce")
            original_non_null = cleaned[column].notna().sum()
            converted_non_null = converted.notna().sum()
            if original_non_null and converted_non_null / original_non_null >= 0.8:
                cleaned[column] = converted
        return cleaned

    @staticmethod
    def clean_drop_unnamed_columns(data):
        """Drop leftover Excel index columns such as Unnamed: 0."""
        keep = [
            column for column in data.columns
            if not re.match(r"(?i)^unnamed", str(column).strip())
        ]
        return data.loc[:, keep]

    @staticmethod
    def clean_drop_duplicates(data):
        """Keep the first copy of fully duplicated rows."""
        return data.drop_duplicates().reset_index(drop=True)

    @staticmethod
    def clean_drop_empty_rows(data):
        """Remove rows where every cell is blank."""
        return data.dropna(how="all").reset_index(drop=True)

    @staticmethod
    def clean_drop_missing_rows(data):
        """Remove a row if any column is empty."""
        return data.dropna(how="any").reset_index(drop=True)

    @staticmethod
    def clean_fill_missing(data, strategy="auto"):
        """Fill blanks: mean/median for numbers, mode for text, or ffill."""
        filled = data.copy()
        strategy = (strategy or "auto").lower()
        if strategy == "ffill":
            return filled.ffill()
        for column in filled.columns:
            series = filled[column]
            if not series.isna().any():
                continue
            if strategy == "mode" or (strategy == "auto" and not pd.api.types.is_numeric_dtype(series)):
                mode = series.mode(dropna=True)
                if not mode.empty:
                    filled[column] = series.fillna(mode.iloc[0])
                continue
            if pd.api.types.is_numeric_dtype(series):
                if strategy in ("median", "auto"):
                    filled[column] = series.fillna(series.median())
                elif strategy == "mean":
                    filled[column] = series.fillna(series.mean())
        return filled

    @staticmethod
    def clean_remove_outliers_iqr(data, columns=None):
        """Drop rows outside 1.5 × IQR on numeric columns."""
        cleaned = data.copy()
        target_columns = columns or [
            column for column in cleaned.columns
            if pd.api.types.is_numeric_dtype(cleaned[column])
        ]
        mask = pd.Series(True, index=cleaned.index)
        for column in target_columns:
            if column not in cleaned.columns or not pd.api.types.is_numeric_dtype(cleaned[column]):
                continue
            q1 = cleaned[column].quantile(0.25)
            q3 = cleaned[column].quantile(0.75)
            iqr = q3 - q1
            if pd.isna(iqr) or iqr == 0:
                continue
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask &= cleaned[column].isna() | ((cleaned[column] >= lower) & (cleaned[column] <= upper))
        return cleaned.loc[mask].reset_index(drop=True)

    @staticmethod
    def clean_drop_columns(data, columns=None):
        """Remove selected columns from the sheet."""
        existing = [column for column in (columns or []) if column in data.columns]
        if not existing:
            return data
        return data.drop(columns=existing)

    @staticmethod
    def clean_sort_by(data, columns=None, ascending=True):
        """Sort the sheet by one or more columns."""
        existing = [column for column in (columns or []) if column in data.columns]
        if not existing:
            return data
        return data.sort_values(by=existing, ascending=ascending).reset_index(drop=True)

    @staticmethod
    def apply_cleaning_operations(data, operations):
        """
        Run the cleaning methods the UI selected, in that order.

        Each operation is a dict with `id` matching CLEANING_METHODS,
        plus optional `columns`, `strategy`, and `ascending`.
        """
        cleaned = data.copy()
        applied = []
        methods_by_id = {item["id"]: item for item in CLEANING_METHODS}

        for operation in operations or []:
            name = operation.get("id") or operation.get("name")
            spec = methods_by_id.get(name)
            if spec is None:
                raise ValueError(f"Unknown cleaning method: {name}")

            columns = operation.get("columns") or []
            if isinstance(columns, str):
                columns = [columns]

            before_rows, before_cols = cleaned.shape
            helper = getattr(ServiceFunctions, spec["service_method"])

            if name == "fill_missing":
                cleaned = helper(cleaned, operation.get("strategy", "auto"))
            elif name in ("remove_outliers_iqr", "drop_columns"):
                cleaned = helper(cleaned, columns or None)
            elif name == "sort_by":
                cleaned = helper(cleaned, columns or None, operation.get("ascending", True))
            else:
                cleaned = helper(cleaned)

            applied.append({
                "id": name,
                "label": spec["label"],
                "service_method": spec["service_method"],
                "rows_before": int(before_rows),
                "rows_after": int(cleaned.shape[0]),
                "columns_before": int(before_cols),
                "columns_after": int(cleaned.shape[1]),
            })

        return cleaned, applied


# Catalog used by Data Studio. `service_method` is the ServiceFunctions name that runs.
CLEANING_METHODS = [
    {
        "id": "normalize_column_names",
        "label": "Normalize column names",
        "service_method": "clean_normalize_column_names",
        "description": "Lowercase names and replace spaces or hyphens with underscores.",
        "needs_columns": False,
    },
    {
        "id": "strip_whitespace",
        "label": "Trim text whitespace",
        "service_method": "clean_strip_whitespace",
        "description": "Strip leading and trailing spaces and treat blank cells as missing.",
        "needs_columns": False,
    },
    {
        "id": "infer_numeric_types",
        "label": "Convert number-like text to numbers",
        "service_method": "clean_infer_numeric_types",
        "description": "Turn columns that are mostly numeric text into real numbers.",
        "needs_columns": False,
    },
    {
        "id": "drop_unnamed_columns",
        "label": "Drop unnamed columns",
        "service_method": "clean_drop_unnamed_columns",
        "description": "Remove leftover Excel index columns such as Unnamed: 0.",
        "needs_columns": False,
    },
    {
        "id": "drop_duplicates",
        "label": "Remove duplicate rows",
        "service_method": "clean_drop_duplicates",
        "description": "Keep the first copy of any fully duplicated row.",
        "needs_columns": False,
    },
    {
        "id": "drop_empty_rows",
        "label": "Drop completely empty rows",
        "service_method": "clean_drop_empty_rows",
        "description": "Remove rows where every cell is blank.",
        "needs_columns": False,
    },
    {
        "id": "drop_missing_rows",
        "label": "Drop rows with any missing value",
        "service_method": "clean_drop_missing_rows",
        "description": "Remove a row if any column is empty.",
        "needs_columns": False,
    },
    {
        "id": "fill_missing",
        "label": "Fill missing values",
        "service_method": "clean_fill_missing",
        "description": "Fill blanks using mean or median for numbers and mode for text.",
        "needs_columns": False,
        "options": ["auto", "mean", "median", "mode", "ffill"],
    },
    {
        "id": "remove_outliers_iqr",
        "label": "Remove numeric outliers (IQR)",
        "service_method": "clean_remove_outliers_iqr",
        "description": "Drop rows outside 1.5 × IQR on selected numeric columns.",
        "needs_columns": True,
    },
    {
        "id": "drop_columns",
        "label": "Drop selected columns",
        "service_method": "clean_drop_columns",
        "description": "Remove columns you do not want in the export.",
        "needs_columns": True,
    },
    {
        "id": "sort_by",
        "label": "Sort by column",
        "service_method": "clean_sort_by",
        "description": "Sort the cleaned table by one or more columns.",
        "needs_columns": True,
    },
]