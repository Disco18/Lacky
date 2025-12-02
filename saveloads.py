import json

def save_load(filename, transport_data, driver_grid, passenger_grid, unplaced_freight):
    """
    Saves the transport data, driver grid, passenger grid, and unplaced freight to a JSON file.
    If the file already exists, it loads the data from the file instead.
    """
    data = {
        "transport_data": transport_data,
        "driver_grid": driver_grid,
        "passenger_grid": passenger_grid,
        "unplaced_freight": unplaced_freight
    }
    with open(filename, 'r') as file:
        json.dump(data, file, indent = 4)
        # If the file exists, load the data from it
        print(f"Data loaded from {filename}")
        

def load_load(filename):
    """
    Loads the transport data, driver grid, passenger grid, and unplaced freight from a JSON file.
    """
    try:
     with open(filename, 'r') as file:
        data = json.load(file)
        return (
            tuple(data["transport_data"]),
            data["driver_grid"],
            data["passenger_grid"],
            data["unplaced_freight"]    
        )
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None, None, None, None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {filename}.")
        return None, None, None, None