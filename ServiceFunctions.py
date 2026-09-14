import pandas as pd
import numpy as np
import seaborn as sn
import matplotlib.pyplot as plt
import plotly.express as px
import warnings
from flask import jsonify

warnings.filterwarnings("ignore")
import os

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