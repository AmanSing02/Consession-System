import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime

conn = sqlite3.connect('students.db')
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS pass_applied (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    applied_date TEXT NOT NULL
)
""")
conn.commit()


def login_student(student_id, password):
    
    cursor.execute("SELECT * FROM studentdetails WHERE username = ? AND password = ?", (student_id, password))
    result = cursor.fetchone()
    return result



def apply_pass(student_id):
    
    cursor.execute("SELECT * FROM pass_applied WHERE student_id = ?", (student_id,))
    existing_pass = cursor.fetchone()

    if existing_pass:
        
        messagebox.showerror("Pass Application", "You have already applied for a pass!")
        return

    
    applied_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO pass_applied (student_id, applied_date) VALUES (?, ?)", (student_id, applied_date))
    conn.commit()
    messagebox.showinfo("Pass Application", "Your pass has been successfully applied!")

root = ttk.Window(themename="litera")
root.title("Student Pass Application System")
root.geometry("600x600")


current_student_id = None



def login():
    global current_student_id
    student_id = entry_student_id.get()
    password = entry_password.get()
    user = login_student(student_id, password)
    if user:
        current_student_id = student_id
        messagebox.showinfo("Success", "Login successful!")
        frame.pack_forget()  
        show_dashboard()  
    else:
        messagebox.showerror("Error", "Invalid student ID or password!")


def show_dashboard():
    
    dashboard_frame = ttk.Frame(root, padding=20)
    dashboard_frame.pack(pady=50)

    ttk.Label(dashboard_frame, text=f"Welcome, {current_student_id}", font=("Arial", 20, "bold")).pack(pady=10)
    ttk.Button(dashboard_frame, text="Apply for Pass", command=lambda: apply_pass(current_student_id)).pack(pady=10)
    ttk.Button(dashboard_frame, text="Logout", command=lambda: logout(dashboard_frame)).pack(pady=10)


def logout(dashboard_frame):
    
    global current_student_id
    current_student_id = None
    dashboard_frame.pack_forget()
    frame.pack(pady=50)



frame = ttk.Frame(root, padding=20)
frame.pack(pady=50)

ttk.Label(frame, text="Student Login", font=("Arial", 20, "bold")).pack(pady=10)

ttk.Label(frame, text="Student ID", font=("Arial", 12)).pack()
entry_student_id = ttk.Entry(frame)
entry_student_id.pack()

ttk.Label(frame, text="Password", font=("Arial", 12)).pack()
entry_password = ttk.Entry(frame, show="*")
entry_password.pack()

ttk.Button(frame, text="Login", command=login).pack(pady=10)



root.mainloop()
