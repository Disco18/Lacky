#the backend will be where all the logic happens to make Lacky work
import sys
import tkinter
import pandas as pd

def importMainfest(filename, sheet_name="Sheet1"):
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