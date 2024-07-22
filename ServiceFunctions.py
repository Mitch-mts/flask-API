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
    def getCsvDataSetInfoForFirstTenRecords(dataSetPath):
        try:
            data = getCSVData(dataSetPath)
            return data.head(10).to_html()
        except Exception as e:
            return f"<p>Error: File not found: , Reason: {e}</p>"

    def getExcelDataSetInfoForFirstTenRecords(dataSetPath):
        try:
            data = getCSVData(dataSetPath)
            return data.head(10).to_html()
        except Exception as e:
            return f"<p>Error: File not found: {dataSetPath}, Reason: {e}</p>"

    def getExcelDataSetInfoForLastTenRecords(dataSetPath):
        try:
            data = getCSVData(dataSetPath)
            return data.tail(10).to_html()
        except Exception as e:
            return f"<p>Error: File not found: {dataSetPath}, Reason: {e}</p>"

    def getCsvDataSetInfo(dataSetPath):
        try:
            data = getCSVData(dataSetPath)
            return data.head().to_html()
        except Exception as e:
            return f"<p>Error: File not found: {dataSetPath}, Reason: {e}</p>"

    def getExcelDataSetInfo(dataSetPath):
        try:
            data = getExcelData(dataSetPath)
            return data.head().to_html()
        except Exception as e:
            return f"<p>Error: File not found: {dataSetPath}, Reason: {e}</p>"

    def hello_world(self):
        print("Hello World!")

    def getDataSetShape(dataSetPath):
        data = getExcelData(dataSetPath)
        return data.shape

    # data set column information
    def getColumnInfo(dataSetPath):
        data = getExcelData(dataSetPath)
        return data.info()

    # data set unique values
    def getUniqueColumnValues(dataSetPath):
        data = getExcelData(dataSetPath)
        return data.NOC.unique()

    # data set value count for a column
    def getColumnValueCount(dataSetPath):
        data = getExcelData(dataSetPath)
        return data.NOC.value_counts()

    # combining columns
    def combineDataSetColumns(dataSetPath):
        data = getExcelData(dataSetPath)
        return data.NOC + " | " + data.Discipline

    # grouping data
    def groupDataByColumnAndCount(dataSetPath):
        data = getExcelData(dataSetPath)
        return data.groupby('NOC').NOC.count()

    def groupDataByTwoColumnsAndCount(dataSetPath):
        data = getExcelData(dataSetPath)
        return data.groupby(['NOC', 'Discipline']).NOC.value_counts()

    # ordering data based on alphabetical order and column specific
    def orderingData(dataSetPath):
        data = getExcelData(dataSetPath)
        return data.sort_values(by=['NOC', 'Discipline'])