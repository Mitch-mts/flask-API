import pandas as pd
import numpy as np
import seaborn as sn
import matplotlib.pyplot as plt
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")
import os


def getCSVData(dataSetPath):
    return pd.read_csv(dataSetPath)


def getExcelData(dataSetPath):
    return pd.read_excel(dataSetPath)


class ServiceFunctions:
    @staticmethod
    def getCsvDataSetInfoForFirstTenRecords(dataSetPath):
        try:
            data = getCSVData(dataSetPath)
            return data.head(10).to_html()
        except Exception as e:
            return f"<p>Error: File not found: {dataSetPath}, Reason: {e}</p>"

    @staticmethod
    def getExcelDataSetInfoForFirstTenRecords(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.head(10).to_html()
        except Exception as e:
            return f"<p>Error: File not found: {dataSetPath}, Reason: {e}</p>"

    @staticmethod
    def getExcelDataSetInfoForLastTenRecords(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.tail(10).to_html()
        except Exception as e:
            return f"<p>Error: File not found: {dataSetPath}, Reason: {e}</p>"

    @staticmethod
    def getCsvDataSetInfo(dataSetPath):
        try:
            data = getCSVData(dataSetPath)
            return data.head().to_html()
        except Exception as e:
            return f"<p>Error: File not found: {dataSetPath}, Reason: {e}</p>"

    @staticmethod
    def getExcelDataSetInfo(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.head().to_html()
        except Exception as e:
            return f"<p>Error: File not found: {dataSetPath}, Reason: {e}</p>"

    @staticmethod
    def hello_world():
        return "Hello World!"

    @staticmethod
    def getDataSetShape(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.shape
        except Exception as e:
            print(f"Error getting dataset shape: {e}")
            return None

    # data set column information
    @staticmethod
    def getColumnInfo(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.info()
        except Exception as e:
            print(f"Error getting column info: {e}")
            return None

    # data set unique values
    @staticmethod
    def getUniqueColumnValues(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.NOC.unique()
        except Exception as e:
            print(f"Error getting unique values: {e}")
            return None

    # data set value count for a column
    @staticmethod
    def getColumnValueCount(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.NOC.value_counts()
        except Exception as e:
            print(f"Error getting column value count: {e}")
            return None

    # combining columns
    @staticmethod
    def combineDataSetColumns(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.NOC + " | " + data.Discipline
        except Exception as e:
            print(f"Error combining columns: {e}")
            return None

    # grouping data
    @staticmethod
    def groupDataByColumnAndCount(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.groupby('NOC').NOC.count()
        except Exception as e:
            print(f"Error grouping data: {e}")
            return None

    @staticmethod
    def groupDataByTwoColumnsAndCount(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.groupby(['NOC', 'Discipline']).NOC.value_counts()
        except Exception as e:
            print(f"Error grouping data by two columns: {e}")
            return None

    # ordering data based on alphabetical order and column specific
    @staticmethod
    def orderingData(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.sort_values(by=['NOC', 'Discipline'])
        except Exception as e:
            print(f"Error ordering data: {e}")
            return None