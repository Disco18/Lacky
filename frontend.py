from tkinter import *
from tkinter import filedialog, messagebox

import backend
import assigner as A


def open_frontend():
    window = Tk()
    window.title("Lacky v0.1")
    window.state("zoomed")

    app_state = {
        "data": None,
        "grid_dimensions": None,
        "is_multi_trailer": False,
        "size_constraints": None,
        "trailers": [],
        "driver_grid": [],
        "passenger_grid": [],
        "unplaced_freight": [],
    }

    content_frame = Frame(window)
    content_frame.pack(fill=BOTH, expand=True)

    def clear_content():
        for child in content_frame.winfo_children():
            child.destroy()

    def has_active_single_plan():
        return (
            not app_state["is_multi_trailer"]
            and bool(app_state["driver_grid"])
            and bool(app_state["passenger_grid"])
        )

    def count_freight_cells(grid):
        cell_counts = {}
        for row in grid:
            for cell_id in row:
                if cell_id and cell_id != "" and cell_id != "R":
                    cell_counts[cell_id] = cell_counts.get(cell_id, 0) + 1
        return cell_counts

    def get_cell_color(cell_id, cell_counts):
        if not cell_id or cell_id == "" or cell_id == "R":
            return "lightblue"
        count = cell_counts.get(cell_id, 1)
        if count == 1:
            return "lightgreen"
        if count == 2:
            return "#FFD700"
        if count == 3:
            return "#FFB6C1"
        if count == 4:
            return "thistle"
        return "#FF0000"

    def render_home():
        clear_content()

        wrapper = Frame(content_frame)
        wrapper.pack(fill=BOTH, expand=True)

        sl_label = Label(wrapper, text="Lacky", font=("Ariel", 18, "bold"), fg="darkorchid4")
        button_settings = Button(wrapper, text="Settings", command=settings_view)
        button_upload = Button(wrapper, text="Upload Spreadsheet", command=button_upload_clicked)
        button_saveload = Button(wrapper, text="Save Load Plan", command=save_load_clicked)
        button_loadload = Button(wrapper, text="Load Load Plan", command=load_load_clicked)
        button_quit = Button(wrapper, text="Quit", command=window.quit)

        sl_label.pack(pady=15)
        button_upload.pack(pady=4)
        button_loadload.pack(pady=4)
        button_saveload.pack(pady=4)
        button_settings.pack(pady=4)
        button_quit.pack(pady=20)

    def open_file_dialog():
        filename = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("Excel files", "*.xlsx *.xls")],
        )

        if not filename:
            return

        data = backend.importManifest(filename)
        if data is None:
            return

        app_state["data"] = data
        choose_transport_setup(data)

    def button_upload_clicked():
        open_file_dialog()

    def choose_transport_setup(data):
        clear_content()

        setup_frame = Frame(content_frame)
        setup_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        Label(setup_frame, text="Please select a transport setup:", font=("Arial", 14, "bold")).pack(pady=10)

        for setup_name, dimensions in backend.TRANSPORT_SETUP.items():
            Button(
                setup_frame,
                text=setup_name,
                command=lambda d=dimensions: show_manifest_data(data, d),
            ).pack(pady=3)

        Button(setup_frame, text="Back", command=render_home).pack(pady=20)

    def show_manifest_data(data, grid_dimensions):
        clear_content()

        manifest_frame = Frame(content_frame)
        manifest_frame.pack(fill=BOTH, expand=True)

        selected_cell = {"widget": None}

        title_label = Label(
            manifest_frame,
            text="Generated Load Plan",
            font=("Arial", 20, "bold"),
            fg="darkorchid4",
        )
        title_label.pack(pady=(10, 0))

        content_area = Frame(manifest_frame)
        content_area.pack(fill=BOTH, expand=True)

        plan_area = Frame(content_area)
        plan_area.pack(side=LEFT, fill=BOTH, expand=True)

        side_panel = Frame(
            content_area,
            width=320,
            bg="#f5f0ff",
            highlightbackground="darkorchid4",
            highlightthickness=2,
            bd=0,
        )
        side_panel.pack(side=RIGHT, fill=Y, padx=(8, 18), pady=(16, 8))
        side_panel.pack_propagate(False)

        Label(
            side_panel,
            text="Freight Details",
            font=("Arial", 14, "bold"),
            fg="darkorchid4",
            bg="#f5f0ff",
        ).pack(fill=X, pady=(8, 4))

        detail_body = Frame(side_panel, bg="#f5f0ff")
        detail_body.pack(fill=BOTH, expand=True, padx=10, pady=8)

        def render_detail_panel(row_data=None):
            for child in detail_body.winfo_children():
                child.destroy()

            if row_data is None:
                Label(
                    detail_body,
                    text="Click an allocated freight cell\nto view details.",
                    justify=LEFT,
                    anchor="nw",
                    bg="#f5f0ff",
                    fg="gray30",
                    font=("Arial", 10),
                ).pack(fill=BOTH, expand=True, anchor="nw")
                return

            for col, val in row_data.items():
                Label(
                    detail_body,
                    text=f"{col}: {val}",
                    anchor="w",
                    justify=LEFT,
                    bg="#f5f0ff",
                    wraplength=280,
                ).pack(fill=X, pady=2, anchor="w")

        def bind_inline_details(widget, row_data):
            def show_details(_event=None):
                if selected_cell["widget"] is not None and selected_cell["widget"] != widget:
                    selected_cell["widget"].configure(highlightthickness=0)

                widget.configure(highlightbackground="darkorchid4", highlightthickness=2)
                selected_cell["widget"] = widget
                render_detail_panel(row_data)

            widget.bind("<Button-1>", show_details)

        render_detail_panel()

        if "id" not in data.columns:
            Label(manifest_frame, text="No 'id' column found in the spreadsheet.").pack(pady=15)
            Button(manifest_frame, text="Back", command=lambda: choose_transport_setup(data)).pack(pady=10)
            return

        is_multi_trailer = isinstance(grid_dimensions, list)
        app_state["is_multi_trailer"] = is_multi_trailer
        app_state["grid_dimensions"] = grid_dimensions
        app_state["data"] = data

        if is_multi_trailer:
            max_rows = max(r for r, c in grid_dimensions)
            max_cols = max(c for r, c in grid_dimensions)
            size_constraints = A.generate_size_constraints(max_rows, max_cols)
            result = A.assign_freight(data, grid_dimensions, size_constraints)

            if result is None:
                messagebox.showerror("Assignment Error", "Could not assign freight for this manifest.")
                choose_transport_setup(data)
                return

            if len(result) != 2:
                messagebox.showerror("Assignment Error", "Unexpected multi-trailer assignment result format.")
                choose_transport_setup(data)
                return

            trailers, unplaced_freight = result
            app_state["trailers"] = trailers
            app_state["unplaced_freight"] = unplaced_freight
            app_state["size_constraints"] = size_constraints
            app_state["driver_grid"] = []
            app_state["passenger_grid"] = []
        else:
            rows, cols = grid_dimensions
            size_constraints = A.generate_size_constraints(rows, cols)
            result = A.assign_freight(data, grid_dimensions, size_constraints)

            if result is None:
                messagebox.showerror("Assignment Error", "Could not assign freight for this manifest.")
                choose_transport_setup(data)
                return

            if len(result) != 3:
                messagebox.showerror("Assignment Error", "Unexpected single-trailer assignment result format.")
                choose_transport_setup(data)
                return

            driver_grid, passenger_grid, unplaced_freight = result
            app_state["driver_grid"] = driver_grid
            app_state["passenger_grid"] = passenger_grid
            app_state["unplaced_freight"] = unplaced_freight
            app_state["size_constraints"] = size_constraints
            app_state["trailers"] = []

        priority_checkboxes = {}

        if app_state["is_multi_trailer"]:
            trailers_reversed = list(reversed(app_state["trailers"]))

            driver_header = Frame(
                plan_area,
                bg="#f5f0ff",
                highlightbackground="darkorchid4",
                highlightthickness=2,
                bd=0,
            )
            driver_header.pack(fill=X, padx=18, pady=(16, 6))
            Label(
                driver_header,
                text="Driver Side",
                font=("Arial", 16, "bold"),
                fg="darkorchid4",
                bg="#f5f0ff",
            ).pack(fill=X, pady=4)

            driver_container = Frame(plan_area)
            driver_container.pack(pady=5)

            col_offset = 0
            for trailer_idx, trailer_info in enumerate(trailers_reversed):
                trailer_name = trailer_info["name"]
                driver_grid = trailer_info["driver_grid"]
                rows = len(driver_grid)
                cols = len(driver_grid[0]) if rows > 0 else 0
                driver_cell_counts = count_freight_cells(driver_grid)

                trailer_label = Label(
                    driver_container,
                    text=trailer_name,
                    font=("Arial", 10, "bold"),
                    fg="darkorchid4",
                )
                trailer_label.grid(row=0, column=col_offset, columnspan=cols, sticky="ew", padx=2, pady=(0, 5))

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
                            bg=bg_color,
                        )
                        if cell_id and cell_id != "R":
                            try:
                                row_data = data.loc[data["id"].astype(str) == str(cell_id)].iloc[0].to_dict()
                                bind_inline_details(label, row_data)
                            except IndexError:
                                print(f"No data found for ID: {cell_id}")
                        label.grid(row=r + 1, column=col_offset + c, padx=1, pady=1)

                if trailer_idx < len(trailers_reversed) - 1:
                    gap_spacer = Frame(driver_container, width=60, bg=plan_area.cget("bg"))
                    gap_spacer.grid(row=0, column=col_offset + cols, rowspan=rows + 1, sticky="ns", padx=0)
                    col_offset += cols + 1
                else:
                    col_offset += cols

            passenger_header = Frame(
                plan_area,
                bg="#f5f0ff",
                highlightbackground="darkorchid4",
                highlightthickness=2,
                bd=0,
            )
            passenger_header.pack(fill=X, padx=18, pady=(16, 6))
            Label(
                passenger_header,
                text="Passenger Side",
                font=("Arial", 16, "bold"),
                fg="darkorchid4",
                bg="#f5f0ff",
            ).pack(fill=X, pady=4)

            passenger_container = Frame(plan_area)
            passenger_container.pack(pady=5)

            col_offset = 0
            for trailer_idx, trailer_info in enumerate(trailers_reversed):
                trailer_name = trailer_info["name"]
                passenger_grid = trailer_info["passenger_grid"]
                rows = len(passenger_grid)
                cols = len(passenger_grid[0]) if rows > 0 else 0
                passenger_cell_counts = count_freight_cells(passenger_grid)

                trailer_label = Label(
                    passenger_container,
                    text=trailer_name,
                    font=("Arial", 10, "bold"),
                    fg="darkorchid4",
                )
                trailer_label.grid(row=0, column=col_offset, columnspan=cols, sticky="ew", padx=2, pady=(0, 5))

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
                            bg=bg_color,
                        )
                        if cell_id and cell_id != "R":
                            try:
                                row_data = data.loc[data["id"].astype(str) == str(cell_id)].iloc[0].to_dict()
                                bind_inline_details(label, row_data)
                            except IndexError:
                                print(f"No data found for ID: {cell_id}")
                        label.grid(row=r + 1, column=col_offset + c, padx=1, pady=1)

                if trailer_idx < len(trailers_reversed) - 1:
                    gap_spacer = Frame(passenger_container, width=60, bg=plan_area.cget("bg"))
                    gap_spacer.grid(row=0, column=col_offset + cols, rowspan=rows + 1, sticky="ns", padx=0)
                    col_offset += cols + 1
                else:
                    col_offset += cols
        else:
            rows, cols = app_state["grid_dimensions"]

            driver_cell_counts = count_freight_cells(app_state["driver_grid"])
            passenger_cell_counts = count_freight_cells(app_state["passenger_grid"])

            driver_header = Frame(
                plan_area,
                bg="#f5f0ff",
                highlightbackground="darkorchid4",
                highlightthickness=2,
                bd=0,
            )
            driver_header.pack(fill=X, padx=18, pady=(16, 6))
            Label(
                driver_header,
                text="Driver Side",
                font=("Arial", 16, "bold"),
                fg="darkorchid4",
                bg="#f5f0ff",
            ).pack(fill=X, pady=4)

            driver_container = Frame(plan_area)
            driver_container.pack(pady=5)

            for r in range(rows):
                for c in range(cols):
                    cell_id = app_state["driver_grid"][r][c]
                    bg_color = get_cell_color(cell_id, driver_cell_counts)
                    label = Label(
                        driver_container,
                        text=cell_id if cell_id else "Empty",
                        width=12,
                        height=5,
                        relief="solid",
                        bg=bg_color,
                    )
                    if cell_id and cell_id != "R":
                        try:
                            row_data = data.loc[data["id"].astype(str) == str(cell_id)].iloc[0].to_dict()
                            bind_inline_details(label, row_data)
                        except IndexError:
                            print(f"No data found for ID: {cell_id}")
                    label.grid(row=r, column=c, padx=1, pady=1)

            passenger_header = Frame(
                plan_area,
                bg="#f5f0ff",
                highlightbackground="darkorchid4",
                highlightthickness=2,
                bd=0,
            )
            passenger_header.pack(fill=X, padx=18, pady=(16, 6))
            Label(
                passenger_header,
                text="Passenger Side",
                font=("Arial", 16, "bold"),
                fg="darkorchid4",
                bg="#f5f0ff",
            ).pack(fill=X, pady=4)

            passenger_container = Frame(plan_area)
            passenger_container.pack(pady=5)

            for r in range(rows):
                for c in range(cols):
                    cell_id = app_state["passenger_grid"][r][c]
                    bg_color = get_cell_color(cell_id, passenger_cell_counts)
                    label = Label(
                        passenger_container,
                        text=cell_id if cell_id else "Empty",
                        width=12,
                        height=5,
                        relief="solid",
                        bg=bg_color,
                    )
                    if cell_id and cell_id != "R":
                        try:
                            row_data = data.loc[data["id"].astype(str) == str(cell_id)].iloc[0].to_dict()
                            bind_inline_details(label, row_data)
                        except IndexError:
                            print(f"No data found for ID: {cell_id}")
                    label.grid(row=r, column=c, padx=1, pady=1)

        unplaced_header = Frame(
            plan_area,
            bg="#f5f0ff",
            highlightbackground="darkorchid4",
            highlightthickness=2,
            bd=0,
        )
        unplaced_header.pack(fill=X, padx=18, pady=(16, 6))
        Label(
            unplaced_header,
            text="Unplaced Freight",
            font=("Arial", 16, "bold"),
            fg="darkorchid4",
            bg="#f5f0ff",
        ).pack(fill=X, pady=4)

        unplaced_container = Frame(plan_area)
        unplaced_container.pack(pady=5, padx=5, fill=X)

        items_per_row = 3
        for col_idx in range(items_per_row):
            unplaced_container.grid_columnconfigure(col_idx, weight=1, uniform="unplaced")

        for i, item_id in enumerate(app_state["unplaced_freight"]):
            row_num = i // items_per_row
            col_num = i % items_per_row

            row_data = None
            try:
                row_data = data.loc[data["id"].astype(str) == str(item_id)].iloc[0]
            except IndexError:
                row_data = None

            item_frame = Frame(unplaced_container, relief="solid", borderwidth=1, bg="orchid4")
            item_frame.grid(row=row_num, column=col_num, sticky="ew", padx=5, pady=4)

            var = IntVar()
            priority_checkboxes[item_id] = var
            checkbox = Checkbutton(
                item_frame,
                variable=var,
                bg="orchid4",
                fg="white",
                text="Prioritise",
                selectcolor="orchid4",
                activebackground="orchid4",
                activeforeground="white",
            )
            checkbox.pack(side=RIGHT, padx=5)

            name_val = ""
            length_val = ""
            width_val = ""
            height_val = ""
            weight_val = ""

            if row_data is not None:
                name_val = str(row_data.get("name", item_id))
                length_val = str(row_data.get("length", ""))
                width_val = str(row_data.get("depth", ""))
                height_val = str(row_data.get("height", ""))
                weight_val = str(row_data.get("weight", ""))
            else:
                name_val = str(item_id)

            Label(item_frame, text=f"Name: {name_val}", bg="orchid4", fg="white", anchor="w", width=18).pack(
                side=LEFT, padx=4
            )
            Label(item_frame, text=f"L: {length_val}", bg="orchid4", fg="white", anchor="w", width=8).pack(
                side=LEFT, padx=2
            )
            Label(item_frame, text=f"W: {width_val}", bg="orchid4", fg="white", anchor="w", width=8).pack(
                side=LEFT, padx=2
            )
            Label(item_frame, text=f"H: {height_val}", bg="orchid4", fg="white", anchor="w", width=8).pack(
                side=LEFT, padx=2
            )
            Label(item_frame, text=f"Weight: {weight_val}KG", bg="orchid4", fg="white", anchor="w", width=10).pack(
                side=LEFT, padx=2
            )

        def reassign_priority_items():
            priority_ids = [freight_id for freight_id, var in priority_checkboxes.items() if var.get() == 1]

            if not priority_ids:
                messagebox.showinfo("No Selection", "Please select at least one item to prioritise.")
                return

            if app_state["is_multi_trailer"]:
                messagebox.showinfo(
                    "Not Supported",
                    "Reassign Priority is currently available only for single-trailer plans.",
                )
                return

            driver_grid, passenger_grid, unplaced = A.reassign_priority_freight(
                data,
                app_state["driver_grid"],
                app_state["passenger_grid"],
                app_state["unplaced_freight"],
                priority_ids,
                app_state["size_constraints"],
            )

            app_state["driver_grid"] = driver_grid
            app_state["passenger_grid"] = passenger_grid
            app_state["unplaced_freight"] = unplaced

            show_manifest_from_state()
            messagebox.showinfo("Reassignment Complete", f"Attempted to place {len(priority_ids)} priority items.")

        def save_current_plan():
            if app_state["is_multi_trailer"]:
                messagebox.showinfo(
                    "Not Supported",
                    "Save Plan currently supports single-trailer generated plans and loaded plans.",
                )
                return

            if not has_active_single_plan():
                messagebox.showinfo("No Plan", "No single-trailer plan is currently available to save.")
                return

            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")],
                title="Save Load Plan",
            )
            if filepath:
                A.save_load_plan(
                    app_state["driver_grid"], app_state["passenger_grid"], app_state["unplaced_freight"], filepath
                )
                messagebox.showinfo("Saved", "Load plan saved successfully!")

        def print_load_plan():
            messagebox.showinfo("Print", "Print functionality coming soon!")

        def export_to_excel():
            messagebox.showinfo("Export", "Excel export functionality coming soon!")

        def refresh_view():
            if app_state["data"] is None or app_state["grid_dimensions"] is None:
                render_home()
                return
            show_manifest_data(app_state["data"], app_state["grid_dimensions"])

        button_bar = Frame(manifest_frame, bg="lightgrey", relief="raised", borderwidth=2)
        button_bar.pack(side=BOTTOM, fill=X, pady=10, padx=10)

        if app_state["unplaced_freight"] and not app_state["is_multi_trailer"]:
            Button(
                button_bar,
                text="Reassign Priority",
                command=reassign_priority_items,
                bg="alice blue",
                fg="black",
                font=("Arial", 10, "bold"),
                padx=15,
                pady=8,
            ).pack(side=LEFT, padx=5, pady=5)

        Button(
            button_bar,
            text="Save Plan",
            command=save_current_plan,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
        ).pack(side=LEFT, padx=5, pady=5)

        Button(
            button_bar,
            text="Print",
            command=print_load_plan,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
        ).pack(side=LEFT, padx=5, pady=5)

        Button(
            button_bar,
            text="Export to Excel",
            command=export_to_excel,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
        ).pack(side=LEFT, padx=5, pady=5)

        Button(
            button_bar,
            text="Refresh",
            command=refresh_view,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
        ).pack(side=LEFT, padx=5, pady=5)

        Button(
            button_bar,
            text="Home",
            command=render_home,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
        ).pack(side=RIGHT, padx=5, pady=5)

        Button(
            button_bar,
            text="Settings",
            command=settings_view,
            bg="alice blue",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
        ).pack(side=RIGHT, padx=5, pady=5)

    def show_manifest_from_state():
        if app_state["data"] is None or app_state["grid_dimensions"] is None:
            render_home()
            return
        show_manifest_data(app_state["data"], app_state["grid_dimensions"])

    def save_load_clicked():
        if app_state["is_multi_trailer"]:
            messagebox.showinfo(
                "Not Supported",
                "Save Load Plan currently supports single-trailer generated plans and loaded plans.",
            )
            return

        if not has_active_single_plan():
            messagebox.showinfo("No Plan", "Generate or load a single-trailer plan first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Save Load Plan",
        )
        if filepath:
            A.save_load_plan(app_state["driver_grid"], app_state["passenger_grid"], app_state["unplaced_freight"], filepath)
            messagebox.showinfo("Saved", "Load plan saved successfully!")

    def load_load_clicked():
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Open Load Plan",
        )
        if not filepath:
            return

        driver_grid, passenger_grid, unplaced_grid = A.load_load_plan(filepath)
        app_state["driver_grid"] = driver_grid
        app_state["passenger_grid"] = passenger_grid
        app_state["unplaced_freight"] = unplaced_grid
        app_state["is_multi_trailer"] = False
        app_state["data"] = None
        app_state["grid_dimensions"] = None
        show_loaded_plan(driver_grid, passenger_grid, unplaced_grid)

    def show_loaded_plan(driver_grid, passenger_grid, unplaced_freight):
        clear_content()

        data_frame = Frame(content_frame)
        data_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        rows = len(driver_grid)
        cols = len(driver_grid[0]) if rows > 0 else 0

        Label(data_frame, text="Loaded Load Plan", font=("Arial", 18, "bold"), fg="darkorchid4").grid(
            row=0, column=0, columnspan=max(cols, 1), pady=(0, 12)
        )

        Label(data_frame, text="Driver Side", font=("Arial", 14, "bold"), fg="darkblue").grid(
            row=1, column=0, columnspan=max(cols, 1), pady=10
        )
        for r in range(rows):
            for c in range(cols):
                cell_id = driver_grid[r][c]
                Label(
                    data_frame,
                    text=cell_id if cell_id else "Empty",
                    width=10,
                    height=5,
                    relief="solid",
                    bg="lightgreen" if cell_id else "lightblue",
                ).grid(row=r + 2, column=c, padx=1, pady=1)

        passenger_start = rows + 3
        Label(data_frame, text="Passenger Side", font=("Arial", 14, "bold"), fg="darkblue").grid(
            row=passenger_start,
            column=0,
            columnspan=max(cols, 1),
            pady=10,
        )
        for r in range(rows):
            for c in range(cols):
                cell_id = passenger_grid[r][c]
                Label(
                    data_frame,
                    text=cell_id if cell_id else "Empty",
                    width=10,
                    height=5,
                    relief="solid",
                    bg="lightgreen" if cell_id else "lightblue",
                ).grid(row=passenger_start + r + 1, column=c, padx=1, pady=1)

        unplaced_start = passenger_start + rows + 2
        Label(data_frame, text="Unplaced Freight", font=("Arial", 14, "bold"), fg="darkblue").grid(
            row=unplaced_start,
            column=0,
            columnspan=max(cols, 1),
            pady=10,
        )
        for i, freight_id in enumerate(unplaced_freight):
            target_col_count = cols if cols > 0 else 1
            Label(
                data_frame,
                text=str(freight_id),
                width=10,
                height=2,
                relief="solid",
                bg="salmon",
            ).grid(
                row=unplaced_start + 1 + (i // target_col_count),
                column=i % target_col_count,
                padx=1,
                pady=1,
            )

        Button(data_frame, text="Home", command=render_home).grid(
            row=unplaced_start + 3 + (len(unplaced_freight) // (cols if cols > 0 else 1)),
            column=0,
            pady=15,
            sticky="w",
        )

    def settings_view():
        clear_content()

        settings_frame = Frame(content_frame)
        settings_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        Label(settings_frame, text="Settings", font=("Arial", 16, "bold")).pack(pady=10)
        Label(settings_frame, text="Settings window (WIP)").pack(pady=10)
        Button(settings_frame, text="Back", command=render_home).pack(pady=15)

    render_home()
    window.mainloop()
