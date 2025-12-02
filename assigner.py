import pandas as pd
import math

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

def assign_freight_multi_trailer(data, trailer_dimensions_list, size_constraints):
    """
    Assign freight across multiple trailers (e.g., A+B trailers).
    
    Args:
        data: DataFrame with freight info
        trailer_dimensions_list: List of (rows, cols) tuples, e.g., [(2,6), (2,11)]
        size_constraints: Size constraints (can be shared or per-trailer)
    
    Returns:
        List of trailer grids, each containing (driver_grid, passenger_grid), plus unplaced_freight
        Format: [{"name": "A Trailer", "driver_grid": [[...]], "passenger_grid": [[...]]}, {...}], unplaced_freight
    """
    # Validate required columns
    required_columns = ["id", "length", "depth", "height", "weight"]
    if not all(col in data.columns for col in required_columns):
        print(f"Missing required columns: {set(required_columns) - set(data.columns)}")
        return None
    
    # Sort to prioritize larger/heavier freight
    sorted_data = data.sort_values(by=["height", "weight", "length"], ascending=[False, False, False]).reset_index(drop=True)
    
    trailer_names = ["A Trailer", "B Trailer", "C Trailer", "D Trailer"]  # Extend as needed
    trailers = []
    unplaced_freight = []
    remaining_data = sorted_data.copy()
    
    for idx, (rows, cols) in enumerate(trailer_dimensions_list):
        trailer_name = trailer_names[idx] if idx < len(trailer_names) else f"Trailer {idx+1}"
        
        # Assign freight to this trailer using single-trailer logic
        driver_grid = [["" for _ in range(cols)] for _ in range(rows)]
        passenger_grid = [["" for _ in range(cols)] for _ in range(rows)]

        # Reserved zone: top row, last 3 columns (front). We'll prefer placing tall-heavy, short-length items here.
        
        total_cells = rows * cols * 2
        assigned_data = remaining_data.head(total_cells)
        prefer_driver = True
        
        placed_ids_this_trailer = set()

        # First pass: place tall-heavy short-length items (<=3 cells) into reserved zone on top row
        for _, row in assigned_data.iterrows():
            freight_id = row["id"]
            freight_height = row["height"]
            freight_length = row["length"]
            freight_depth = row["depth"]

            cells_required_length = max(1, math.ceil(freight_length / 1.2))
            cells_required_height = max(1, math.ceil(freight_height / 1.35))
            cells_required_depth = max(1, math.ceil(freight_depth / 1.2))

            if freight_id in placed_ids_this_trailer:
                continue

            if cells_required_height > 1 and cells_required_length <= 3:
                rr = 0  # top row only
                start_cc_max = cols - cells_required_length
                start_cc_min = max(0, cols - 3)

                placed_reserved = False
                # Try cross-side first if needed
                if cells_required_depth > 1:
                    for cc in range(start_cc_max, start_cc_min - 1, -1):
                        if all(
                            all(driver_grid[rr + hh][cc + ll] == "" and passenger_grid[rr + hh][cc + ll] == "" for ll in range(cells_required_length))
                            for hh in range(cells_required_height)
                        ):
                            for hh in range(cells_required_height):
                                for ll in range(cells_required_length):
                                    driver_grid[rr + hh][cc + ll] = freight_id
                                    passenger_grid[rr + hh][cc + ll] = freight_id
                            placed_reserved = True
                            break
                else:
                    # Single-side: try driver then passenger (reserved zone has no mezz, relax constraints)
                    for side_grid in (driver_grid, passenger_grid):
                        if placed_reserved:
                            break
                        for cc in range(start_cc_max, start_cc_min - 1, -1):
                            if all(
                                all(side_grid[rr + hh][cc + ll] == "" for ll in range(cells_required_length))
                                for hh in range(cells_required_height)
                            ):
                                for hh in range(cells_required_height):
                                    for ll in range(cells_required_length):
                                        side_grid[rr + hh][cc + ll] = freight_id
                                placed_reserved = True
                                break

                if placed_reserved:
                    placed_ids_this_trailer.add(freight_id)

        # Second pass: general placement, avoiding reserved zone for all items
        for _, row in assigned_data.iterrows():
            freight_id = row["id"]
            freight_height = row["height"]
            freight_length = row["length"]
            freight_depth = row["depth"]
            
            cells_required_length = max(1, math.ceil(freight_length / 1.2))
            cells_required_height = max(1, math.ceil(freight_height / 1.35))
            cells_required_depth = max(1, math.ceil(freight_depth / 1.2))
            placed = False

            if freight_id in placed_ids_this_trailer:
                placed = True
                prefer_driver = not prefer_driver
                remaining_data = remaining_data[remaining_data["id"] != freight_id]
                continue
            
            # Cross-side placement logic
            if cells_required_depth > 1:
                for rr in range(rows - cells_required_height, -1, -1):
                    if freight_height > 1.35 and rr >= 3 and rr < rows - 3:
                        continue
                    for cc in range(cols - cells_required_length, -1, -1):
                        # Avoid reserved zone (top row, last 3 cols) during general placement
                        if rr == 0 and cc >= cols - 3:
                            continue
                        if all(
                            all(driver_grid[rr + hh][cc + ll] == "" and passenger_grid[rr + hh][cc + ll] == "" for ll in range(cells_required_length))
                            for hh in range(cells_required_height)
                        ):
                            for hh in range(cells_required_height):
                                for ll in range(cells_required_length):
                                    driver_grid[rr + hh][cc + ll] = freight_id
                                    passenger_grid[rr + hh][cc + ll] = freight_id
                            placed = True
                            break
                    if placed:
                        break
            else:
                # Single-side placement
                def try_place(target_grid):
                    for rr in range(rows - cells_required_height, -1, -1):
                        if freight_height > 1.35 and rr >= 3 and rr < rows - 3:
                            continue
                        for cc in range(cols - cells_required_length, -1, -1):
                            # Avoid reserved zone during general placement
                            if rr == 0 and cc >= cols - 3:
                                continue
                            if all(
                                all(target_grid[rr + hh][cc + ll] == "" for ll in range(cells_required_length)) and
                                all(
                                    size_constraints[rr + hh][cc + ll]["height"] >= freight_height and
                                    size_constraints[rr + hh][cc + ll]["depth"] >= freight_depth
                                    for ll in range(cells_required_length)
                                )
                                for hh in range(cells_required_height)
                            ):
                                for hh in range(cells_required_height):
                                    for ll in range(cells_required_length):
                                        target_grid[rr + hh][cc + ll] = freight_id
                                return True
                    return False
                
                if prefer_driver:
                    placed = try_place(driver_grid) or try_place(passenger_grid)
                else:
                    placed = try_place(passenger_grid) or try_place(driver_grid)
            
            prefer_driver = not prefer_driver
            
            if placed:
                # Remove from remaining data
                remaining_data = remaining_data[remaining_data["id"] != freight_id]
            else:
                # Track unplaced for this trailer
                if freight_id not in unplaced_freight:
                    unplaced_freight.append(freight_id)
        
        trailers.append({
            "name": trailer_name,
            "driver_grid": driver_grid,
            "passenger_grid": passenger_grid
        })
        
        print(f"Assigned Freight Grid ({trailer_name} - Driver Side):")
        for row_data in driver_grid:
            print(row_data)
        print(f"Assigned Freight Grid ({trailer_name} - Passenger Side):")
        for row_data in passenger_grid:
            print(row_data)
    
    print("Unplaced Freight:")
    # No sentinel values; print actual unplaced freight only
    for freight in unplaced_freight:
        print(freight)
    
    return trailers, unplaced_freight

