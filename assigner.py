import pandas as pd

def generate_size_constraints(rows, cols, max_height_limit=2.7, location_length=1.2, location_depth=1.2):
     
    size_constraints = []
    for r in range(rows * 2):  # *2 rows for both sides of the transport config
        row_constraints = []
        for c in range(cols):
            height = 1.35
            depth = location_depth
            length = location_length
            row_constraints.append({"height": height, "length": length, "depth": depth})
        size_constraints.append(row_constraints)
    return size_constraints

def assign_freight(data, grid_dimensions, size_constraints):
        rows, cols = grid_dimensions
        total_cells = rows * cols * 2

        # Checks the data sheet to make sure the required columns exist
        required_columns = ["id", "length", "depth", "height", "weight"]
        if not all(col in data.columns for col in required_columns):
            print(f"Missing required columns: {set(required_columns) - set(data.columns)}")
            return None

         # Sorts data by height, width, and weight to prioritize larger and heavier freight.
        sorted_data = data.sort_values(by=["height", "weight", "length"], ascending=[False, False, False]).reset_index(drop=True)

        driver_grid = [["" for _ in range(cols)] for _ in range(rows)]
        passenger_grid = [["" for _ in range(cols)] for _ in range(rows)]

        assigned_data = sorted_data.head(total_cells)
        selected_driver_grid = True
        unplaced_freight = []
        
        for _, row in assigned_data.iterrows():
            freight_height = row["height"]
            freight_length = row["length"]
            freight_depth = row["depth"]
            
            cells_required_length = max(1, int(freight_length // 1.2))
            cells_required_depth = max(1, int(freight_depth // 1.2))
            cells_required_height = max(1, int(freight_height // 1.35))
            placed = False

            for r in range(rows - cells_required_height, -1, -1):
                if freight_height > 1.35 and r >= 3 and r < rows - 3:
                    continue

                for c in range(cols - cells_required_length, -1, -1):
                    current_grid = driver_grid if selected_driver_grid else passenger_grid

                    if r < 3 and freight_height > 1.35:
                        if r + 1 < rows and current_grid[r + 1][c] == "":
                            current_grid[r + 1][c] = row["id"]
                        else:
                            continue

                    if all(
                        all(current_grid[r + h][c + l] == "" for l in range (cells_required_length)) and
                        all(size_constraints[r + h][c + l]["height"] >= freight_height and
                            size_constraints[r + h][c + l]["length"] >= freight_length and
                            size_constraints[r + h][c + l]["depth"] >= freight_depth
                            for l in range(cells_required_length))
                        for h in range(cells_required_height)
                    ):
                        for h in range(cells_required_height):
                            for l in range(cells_required_length):
                                current_grid[r + h][c + l] = row["id"]
                        placed = True
                        break
                if placed:
                    break

            selected_driver_grid = not selected_driver_grid

            if not placed:
                print(f"Freight ID {row['id']} could not be placed due to size constraints")
                unplaced_freight.append(row["id"])

        print("Assigned Freight Grid (Driver Side):")
        for row in driver_grid:
            print(row)

        print("Assigned Frieght Grid (Passenger Side):")
        for row in passenger_grid:
            print(row)

        print("Unplaced Freight:")
        for freight in unplaced_freight:
            print(freight['id'])

        return driver_grid, passenger_grid, unplaced_freight