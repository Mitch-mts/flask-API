# Startup utilities for the Flask API

from ServiceFunctions import ServiceFunctions

def print_startup_info():
    """Print dataset information on startup"""
    functions = ServiceFunctions()
    athletesDataSetPath = "./data/Athletes.xlsx"
    
    try:
        print("Dataset shape:", functions.getDataSetShape(athletesDataSetPath))
        print("Dataset unique values:", functions.getUniqueColumnValues(athletesDataSetPath))
    except Exception as e:
        print(f"Error loading dataset: {e}")
