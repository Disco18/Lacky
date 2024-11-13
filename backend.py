#the backend will be where all the logic happens to make Lacky work
import sys
import tkinter
from tkinter import filedialog
import pandas as pd

#Define the size for each transport setup.

TRANSPORT_SETUP = {
    "Linehaul (A+B Trailers)": (2,11),
    "PUD Truck (14)": (1,7),
    "PUD Truck (14) with Mezz": (2, 7),
    "PUD Truck (16)": (1,8),
    "PUD Truck (16) with Trailer": (1,12),
    "PUD Truck (16) with Trailer and Mezz": (2,12),
    "20FT Shipping Container": (1,5),
    "40FT Shipping Container": (1,10)
}

def importManifest(filename, sheet_name="Sheet1"):
    #This function will import the data from the manifest via spreadsheet.
    try:
        data = pd.read_excel(filename, sheet_name=sheet_name)
        print("Data loaded successfully.")
        return data
    
    except FileNotFoundError:
        print("THe file was not found.")


#def trailerDimenions():
#This function will define the layout and measurements of the trailers in use.
#The name of this function may change.
#Need to create a function for selecting the correct trailers the user wants to use.

#def createLoadPlan():
#Takes the manifest and blends it with the paramaiters to create the ideal load plan.