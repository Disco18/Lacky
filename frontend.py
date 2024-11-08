from tkinter import *
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText
import backend

#Graphics and display will be coded into this module

#Creates an instance, title and size.
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

        if 'id' not in data.columns:
            print("No 'id' column found in the spreadsheet.").pack()
        
        else:
            if data is not None:
                show_manifest_data(data)

def button_upload_clicked():
    newWindow = Toplevel(window)
    newWindow.title("Upload")
    newWindow.geometry("400x200")
    Label(newWindow, text="Drag and drop .csv file here!").pack()
    newWindow.bind("<Button-1>", lambda event: open_file_dialog())

def show_manifest_data(data):
    data_window = Toplevel(window)
    data_window.title("Manifest")

    if 'id' not in data.columns:
        Label(data_window, text="No 'id' column found in the spreadsheet.").pack()
        return
    
    id_data = data['id'].dropna().tolist()
    #Sets the grid size based on the manifest. Probably change this to a set value based on the trailer size.
    grid_size = int(len(id_data) ** 0.5) + 1

    for i, value in enumerate(id_data):
        row = i // grid_size
        col = i % grid_size
        label = Label(data_window, text=str(value), width=10, height=5, relief="solid", bg="lightblue")
        label.grid(row=row, column=col, padx=4, pady=4)

#this will display the other details accosiated with the imported data. e.g (length,height,dg ect..)
#in a pop up window when a populated grid square clicked.
def display_manifest_data(data):
    popup = Toplevel(window)
    popup.title("Information")

    for idx, (col, val) in enumerate(row_data.items()):
        tk.Label(popup, text=f"{col}: {val}", anchor="w").grid(row=idx, column=0, padx=10, pady=2, sticky="w")



#def print_window():
    #x = window.winfo_rootx()
    #y = window.winfo_rooty()
    #w = x + window.winfo_width()
    #h = y + window.winfo_height()

    #mageGrab.grab().crop((x, y, w, h)).save("window_screenshot.png")
    #label.config(text"Window screenshot saved as 'window_screenshot.png'!")

button_upload = Button(window, text="Upload Spreadsheet", command=button_upload_clicked)
button_clp = Button(window, text="Generate Load Plan", command=button_clp_clicked)
button_print = Button(window, text="Print", background="blue", foreground="white")
button_quit = Button(window, text="Exit", command=window.quit)

button_upload.pack(pady=10)
button_clp.pack(pady=10)
button_print.pack(pady=10)
button_quit.pack(pady=10)



window.mainloop()