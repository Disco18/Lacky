from tkinter import *
from tkinter import messagebox
import frontend

#Account creation will be done on a private level.
#Eventually you will need account access to use Lacky
#Probably allow trial accounts.

USER_DB = {
    "Admin": "Readyfireaim",
    "testuser": "password123",
}

def login():
    username = un_entry.get()
    password = ps_entry.get()

    if username in USER_DB and USER_DB[username] == password:
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
        root.destory()
        #begin fronend.py here. eventually main.py
        frontend()
    else:
        messagebox.showerror("Login failed", "Invalid username or password!")

root = Tk()
root.title("Lacky Login")
root.geometry("800x500")
root.configure(bg="purple")

title_label = Label(root, text="Welcome to Lacky", font=("Arial", 20, "bold"), bg="purple", fg="white")
title_label.pack(pady=10)

un_label = Label(root, text="Username:", font=("Arial", 12), fg="black")
un_label.pack(pady=5)
un_entry = Entry(root, font=("Arial", 12))
un_entry.pack(pady=5)

ps_label = Label(root, text="Password:", font=("Arial", 12), fg="black")
ps_label.pack(pady=5)
ps_entry = Entry(root, font=("Arial", 12), show="*")
ps_entry.pack(pady=5)

login_btn = Button(root, text="Login", font=("Arial", 12), command=login)
login_btn.pack(pady=10)

root.mainloop()