def assign_freight(data, grid_dimensions, size_constraints):
    # Check if multi-trailer config (list of tuples) or single trailer (tuple)
    is_multi_trailer = isinstance(grid_dimensions, list)
    
    if is_multi_trailer:
        # Multi-trailer: assign across all trailers
        return assign_freight_multi_trailer(data, grid_dimensions, size_constraints)
    
    # Single trailer logic (existing)
    rows, cols = grid_dimensions
    total_cells = rows * cols * 2

    # Validate required columns
    required_columns = ["id", "length", "depth", "height", "weight"]
    if not all(col in data.columns for col in required_columns):
        print(f"Missing required columns: {set(required_columns) - set(data.columns)}")
        return None

    # Sort to prioritize larger/heavier freight
    sorted_data = data.sort_values(by=["height", "weight", "length"], ascending=[False, False, False]).reset_index(drop=True)

    driver_grid = [["" for _ in range(cols)] for _ in range(rows)]
    passenger_grid = [["" for _ in range(cols)] for _ in range(rows)]

    # Reserved zone: top row, last 3 columns (front). We'll prefer placing tall-heavy, short-length items here.

    assigned_data = sorted_data.head(total_cells)
    unplaced_freight = []

    # Alternate the preferred side per item for balanced fill, with fallback to the other side
    prefer_driver = True

    for _, row in assigned_data.iterrows():
        freight_id = row["id"]
        freight_height = row["height"]
        freight_length = row["length"]
        freight_depth = row["depth"]

        # Use ceiling to avoid under-estimating required cells
        cells_required_length = max(1, math.ceil(freight_length / 1.2))
        cells_required_height = max(1, math.ceil(freight_height / 1.35))
        cells_required_depth = max(1, math.ceil(freight_depth / 1.2))
        placed = False

        # Check if item spans both sides (depth > 1.2m means cells_required_depth > 1)
        if cells_required_depth > 1:
            # Try placing across both driver and passenger grids at the same position
            for rr in range(rows - cells_required_height, -1, -1):
                if freight_height > 1.35 and rr >= 3 and rr < rows - 3:
                    continue
                for cc in range(cols - cells_required_length, -1, -1):
                    # Reserved tall-freight zone: last 3 columns on top row.
                    # Only block these cells for short freight (height fits in one cell).
                    if rr == 0 and cc >= cols - 3 and cells_required_height == 1:
                        print(f"[Single] Skipping short freight {freight_id} in reserved zone")
                        continue
                    # Check if space is available on BOTH sides at the same position (allow tall items to use 'R')
                    if all(
                        all(
                            (driver_grid[rr + hh][cc + ll] == "" or (driver_grid[rr + hh][cc + ll] == "R" and cells_required_height > 1)) and
                            (passenger_grid[rr + hh][cc + ll] == "" or (passenger_grid[rr + hh][cc + ll] == "R" and cells_required_height > 1))
                            for ll in range(cells_required_length)
                        )
                        for hh in range(cells_required_height)
                    ):
                        reserved_hit = any(
                            any(driver_grid[rr + hh][cc + ll] == "R" or passenger_grid[rr + hh][cc + ll] == "R" for ll in range(cells_required_length))
                            for hh in range(cells_required_height)
                        )
                        # Place on both grids
                        for hh in range(cells_required_height):
                            for ll in range(cells_required_length):
                                driver_grid[rr + hh][cc + ll] = freight_id
                                passenger_grid[rr + hh][cc + ll] = freight_id
                        placed = True
                        if reserved_hit:
                            print(f"[Single] Tall freight {freight_id} placed in reserved zone")
                        break
                if placed:
                    break
        else:
            # Item fits on one side only (depth <= 1.2m)
            def try_place(target_grid):
                # returns True if placed
                for rr in range(rows - cells_required_height, -1, -1):
                    if freight_height > 1.35 and rr >= 3 and rr < rows - 3:
                        continue
                    for cc in range(cols - cells_required_length, -1, -1):
                        # Reserved tall-freight zone (top row, last 3 cols) only for tall items; block for short ones.
                        if rr == 0 and cc >= cols - 3 and cells_required_height == 1:
                            print(f"[Single] Skipping short freight {freight_id} in reserved zone")
                            continue
                        if all(
                            all(
                                (target_grid[rr + hh][cc + ll] == "" or (target_grid[rr + hh][cc + ll] == "R" and cells_required_height > 1))
                                for ll in range(cells_required_length)
                            ) and
                            all(
                                size_constraints[rr + hh][cc + ll]["height"] >= freight_height and
                                size_constraints[rr + hh][cc + ll]["depth"] >= freight_depth
                                for ll in range(cells_required_length)
                            )
                            for hh in range(cells_required_height)
                        ):
                            reserved_hit = any(
                                any(target_grid[rr + hh][cc + ll] == "R" for ll in range(cells_required_length))
                                for hh in range(cells_required_height)
                            )
                            for hh in range(cells_required_height):
                                for ll in range(cells_required_length):
                                    target_grid[rr + hh][cc + ll] = freight_id
                            if reserved_hit:
                                print(f"[Single] Tall freight {freight_id} placed in reserved zone")
                            return True
                return False

            # First try the preferred side, then the other side
            if prefer_driver:
                placed = try_place(driver_grid) or try_place(passenger_grid)
            else:
                placed = try_place(passenger_grid) or try_place(driver_grid)

        # Flip preferred side for next item
        prefer_driver = not prefer_driver

        if not placed:
            print(f"Freight ID {freight_id} could not be placed due to size constraints")
            unplaced_freight.append(freight_id)

    print("Assigned Freight Grid (Driver Side):")
    for row in driver_grid:
        print(row)
    print("Assigned Frieght Grid (Passenger Side):")
    for row in passenger_grid:
        print(row)
    print("Unplaced Freight:")
    for freight in unplaced_freight:
        print(freight)

    return driver_grid, passenger_grid, unplaced_freight

