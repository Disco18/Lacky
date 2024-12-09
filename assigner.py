import frontend
import pandas as pd

def generate_size_constraints(rows, cols, max_height_rows=3, max_height_limit=2.7, location_width=1.2, location_depth=1.2):
     
    size_constraints = []
    for r in range(rows * 2):  # *2 rows for both sides of the transport config
        row_constraints = []
        for c in range(cols):
            height = max_height_limit if r < max_height_rows or r >= rows + max_height_rows else 2.5
            row_constraints.append({"height": height, "width": location_width, "depth": location_depth})
        size_constraints.append(row_constraints)
    return size_constraints

def assign_freight(data, grid_dimensions, size_constraints):
        rows, cols = grid_dimensions
        total_cells = rows * cols * 2

        required_columns = ["id", "length", "width", "height", "weight"]
        if not all(col in data.columns for col in required_columns):
            print(f"Missing required columns: {set(required_columns) - set(data.columns)}")
            return None

         # Sorts data by height, width, and weight to prioritize larger and heavier freight.
        sorted_data = data.sort_values(by=["height", "width", "weight"], ascending=[False, False, False]).reset_index(drop=True)

        grid = [["" for _ in range(cols)] for _ in range(rows * 2)]

        for _, row in sorted_data.iterrows():
            placed = False
            required_width_cells = int(-(-row["width"] // size_constraints[0][0]["width"]))  # Number of columns needed
            required_depth_cells = int(-(-row["depth"] // size_constraints[0][0]["depth"]))  # Number of rows needed

            for r in range(rows * 2 - required_depth_cells + 1):  # Ensure space for required depth
                for c in range(cols - required_width_cells + 1):  # Ensure space for required width
                    # Check if the freight fits within the constraints for all required cells
                    if all(
                        grid[r + dr][c + dc] == ""  # Ensure cells are empty
                        and size_constraints[r + dr][c + dc]["height"] >= row["height"]
                        for dr in range(required_depth_cells)
                        for dc in range(required_width_cells)
                    ):
                        # Allocate the freight to the required spaces
                        for dr in range(required_depth_cells):
                            for dc in range(required_width_cells):
                                grid[r + dr][c + dc] = str(row["id"])
                        placed = True
                        break
                if placed:
                    break

            if not placed:
                print(f"Freight ID {row['id']} could not be placed.")
        
        print("Assigned Freight Grid:")
        for row in grid:
            print(row)

        return grid