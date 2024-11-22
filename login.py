from tkinter import *
from tkinter import messagebox
from frontend import open_frontend

#Account creation will be done on a private level.
#Eventually you will need account access to use Lacky
#Probably allow trial accounts.

USER_DB = {
    "Admin": "Readyfireaim",
    "testuser": "password123",
    "t": "t",
}

def login(root, un_entry, ps_entry):
    username = un_entry.get()
    password = ps_entry.get()

    if username in USER_DB and USER_DB[username] == password:
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
        root.destroy()
        #begin fronend.py here. eventually main.py
        open_frontend()
    else:
        messagebox.showerror("Login failed", "Invalid username or password!")

def run_login():
    root = Tk()
    root.title("Lacky Login")
    root.geometry("800x500")
    root.configure(bg="lightgrey")

    title_label = Label(root, text="Welcome to Lacky", font=("Arial", 20, "bold"), bg="lightgrey", fg="black")
    title_label.pack(pady=10)

    un_label = Label(root, text="Username:", font=("Arial", 12), bg="lightgrey", fg="black")
    un_label.pack(pady=5)
    un_entry = Entry(root, font=("Arial", 12))
    un_entry.pack(pady=5)

    ps_label = Label(root, text="Password:", font=("Arial", 12), bg="lightgrey", fg="black")
    ps_label.pack(pady=5)
    ps_entry = Entry(root, font=("Arial", 12), show="*")
    ps_entry.pack(pady=5)

    login_btn = Button(root, text="Login", font=("Arial", 12), command=lambda: login(root, un_entry, ps_entry))
    login_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_login()