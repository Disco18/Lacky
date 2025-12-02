#the backend will be where all the logic happens to make Lacky work
from tkinter import filedialog
import pandas as pd

#Define the size for each transport setup.
# For multi-trailer configs, use list of (rows, cols) tuples: [(A_trailer), (B_trailer), ...]
# Single trailer configs use single tuple (rows, cols)

TRANSPORT_SETUP = {
    "Linehaul B-Double (A+B Trailers)": [(2, 6), (2, 11)],  # A trailer (2x6) + B trailer (2x11)
    "Linehaul Road Train (B+B Trailers)": [(2, 11), (2, 11)],  # B trailer + B trailer
    "Linehaul Semi (B Trailer Only)": (2, 11),
    "Pantech (24)": (1, 12),
    "PUD Truck (14)": (1,7),
    "PUD Truck (14) with Mezz": (2, 7),
    "PUD Truck (16)": (1,8),
    "PUD Truck (16) with Trailer": (1,12),
    "PUD Truck (16) with Trailer and Mezz": (2,12),
    "20FT Shipping Container": (1,5),
    "40FT Shipping Container": (1,10)
}

DG_TYPES = {
    "Explosives": (1),
    "Flammable Gas": (2.1),
    "Non Flammable, Non Toxic": (2.2),
    "Toxic Gas": (2.3),
    "Flammable Liquid": (3),
    "Flammable Solid": (4.1),
    "Spontaneously Combustible": (4.2),
    "Dangerous When Wet": (4.3),
    "Oxidising Agent": (5.1),
    "Organic Peroxide": (5.2),
    "Toxic": (6),
    "Radioactive": (7),
    "Corrosive": (8),
    "Miscellaneous Dangerous Goods": (9)
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