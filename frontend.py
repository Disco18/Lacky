from tkinter import *
from tkinter import filedialog, messagebox
import backend 
import assigner as A
from PIL import Image, ImageTk

def open_frontend():
    window = Tk()
    window.title("Lacky v0.1")
    window.state('zoomed')  # Maximize window on Windows
    # For cross-platform compatibility:
    # window.attributes('-zoomed', True)  # For Linux
    # window.state('zoomed')  # For Windows
    # window.attributes('-fullscreen', False)  # Not fullscreen, just maximized

    def open_file_dialog():
        filename = filedialog.askopenfilename(
            title = "Select a file",
            filetypes = [("Excel files", "*.xlsx *.xls")]
        )

        if filename:
            data = backend.importManifest(filename)
            if data is not None:
                choose_transport_setup(data)

    def button_upload_clicked():
        newWindow = Toplevel(window)
        newWindow.title("Upload")
        newWindow.state('zoomed')  # Maximize window
        Label(newWindow, text="Drag and drop .csv file here!").pack()
        newWindow.bind("<Button-1>", lambda event: (open_file_dialog(), newWindow.destroy()))

    """ Tried to intorduce a background image with grid generation """
    """
    def show_manifest_data(data, dimensions):
        rows, cols = dimensions

        win = Toplevel(window)
        win.title("Lacky Manifest")

        # --- Load and centre background ---
        truck_img = Image.open("Lackybackground.png")
        bg_w, bg_h = truck_img.size
        bg_tk = ImageTk.PhotoImage(truck_img)

        canvas = Canvas(win, width=bg_w, height=bg_h)
        canvas.grid(row=0, column=0, sticky="nsew")

        canvas.bg_img = bg_tk
        canvas.create_image(bg_w // 2, bg_h // 2, image=bg_tk)
        
        half_h = bg_h // 2

        cell_w = bg_w / cols
        cell_h = half_h / rows

        # --- Driver side grid (TOP) ---
        driver_grid = []
        for r in range(rows):
            row_cells = []
            for c in range(cols):
                x1 = c * cell_w
                y1 = r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                rect = canvas.create_rectangle(x1, y1, x2, y2, outline="red")
                row_cells.append(rect)
            driver_grid.append(row_cells)

        # --- Passenger side grid (BOTTOM) ---
        passenger_grid = []
        for r in range(rows):
            row_cells = []
            for c in range(cols):
                x1 = c * cell_w
                y1 = half_h + r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                rect = canvas.create_rectangle(x1, y1, x2, y2, outline="blue")
                row_cells.append(rect)
            passenger_grid.append(row_cells)

        
        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(0, weight=1)
        """

    def show_manifest_data(data, grid_dimensions):
        data_window = Toplevel(window)
        data_window.title("Manifest")
        data_window.state('zoomed')  # Maximize window

        # Top title for the generated load plan
        title_label = Label(
            data_window,
            text="Generated Load Plan",
            font=("Arial", 20, "bold"),
            fg="darkorchid4"
        )
        title_label.pack(pady=(10, 0))

        # Check if multi-trailer config
        is_multi_trailer = isinstance(grid_dimensions, list)
        
        if is_multi_trailer:
            # Generate size constraints for the largest trailer
            max_rows = max(r for r, c in grid_dimensions)
            max_cols = max(c for r, c in grid_dimensions)
            size_constraints = A.generate_size_constraints(max_rows, max_cols)
            
            result = A.assign_freight(data, grid_dimensions, size_constraints)
            if result is None:
                return
            
            trailers, A.unplaced_freight = result
            A.trailers = trailers  # Store for reassignment
        else:
            # Single trailer
            rows, cols = grid_dimensions
            size_constraints = A.generate_size_constraints(rows, cols)
            A.driver_grid, A.passenger_grid, A.unplaced_freight = A.assign_freight(data, grid_dimensions, size_constraints)
            print("Grid Dimensions:", rows, "rows,", cols, "cols")

        # Dictionary to track checkbox states: {freight_id: IntVar}
        priority_checkboxes = {}

        if 'id' not in data.columns:
            Label(data_window, text="No 'id' column found in the spreadsheet.").pack()
            return

        # Render grids based on single or multi-trailer
        if is_multi_trailer:
            # Render trailers side-by-side horizontally (A trailer RIGHT/front, B trailer LEFT/rear)
            # Reverse order so first trailer (A) appears on right (front of truck)
            trailers_reversed = list(reversed(trailers))
            max_rows = max(len(t["driver_grid"]) for t in trailers)
            
            # Driver side header
            # Helper function to count cells occupied by each freight ID
            def count_freight_cells(grid):
                """Count how many cells each freight ID occupies in a grid"""
                cell_counts = {}
                for row in grid:
                    for cell_id in row:
                        if cell_id and cell_id != "" and cell_id != "R":
                            cell_counts[cell_id] = cell_counts.get(cell_id, 0) + 1
                return cell_counts
            
            # Helper function to get color based on cell count
            def get_cell_color(cell_id, cell_counts):
                """Return color based on whether freight occupies multiple cells"""
                if not cell_id or cell_id == "" or cell_id == "R":
                    return "lightblue"  # Empty
                count = cell_counts.get(cell_id, 1)
                if count == 1:
                    return "lightgreen"  # Single cell
                elif count == 2:
                    return "#FFD700"  # Gold - 2 cells
                elif count == 3:
                    return "#FFB6C1"  # Light pink - 3 cells
                elif count == 4:
                    return "thistle"  # Thistle - 4 cells
                else:
                    return "#FF0000"  # Red - 5+ cells
            
            driver_header = Frame(data_window, bg="#f5f0ff", highlightbackground="darkorchid4", highlightthickness=2, bd=0)
            driver_header.pack(fill=X, padx=18, pady=(16, 6))
            Label(driver_header, text="Driver Side", font=("Arial", 16, "bold"), fg="darkorchid4", bg="#f5f0ff").pack(fill=X, pady=4)
            
            driver_container = Frame(data_window)
            driver_container.pack(pady=5)
            
            # Render all trailers side-by-side in driver container
            col_offset = 0
            
            for trailer_idx, trailer_info in enumerate(trailers_reversed):
                trailer_name = trailer_info["name"]
                driver_grid = trailer_info["driver_grid"]
                rows = len(driver_grid)
                cols = len(driver_grid[0]) if rows > 0 else 0
                
                # Count cells per freight ID for this trailer
                driver_cell_counts = count_freight_cells(driver_grid)
                
                # Add trailer label above this trailer's section
                trailer_label = Label(
                    driver_container,
                    text=trailer_name,
                    font=("Arial", 10, "bold"),
                    fg="darkorchid4"
                )
                trailer_label.grid(row=0, column=col_offset, columnspan=cols, sticky="ew", padx=2, pady=(0, 5))
                
                # Render grid cells
                for r in range(rows):
                    for c in range(cols):
                        cell_id = driver_grid[r][c]
                        bg_color = get_cell_color(cell_id, driver_cell_counts)
                        label = Label(
                            driver_container,
                            text=cell_id if cell_id else "Empty",
                            width=12,
                            height=5,
                            relief="solid",
                            bg=bg_color
                        )
                        if cell_id:
                            try:
                                row_data = data.loc[data["id"].astype(str) == str(cell_id)].iloc[0].to_dict()
                                add_popup(label, row_data)
                            except IndexError:
                                print(f"No data found for ID: {cell_id}")
                        label.grid(row=r+1, column=col_offset+c, padx=1, pady=1)  # +1 row offset for label
                
                # Add gap spacer after this trailer (except for last trailer)
                if trailer_idx < len(trailers_reversed) - 1:
                    # Create visual gap spacer (half grid square width)
                    gap_spacer = Frame(driver_container, width=60, bg=data_window.cget("bg"))
                    gap_spacer.grid(row=0, column=col_offset+cols, rowspan=rows+1, sticky="ns", padx=0)
                    col_offset += cols + 1  # Move to next trailer position with gap column
                else:
                    col_offset += cols
            
            # Passenger side header
            passenger_header = Frame(data_window, bg="#f5f0ff", highlightbackground="darkorchid4", highlightthickness=2, bd=0)
            passenger_header.pack(fill=X, padx=18, pady=(16, 6))
            Label(passenger_header, text="Passenger Side", font=("Arial", 16, "bold"), fg="darkorchid4", bg="#f5f0ff").pack(fill=X, pady=4)
            
            passenger_container = Frame(data_window)
            passenger_container.pack(pady=5)
            
            # Render all trailers side-by-side in passenger container
            col_offset = 0
            
            for trailer_idx, trailer_info in enumerate(trailers_reversed):
                trailer_name = trailer_info["name"]
                passenger_grid = trailer_info["passenger_grid"]
                rows = len(passenger_grid)
                cols = len(passenger_grid[0]) if rows > 0 else 0
                
                # Count cells per freight ID for this trailer
                passenger_cell_counts = count_freight_cells(passenger_grid)
                
                # Add trailer label above this trailer's section
                trailer_label = Label(
                    passenger_container,
                    text=trailer_name,
                    font=("Arial", 10, "bold"),
                    fg="darkorchid4"
                )
                trailer_label.grid(row=0, column=col_offset, columnspan=cols, sticky="ew", padx=2, pady=(0, 5))
                
                # Render grid cells
                for r in range(rows):
                    for c in range(cols):
                        cell_id = passenger_grid[r][c]
                        bg_color = get_cell_color(cell_id, passenger_cell_counts)
                        label = Label(
                            passenger_container,
                            text=cell_id if cell_id else "Empty",
                            width=12,
                            height=5,
                            relief="solid",
                            bg=bg_color
                        )
                        if cell_id:
                            try:
                                row_data = data.loc[data["id"].astype(str) == str(cell_id)].iloc[0].to_dict()
                                add_popup(label, row_data)
                            except IndexError:
                                print(f"No data found for ID: {cell_id}")
                        label.grid(row=r+1, column=col_offset+c, padx=1, pady=1)  # +1 row offset for label
                
                # Add gap spacer after this trailer (except for last trailer)
                if trailer_idx < len(trailers_reversed) - 1:
                    # Create visual gap spacer (half grid square width)
                    gap_spacer = Frame(passenger_container, width=60, bg=data_window.cget("bg"))
                    gap_spacer.grid(row=0, column=col_offset+cols, rowspan=rows+1, sticky="ns", padx=0)
                    col_offset += cols + 1  # Move to next trailer position with gap column
                else:
                    col_offset += cols
        else:
            # Single trailer rendering
            rows, cols = grid_dimensions
            
            # Helper function to count cells occupied by each freight ID
            def count_freight_cells(grid):
                """Count how many cells each freight ID occupies in a grid"""
                cell_counts = {}
                for row in grid:
                    for cell_id in row:
                        if cell_id and cell_id != "" and cell_id != "R":
                            cell_counts[cell_id] = cell_counts.get(cell_id, 0) + 1
                return cell_counts
            
            # Helper function to get color based on cell count
            def get_cell_color(cell_id, cell_counts):
                """Return color based on whether freight occupies multiple cells"""
                if not cell_id or cell_id == "" or cell_id == "R":
                    return "lightblue"  # Empty
                count = cell_counts.get(cell_id, 1)
                if count == 1:
                    return "lightgreen"  # Single cell
                elif count == 2:
                    return "#FFD700"  # Gold - 2 cells
                elif count == 3:
                    return "#FFB6C1"  # Light pink - 3 cells
                elif count == 4:
                    return "thistle"  # Thistle - 4 cells
                else:
                    return "#FF0000"  # Red - 5+ cells
            
            # Count cells for driver and passenger grids
            driver_cell_counts = count_freight_cells(A.driver_grid)
            passenger_cell_counts = count_freight_cells(A.passenger_grid)
            
            # Section header: Driver Side
            driver_header = Frame(data_window, bg="#f5f0ff", highlightbackground="darkorchid4", highlightthickness=2, bd=0)
            driver_header.pack(fill=X, padx=18, pady=(16, 6))
            Label(driver_header, text="Driver Side", font=("Arial", 16, "bold"), fg="darkorchid4", bg="#f5f0ff").pack(fill=X, pady=4)

            driver_container = Frame(data_window)
            driver_container.pack(pady=5)

            for r in range(rows):
                for c in range(cols):
                    cell_id = A.driver_grid[r][c]
                    bg_color = get_cell_color(cell_id, driver_cell_counts)
                    label = Label(
                        driver_container,
                        text=cell_id if cell_id else "Empty",
                        width=12,
                        height=5,
                        relief="solid",
                        bg=bg_color
                    )
                    if cell_id:
                        try:
                            row_data = data.loc[data["id"].astype(str) == str(cell_id)].iloc[0].to_dict()
                            add_popup(label, row_data)
                        except IndexError:
                            print(f"No data found for ID: {cell_id}")
                    label.grid(row=r, column=c, padx=1, pady=1)

            # Section header: Passenger Side
            passenger_header = Frame(data_window, bg="#f5f0ff", highlightbackground="darkorchid4", highlightthickness=2, bd=0)
            passenger_header.pack(fill=X, padx=18, pady=(16, 6))
            Label(passenger_header, text="Passenger Side", font=("Arial", 16, "bold"), fg="darkorchid4", bg="#f5f0ff").pack(fill=X, pady=4)

            passenger_container = Frame(data_window)
            passenger_container.pack(pady=5)

            for r in range(rows):
                for c in range(cols):
                    cell_id = A.passenger_grid[r][c]
                    bg_color = get_cell_color(cell_id, passenger_cell_counts)
                    label = Label(
                        passenger_container,
                        text=cell_id if cell_id else "Empty",
                        width=12,
                        height=5,
                        relief="solid",
                        bg=bg_color
                    )
                    if cell_id:
                        try:
                            row_data = data.loc[data["id"].astype(str) == str(cell_id)].iloc[0].to_dict()
                            add_popup(label, row_data)
                        except IndexError:
                            print(f"No data found for ID: {cell_id}")
                    label.grid(row=r, column=c, padx=1, pady=1)
        
        # Unplaced freight section (same for both single and multi-trailer)
        unplaced_header = Frame(data_window, bg="#f5f0ff", highlightbackground="darkorchid4", highlightthickness=2, bd=0)
        unplaced_header.pack(fill=X, padx=18, pady=(16, 6))
        Label(unplaced_header, text="Unplaced Freight", font=("Arial", 16, "bold"), fg="darkorchid4", bg="#f5f0ff").pack(fill=X, pady=4)
        
        unplaced_container = Frame(data_window)
        unplaced_container.pack(pady=5, padx=5, fill=X)

        #Unplaced freight list with checkboxes (horizontal layout)
        items_per_row = 3  # Number of items to display per row
        
        # Configure the container's columns to be independent
        for col_idx in range(items_per_row):
            unplaced_container.grid_columnconfigure(col_idx, weight=1, uniform="unplaced")

        for i, item_id in enumerate(A.unplaced_freight):
            row_num = i // items_per_row
            col_num = i % items_per_row

            # Resolve row data for this unplaced freight item
            row_data = None
            try:
                row_data = data.loc[data["id"].astype(str) == str(item_id)].iloc[0]
            except IndexError:
                row_data = None

            # Create a frame for each unplaced freight item
            item_frame = Frame(unplaced_container, relief="solid", borderwidth=1, bg="orchid4")
            item_frame.grid(row=row_num, column=col_num, sticky="ew", padx=5, pady=4)

            # Prioritise checkbox
            var = IntVar()
            priority_checkboxes[item_id] = var  # Store checkbox state
            checkbox = Checkbutton(
                item_frame, 
                variable=var, 
                bg="orchid4", 
                fg="white", 
                text="Prioritise",
                selectcolor="orchid4",
                activebackground="orchid4",
                activeforeground="white"
            )
            checkbox.pack(side=RIGHT, padx=5)

            # Specific information: Name, length, width(depth), height, weight
            name_val = ""
            length_val = ""
            width_val = ""
            height_val = ""
            weight_val = ""

            if row_data is not None:
                name_val = str(row_data.get("name", item_id))
                length_val = str(row_data.get("length", ""))
                width_val = str(row_data.get("depth", ""))  # using 'depth' as width
                height_val = str(row_data.get("height", ""))
                weight_val = str(row_data.get("weight", ""))
            else:
                # Fallback: show only the ID if details aren't available
                name_val = str(item_id)

            # Layout labels horizontally inside the item frame
            Label(item_frame, text=f"Name: {name_val}", bg="orchid4", fg="white", anchor="w", width=18).pack(side=LEFT, padx=4)
            Label(item_frame, text=f"L: {length_val}", bg="orchid4", fg="white", anchor="w", width=8).pack(side=LEFT, padx=2)
            Label(item_frame, text=f"W: {width_val}", bg="orchid4", fg="white", anchor="w", width=8).pack(side=LEFT, padx=2)
            Label(item_frame, text=f"H: {height_val}", bg="orchid4", fg="white", anchor="w", width=8).pack(side=LEFT, padx=2)
            Label(item_frame, text=f"Weight: {weight_val}KG", bg="orchid4", fg="white", anchor="w", width=10).pack(side=LEFT, padx=2)
        
        # Function to handle reassignment
        def reassign_priority_items():
            # Get list of checked freight IDs
            priority_ids = [freight_id for freight_id, var in priority_checkboxes.items() if var.get() == 1]
            
            if not priority_ids:
                messagebox.showinfo("No Selection", "Please select at least one item to prioritise.")
                return
            
            # Call backend reassignment function
            A.driver_grid, A.passenger_grid, A.unplaced_freight = A.reassign_priority_freight(
                data, A.driver_grid, A.passenger_grid, A.unplaced_freight, priority_ids, size_constraints
            )
            
            # Close current window and reopen with updated data
            data_window.destroy()
            show_manifest_data(data, grid_dimensions)
            
            messagebox.showinfo("Reassignment Complete", f"Attempted to place {len(priority_ids)} priority items.")
        
        def save_current_plan():
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")],
                title="Save Load Plan"
            )
            if filepath:
                A.save_load_plan(A.driver_grid, A.passenger_grid, A.unplaced_freight, filepath)
                messagebox.showinfo("Saved", f"Load plan saved successfully!")
        
        def print_load_plan():
            # Placeholder for print functionality
            messagebox.showinfo("Print", "Print functionality coming soon!")
        
        def export_to_excel():
            # Placeholder for Excel export
            messagebox.showinfo("Export", "Excel export functionality coming soon!")
        
        def refresh_view():
            # Refresh the current view
            data_window.destroy()
            show_manifest_data(data, grid_dimensions)
        
        def close_window():
            data_window.destroy()
            # Add the option to cancel if it was accidently clicked.
            # Add confirmation dialog.
        
        # Create button bar frame at the bottom
        button_bar = Frame(data_window, bg="lightgrey", relief="raised", borderwidth=2)
        button_bar.pack(side=BOTTOM, fill=X, pady=10, padx=10)
        
        # Add buttons to the button bar
        if A.unplaced_freight:  # Only show reassign button if there are unplaced items
            Button(
                button_bar, 
                text="Reassign Priority", 
                command=reassign_priority_items,
                bg="alice blue",
                fg="black",
                font=("Arial", 10, "bold"),
                padx=15,
                pady=8
            ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            button_bar, 
            text="Save Plan", 
            command=save_current_plan,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8
        ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            button_bar, 
            text="Print", 
            command=print_load_plan,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8
        ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            button_bar, 
            text="Export to Excel", 
            command=export_to_excel,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8
        ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            button_bar, 
            text="Refresh", 
            command=refresh_view,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8
        ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            button_bar, 
            text="Close", 
            command=close_window,
            bg="darkred",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8
        ).pack(side=RIGHT, padx=5, pady=5)

        Button(
            button_bar, 
            text="Settings", 
            command=settings_window,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8
        ).pack(side=RIGHT, padx=5, pady=5)
    
    def choose_transport_setup(data):
        setup_window = Toplevel(window)
        setup_window.title("Select Transport Setup")
        setup_window.state('zoomed')  # Maximize window

        Label(setup_window, text="Please select a transport setup:").pack(pady=5)
        for setup_name, dimensions in backend.TRANSPORT_SETUP.items():
            btn = Button(
                setup_window,
                text=setup_name,
                command=lambda d=dimensions: [setup_window.destroy(), show_manifest_data(data, d)]
            )
            btn.pack(pady=3)
    
    def settings_window():
        settings_window = Toplevel(window)
        settings_window.title("Settings")
        settings_window.state('zoomed')  # Maximize window

        Label(settings_window, text="Settings window (WIP)").pack(pady=10)

    """
    ######################################################################
    v-- is the start to the save and loading functions in the frontend --v
    """
    def save_load_clicked():
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Save Load Plan"
        )
        if filepath:
            A.save_load_plan(A.driver_grid, A.passenger_grid, A.unplaced_freight, filepath)
    
    def load_load_clicked():
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Open Load Plan"
        )
        if filepath:
            driver_grid, passenger_grid, unplaced_grid = A.load_load_plan(filepath)
            show_loaded_plan(driver_grid,passenger_grid,unplaced_grid)

    def show_loaded_plan(driver_grid, passenger_grid, unplaced_freight):
        data_window = Toplevel(window)
        data_window.title("Loaded Load Plan")

        rows = len(driver_grid)
        cols = len(driver_grid[0]) if rows > 0 else 0

        # Driver side
        Label(data_window, text="Driver Side", font=("Arial", 14, "bold"), fg="darkblue").grid(row=0, column=0, columnspan=cols, pady=10)
        for r in range(rows):
            for c in range(cols):
                cell_id = driver_grid[r][c]
                Label(data_window, text=cell_id if cell_id else "Empty", width=10, height=5, relief="solid", bg="lightgreen" if cell_id else "lightblue").grid(row=r+1, column=c, padx=1, pady=1)

        # Passenger side
        Label(data_window, text="Passenger Side", font=("Arial", 14, "bold"), fg="darkblue").grid(row=rows+2, column=0, columnspan=cols, pady=10)
        for r in range(rows):
            for c in range(cols):
                cell_id = passenger_grid[r][c]
                Label(data_window, text=cell_id if cell_id else "Empty", width=10, height=5, relief="solid", bg="lightgreen" if cell_id else "lightblue").grid(row=r+rows+3, column=c, padx=1, pady=1)

        # Unplaced list
        Label(data_window, text="Unplaced Freight", font=("Arial", 14, "bold"), fg="darkblue").grid(row=2 * rows + 4, column=0, columnspan=cols, pady=10)
        for i, freight_id in enumerate(unplaced_freight):
            Label(data_window, text=str(freight_id), width=10, height=2, relief="solid", bg="salmon").grid(row=2 * rows + 5 + (i // cols), column=i % cols, padx=1, pady=1)

    """
    ^-- is the end to the save and loading functions in the frontend --^
    ######################################################################
    """
    
    #this will display the other details accosiated with the imported data. e.g (length,height,dg ect..)
    #in a pop up window when a populated grid square is hovered over.
    def add_popup(widget, row_data):
        popup = None

        def popup_on(event):
            nonlocal popup
            if popup is not None:
                return
            
            popup = Toplevel(widget)
            popup.title("Information")
            popup.geometry("150x200")
            popup.transient(widget)

            for idx, (col, val) in enumerate(row_data.items()):
                Label(popup, text=f"{col}: {val}", anchor="w").grid(row=idx, column=0, padx=10, pady=2, sticky="w")

            popup.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

        def popup_off(event):
            nonlocal popup
            if popup is not None:
                popup.destroy()
                popup = None
        
        widget.bind("<Enter>", popup_on)
        widget.bind("<Leave>", popup_off)

    """
        ###############################################################################
        v--- Is the start to the visual buttons on the main screen (first window after login) ---v
    """
    sl_label = Label(window, text="Lacky", font=("Ariel", 18, "bold"), fg="darkorchid4" )

    button_settings = Button(window, text="Settings", command=settings_window)
    button_upload = Button(window, text="Upload Spreadsheet", command=button_upload_clicked)
    button_saveload = Button(window, text="Save Load Plan", command=save_load_clicked)
    button_loadload = Button(window, text="Load Load Plan", command=load_load_clicked)
    button_quit = Button(window, text="Quit", command=window.quit)

    sl_label.pack(pady=15)
    button_upload.pack(pady=4)
    button_loadload.pack(pady=4)
    button_saveload.pack(pady=4)
    button_settings.pack(pady=4)
    button_quit.pack(pady=20)

    """
        ^--- Is the end to the visual buttons on the main screen (first window after login) ---^
        ###############################################################################
    """

    def onclick_consignment_data(row_data):
        popup = Toplevel()
        popup.title("Information")

        text= ""
        for key, value in row_data.items():
            text+= f"{key}: {value}\n"

        Label(popup, text=text, justify=LEFT, padx=10, pady=10).pack()

    window.mainloop()