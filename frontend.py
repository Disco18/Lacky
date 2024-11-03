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

        if data is not None:
            return show_manifest_data

def button_upload_clicked():
    newWindow = Toplevel(window)
    newWindow.title("Upload")
    newWindow.geometry("400x200")
    #frame1 = Toplevel.frame(root, width=400, height=200)
    #frame1.grid(row=0, column=0)
    Label(newWindow, text="Drag and drop .csv file here!").pack()
    Label.bind("<Button-1>", lambda event: open_file_dialog())

def show_manifest_data(data):
    data_window = Toplevel(window)
    data_window.title("Manifest")

    tree = ttk.Treeview(data_window)
    tree["columns"] = list(data.columns)
    tree["show"] = "headings"

    for col in data.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    for _, row in data.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(expand=True, fill="both")


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