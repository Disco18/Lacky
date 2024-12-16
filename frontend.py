from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import backend
import assigner

#Graphics and display will be coded into this module

#Creates an instance, title and size.
def open_frontend():
    window = Tk()
    window.title("Lacky v0.1")
    window.geometry("600x400")

    def button_clp_clicked():
        print("Please wait while we take the freight and generate a load plan.")

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
        newWindow.geometry("400x200")
        Label(newWindow, text="Drag and drop .csv file here!").pack()
        newWindow.bind("<Button-1>", lambda event: (open_file_dialog(), newWindow.destroy()))

    def show_manifest_data(data, grid_dimensions):
        data_window = Toplevel(window)
        data_window.title("Manifest")

        rows, cols = grid_dimensions
        size_constraints = assigner.generate_size_constraints(rows, cols)
        assigner.driver_grid, assigner.passenger_grid = assigner.assign_freight(data, grid_dimensions, size_constraints)

        print("Grid Dimensions:", rows, "rows,", cols, "cols")

        #Added a label to tell the user which side of the graph they are viewing.
        #columnspan will make sure that the loading grid is placed below this label.
        ds_label = Label(data_window, text="Driver Side", font=("Ariel", 14, "bold"), fg="darkblue")
        ds_label.grid(row=0, column=0, columnspan=cols, pady=10)
        
        ps_label = Label(data_window, text="Passenger Side", font=("Arial", 14, "bold"), fg="darkblue")
        ps_label.grid(row=rows + 2, column=0, columnspan=cols, pady=10)
        
        if 'id' not in data.columns:
            Label(data_window, text="No 'id' column found in the spreadsheet.").pack()
            return
        
        #id_data = data.dropna(subset=['id']).reset_index(drop=True)

        #Creates the grid of labels for each ID to the choosen transport setup.
        #This should stop the grid creation to the size set in the TRANSPORT_SETUP.
        for r in range(rows):
            for c in range(cols):
                cell_id = assigner.driver_grid[r][c]
                label = Label(
                    data_window,
                    text=cell_id if cell_id else "Empty",
                    width=10,
                    height=5,
                    relief="solid",
                    bg="lightgreen" if cell_id else "lightblue"
                )
                if cell_id:
                    try:
                        row_data = data.loc[data["id"].astype(str) == str(cell_id)].iloc[0].to_dict()
                        add_popup(label, row_data)
                    except IndexError:
                        print(f"No data found for ID: {cell_id}")
                label.grid(row=r + 1, column=c, padx=1, pady=1)

        #Passenger grid
        for r in range(rows):
            for c in range(cols):
                cell_id = assigner.passenger_grid[r][c]
                label = Label(
                    data_window,
                    text=cell_id if cell_id else "Empty",
                    width=10,
                    height=5,
                    relief="solid",
                    bg="lightgreen" if cell_id else "lightblue"
                )
                if cell_id:  # Only bind the event if the cell is populated
                    try:
                        row_data = data.loc[data["id"].astype(str) == str(cell_id)].iloc[0].to_dict()
                        add_popup(label, row_data)
                    except IndexError:
                        print(f"No data found for ID: {cell_id}")
                label.grid(row=rows + 3 + r, column=c, padx=1, pady=1)

    def choose_transport_setup(data):
        setup_window = Toplevel(window)
        setup_window.title("Select Transport Setup")
        setup_window.geometry("400x400")

        Label(setup_window, text="Please select a transport setup:").pack(pady=5)
        for setup_name, dimensions in backend.TRANSPORT_SETUP.items():
            btn = Button(
                setup_window,
                text=setup_name,
                command=lambda d=dimensions: [setup_window.destroy(), show_manifest_data(data, d)]
            )
            btn.pack(pady=3)

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


    button_upload = Button(window, text="Upload Spreadsheet", command=button_upload_clicked)
    button_clp = Button(window, text="Generate Load Plan", command=button_clp_clicked)
    button_print = Button(window, text="Print", background="blue", foreground="white")
    button_quit = Button(window, text="Exit", command=window.quit)

    button_upload.pack(pady=10)
    button_clp.pack(pady=10)
    button_print.pack(pady=10)
    button_quit.pack(pady=10)



    window.mainloop()