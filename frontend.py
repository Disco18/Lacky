from tkinter import *
from tkinter import ttk
#from PIL import ImageGrab

#Graphics and display will be coded into this module

#Creates an instance, title and size.
window = Tk()
window.title("Lacky v0.1")
window.geometry("600x400")

def button_clp_clicked():
    print("Please wait while we take the freight and generate a load plan.")

def button_upload_clicked():
    newWindow = Toplevel(window)
    newWindow.title("Upload")
    newWindow.geometry("400x200")
    #frame1 = Toplevel.frame(root, width=400, height=200)
    #frame1.grid(row=0, column=0)
    Label(newWindow, text="Drag and drop .csv file here!").pack()

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