def save_load_plan(driver_grid, passenger_grid, unplaced_freight, filepath):
    import json
    save_data = {
        "driver_grid": driver_grid,
        "passenger_grid": passenger_grid,
        "unplaced_freight": unplaced_freight
    }
    with open(filepath, "w") as f:
        json.dump(save_data, f, indent=4)
    print(f"Load plan saved to {filepath}")

def load_load_plan(filepath):
    import json
    with open(filepath, 'r') as f:
        data = json.load(f)
    driver_grid = data.get("driver_grid", [])
    passenger_grid = data.get("passenger_grid", [])
    unplaced_freight = data.get("unplaced_freight",[])
    print(f"Load plan loaded from {filepath}")
    return driver_grid, passenger_grid, unplaced_freight

def reassign_priority_freight(data, driver_grid, passenger_grid, unplaced_freight, priority_ids, size_constraints):
    """
    Attempts to place priority freight items from the unplaced list onto the grids.
    
    Args:
        data: DataFrame containing all freight information
        driver_grid: Current driver side grid
        passenger_grid: Current passenger side grid
        unplaced_freight: List of unplaced freight IDs
        priority_ids: List of freight IDs that have been marked as priority
        size_constraints: Grid size constraints
    
    Returns:
        Updated driver_grid, passenger_grid, unplaced_freight
    """
    if not priority_ids:
        print("No priority items selected for reassignment")
        return driver_grid, passenger_grid, unplaced_freight
    
    rows = len(driver_grid)
    cols = len(driver_grid[0]) if rows > 0 else 0
    
    # Filter data to only priority items that are still unplaced
    priority_items = data[data["id"].isin(priority_ids) & data["id"].isin(unplaced_freight)]
    
    # Sort by size/weight to prioritize larger items first
    priority_items = priority_items.sort_values(by=["height", "weight", "length"], ascending=[False, False, False])
    
    newly_placed = []
    
    for _, row in priority_items.iterrows():
        freight_id = row["id"]
        freight_height = row["height"]
        freight_length = row["length"]
        freight_depth = row["depth"]
        
        # Use ceiling to avoid under-estimating required cells
        cells_required_length = max(1, math.ceil(freight_length / 1.2))
        cells_required_height = max(1, math.ceil(freight_height / 1.35))
        cells_required_depth = max(1, math.ceil(freight_depth / 1.2))
        placed = False
        
        # Check if item spans both sides (depth > 1.2m)
        if cells_required_depth > 1:
            # Try placing across both driver and passenger grids at the same position
            for r in range(rows - cells_required_height, -1, -1):
                if freight_height > 1.35 and r >= 3 and r < rows - 3:
                    continue
                for c in range(cols - cells_required_length, -1, -1):
                    # Avoid reserved zone for non-reserved-pass placements
                    if r == 0 and c >= cols - 3 and (cells_required_height == 1 or cells_required_length > 3):
                        continue
                    # Check if space is available on BOTH sides at the same position
                    if all(
                        all(driver_grid[r + h][c + l] == "" and passenger_grid[r + h][c + l] == "" 
                            for l in range(cells_required_length))
                        for h in range(cells_required_height)
                    ):
                        # Place on both grids
                        for h in range(cells_required_height):
                            for l in range(cells_required_length):
                                driver_grid[r + h][c + l] = freight_id
                                passenger_grid[r + h][c + l] = freight_id
                        placed = True
                        newly_placed.append(freight_id)
                        print(f"Placed priority freight ID {freight_id} across both grids")
                        break
                if placed:
                    break
        else:
            # Try driver grid first for single-side items
            for r in range(rows - cells_required_height, -1, -1):
                if freight_height > 1.35 and r >= 3 and r < rows - 3:
                    continue
                    
                for c in range(cols - cells_required_length, -1, -1):
                    # Avoid reserved zone for non-reserved-pass placements
                    if r == 0 and c >= cols - 3 and (cells_required_height == 1 or cells_required_length > 3):
                        continue
                    if all(
                        all(driver_grid[r + h][c + l] == "" for l in range(cells_required_length)) and
                        all(
                            size_constraints[r + h][c + l]["height"] >= freight_height and
                            size_constraints[r + h][c + l]["depth"] >= freight_depth
                            for l in range(cells_required_length)
                        )
                        for h in range(cells_required_height)
                    ):
                        for h in range(cells_required_height):
                            for l in range(cells_required_length):
                                driver_grid[r + h][c + l] = freight_id
                        placed = True
                        newly_placed.append(freight_id)
                        print(f"Placed priority freight ID {freight_id} on driver grid")
                        break
                if placed:
                    break
            
            # Try passenger grid if not placed on driver
            if not placed:
                for r in range(rows - cells_required_height, -1, -1):
                    if freight_height > 1.35 and r >= 3 and r < rows - 3:
                        continue
                        
                    for c in range(cols - cells_required_length, -1, -1):
                        # Reserved tall-freight zone: block for short freight items
                        if r == 0 and c >= cols - 3 and cells_required_height == 1:
                            continue
                        if all(
                            all(passenger_grid[r + h][c + l] == "" for l in range(cells_required_length)) and
                            all(
                                size_constraints[r + h][c + l]["height"] >= freight_height and
                                size_constraints[r + h][c + l]["depth"] >= freight_depth
                                for l in range(cells_required_length)
                            )
                            for h in range(cells_required_height)
                        ):
                            for h in range(cells_required_height):
                                for l in range(cells_required_length):
                                    passenger_grid[r + h][c + l] = freight_id
                            placed = True
                            newly_placed.append(freight_id)
                            print(f"Placed priority freight ID {freight_id} on passenger grid")
                            break
                    if placed:
                        break
        
        if not placed:
            print(f"Could not place priority freight ID {freight_id} - no space available")
    
    # Remove newly placed items from unplaced_freight list
    unplaced_freight = [item for item in unplaced_freight if item not in newly_placed]
    
    print(f"Reassignment complete: {len(newly_placed)} priority items placed")
    return driver_grid, passenger_grid, unplaced_freight