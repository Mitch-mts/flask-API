import pandas as pd
import numpy as np
import seaborn as sn
import matplotlib.pyplot as plt
import plotly.express as px
import warnings
from flask import jsonify

warnings.filterwarnings("ignore")
import os

def getCSVData(dataSetPath):
    return pd.read_csv(dataSetPath)


def getExcelData(dataSetPath):
    return pd.read_excel(dataSetPath)


def getData(dataSetPath):
    """
    Dynamically loads data from a CSV or Excel file based on the file extension in dataSetPath.
    Returns a pandas DataFrame.
    """
    if not isinstance(dataSetPath, str):
        raise ValueError("DataSetPath must be a string representing the file path.")

    _, ext = os.path.splitext(dataSetPath.lower())
    if ext in ['.csv']:
        return getCSVData(dataSetPath)
    elif ext in ['.xls', '.xlsx']:
        return getExcelData(dataSetPath)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


class ServiceFunctions:
    @staticmethod
    def getHeadDataInfo(dataSetPath, numberOfRecords):
        try:
            data = getData(dataSetPath)
            data.head(numberOfRecords)
            return jsonify({
                "data": data
            })
        except Exception as e:
            return jsonify({
                "data": [],
                "message": f"Error: File not found: {dataSetPath}, Reason: {e}"
            })

    @staticmethod
    def getTailDataInfo(dataSetPath, numberOfRecords):
        try:
            data = getData(dataSetPath)
            data.tail(numberOfRecords)
            return jsonify({
                "data": data
            })
        except Exception as e:
            return jsonify({
                "data": [],
                "message": f"Error: File not found: {dataSetPath}, Reason: {e}"
            })

    @staticmethod
    def hello_world():
        return "Hello World!"

    @staticmethod
    def getDataSetShape(dataSetPath):
        try:
            data = getData(dataSetPath)
            return data.shape
        except Exception as e:
            print(f"Error getting dataset shape: {e}")
            return None

    # data set column information
    @staticmethod
    def getColumnInfo(dataSetPath):
        try:
            data = getData(dataSetPath)
            return data.info()
        except Exception as e:
            print(f"Error getting column info: {e}")
            return None

    # data set unique values
    @staticmethod
    def getUniqueColumnValues(dataSetPath, columnName):
        """
        Get unique values from a specific column in the dataset
        
        Args:
            dataSetPath (str): Path to the dataset file
            columnName (str): Name of the column to get unique values from
            
        Returns:
            numpy.ndarray: Array of unique values from the specified column
            None: If an error occurs
        """
        try:
            data = getData(dataSetPath)
            
            # Validate that the column exists
            if columnName not in data.columns:
                print(f"Error: Column '{columnName}' not found in dataset. Available columns: {list(data.columns)}")
                return None
                
            return data[columnName].unique()
        except Exception as e:
            print(f"Error getting unique values from column '{columnName}': {e}")
            return None

    # data set value count for a column
    @staticmethod
    def getColumnValueCount(dataSetPath, columnName):
        """
        Get value counts for a specific column in the dataset
        
        Args:
            dataSetPath (str): Path to the dataset file
            columnName (str): Name of the column to count values for
            
        Returns:
            pandas.Series: Series with value counts for the specified column
            None: If an error occurs
        """
        try:
            data = getData(dataSetPath)
            
            # Validate that the column exists
            if columnName not in data.columns:
                print(f"Error: Column '{columnName}' not found in dataset. Available columns: {list(data.columns)}")
                return None
                
            return data[columnName].value_counts()
        except Exception as e:
            print(f"Error getting column value count for '{columnName}': {e}")
            return None

    # combining columns
    @staticmethod
    def combineDataSetColumns(dataSetPath, column1, column2, separator=" | "):
        """
        Combine two columns from the dataset into a single series
        
        Args:
            dataSetPath (str): Path to the dataset file
            column1 (str): Name of the first column to combine
            column2 (str): Name of the second column to combine
            separator (str): String to use as separator between column values (default: " | ")
            
        Returns:
            pandas.Series: Combined column values as strings
            None: If an error occurs
        """
        try:
            data = getData(dataSetPath)
            
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
    def groupDataByColumnAndCount(dataSetPath, columnName):
        """
        Group data by a specific column and count occurrences
        
        Args:
            dataSetPath (str): Path to the dataset file
            columnName (str): Name of the column to group by
            
        Returns:
            pandas.Series: Count of occurrences for each group
            None: If an error occurs
        """
        try:
            data = getData(dataSetPath)
            
            # Validate that the column exists
            if columnName not in data.columns:
                print(f"Error: Column '{columnName}' not found in dataset. Available columns: {list(data.columns)}")
                return None
                
            return data.groupby(columnName)[columnName].count()
        except Exception as e:
            print(f"Error grouping data by column '{columnName}': {e}")
            return None

    @staticmethod
    def groupDataByTwoColumnsAndCount(dataSetPath, column1, column2):
        """
        Group data by two columns and count occurrences
        
        Args:
            dataSetPath (str): Path to the dataset file
            column1 (str): Name of the first column to group by
            column2 (str): Name of the second column to group by
            
        Returns:
            pandas.Series: Count of occurrences for each group combination
            None: If an error occurs
        """
        try:
            data = getData(dataSetPath)
            
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
    def orderingData(dataSetPath, columns, ascending=True):
        """
        Sort data by specified columns
        
        Args:
            dataSetPath (str): Path to the dataset file
            columns (list or str): Column name(s) to sort by
            ascending (bool): Sort order - True for ascending, False for descending
            
        Returns:
            pandas.DataFrame: Sorted DataFrame
            None: If an error occurs
        """
        try:
            data = getData(dataSetPath)
            
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