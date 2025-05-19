import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime, timedelta
import uuid
import sqlite3
import hashlib
from tkcalendar import DateEntry
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import random
from tkcalendar import DateEntry
from datetime import datetime

class PeriodEnum:
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"
    MONTHLY = "Monthly"

class ClassEnum:
    CLASS1 = "1"
    CLASS2 = "2"

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Form Generator")
        
        self.init_db()

        self.create_login_window()

    def init_db(self):
        self.conn = sqlite3.connect('students.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                rollno TEXT NOT NULL UNIQUE,
                prn TEXT NOT NULL,
                course TEXT,
                travel_from TEXT,
                travel_to TEXT,
                dob DATE,
                classes TEXT         
            )
        ''')

        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rollno TEXT NOT NULL,
                travel_from TEXT,
                travel_to TEXT,
                from_date DATE,
                to_date DATE,
                period TEXT,
                classes TEXT
            )
        ''')

        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS studentdetails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        self.cursor.execute('SELECT COUNT(*) FROM users')
        if self.cursor.fetchone()[0] == 0:
            default_password = hashlib.sha256("admin".encode()).hexdigest()
            self.cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ("admin", default_password))
            self.conn.commit()

        self.conn.commit()

    def create_login_window(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        
        tk.Label(self.login_window, text="Username").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.login_window)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.login_window, text="Password").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.login_window, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.login_window, text="Login", command=self.check_login).grid(row=2, columnspan=2, padx=5, pady=5)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        self.cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        user = self.cursor.fetchone()

        if user:
            messagebox.showinfo("Login Successful", "You have successfully logged in!")
            self.login_window.destroy()  
            self.create_main_window() 
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def create_main_window(self):
        self.setup_layout()

        self.initialize_fields()

        self.dob_entry.bind("<<DateEntrySelected>>", self.calculate_age)

    def setup_layout(self):
        tk.Label(self.root, text="Name").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Roll No").grid(row=1, column=0, padx=5, pady=5)
        self.rollno_entry = tk.Entry(self.root)
        self.rollno_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.root, text="PRN").grid(row=2, column=0, padx=5, pady=5)
        self.prn_entry = tk.Entry(self.root)
        self.prn_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Course").grid(row=3, column=0, padx=5, pady=5)
        self.course_combobox = ttk.Combobox(self.root, values=["MCA", "MMS"])
        self.course_combobox.grid(row=3, column=1, padx=5, pady=5)

        self.placeholder_text = "Select or type station"
        self.mumbai_stations = self.get_mumbai_station_list()

        tk.Label(self.root, text="Travel From").grid(row=4, column=0, padx=5, pady=5)
        self.travel_from_combobox = ttk.Combobox(root, values=self.mumbai_stations)
        self.travel_from_combobox.grid(row=4, column=1, padx=5, pady=5)
        self.travel_from_combobox.set(self.placeholder_text)  
        self.travel_from_combobox.bind("<FocusIn>", self.clear_placeholder)
        self.travel_from_combobox.bind("<FocusOut>", self.add_placeholder)
        self.travel_from_combobox.bind("<KeyRelease>", self.update_suggestions_from)

        tk.Label(self.root, text="Travel To").grid(row=5, column=0, padx=5, pady=5)
        self.travel_to_combobox = ttk.Combobox(root, values=self.mumbai_stations)
        self.travel_to_combobox.grid(row=5, column=1, padx=5, pady=5)
        self.travel_to_combobox.set(self.placeholder_text)  
        self.travel_to_combobox.bind("<FocusIn>", self.clear_placeholder)
        self.travel_to_combobox.bind("<FocusOut>", self.add_placeholder)
        self.travel_to_combobox.bind("<KeyRelease>", self.update_suggestions_to)

        

        tk.Label(self.root, text="DOB").grid(row=6, column=0, padx=5, pady=5)
        self.dob_entry = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy')
        self.dob_entry.grid(row=6, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Age").grid(row=7, column=0, padx=5, pady=5)
        self.age_entry = tk.Entry(self.root)
        self.age_entry.grid(row=7, column=1, padx=5, pady=5)
        self.age_entry.config(state='readonly') 
        
        tk.Label(self.root, text="Class").grid(row=8, column=0, padx=5, pady=5)
        self.class_combobox = ttk.Combobox(self.root, values=[ClassEnum.CLASS1, ClassEnum.CLASS2])
        self.class_combobox.grid(row=8, column=1, padx=5, pady=5)

        
        tk.Button(self.root, text="Add Student", command=self.add_student).grid(row=9, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Read Student", command=self.ask_for_rollno_read).grid(row=9, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Update Student", command=self.ask_for_rollno_update).grid(row=10, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Delete Student", command=self.ask_for_rollno_delete).grid(row=10, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Requested Pass", command=self.fetch_applied_passes).grid(row=11, column=0, padx=5, pady=5)
        self.update_button = tk.Button(self.root, text="Confirm Update", command=self.confirm_update, state='disabled')
        self.update_button.grid(row=11, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Clear", command=self.clear_entries).grid(row=12, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Generate Form", command=self.generate_form).grid(row=12, column=1, padx=5, pady=5)




    def clear_placeholder(self, event):
        
        if event.widget.get() == self.placeholder_text:
            event.widget.set("")  

    def add_placeholder(self, event):
        
        if not event.widget.get():  
            event.widget.set(self.placeholder_text)  

    def update_suggestions_from(self, event):
        
        typed_text = self.travel_from_combobox.get()

        
        if typed_text:
            suggestions = [station for station in self.mumbai_stations if station.lower().startswith(typed_text.lower())]
            self.travel_from_combobox['values'] = suggestions  
        else:
            
            self.travel_from_combobox['values'] = self.mumbai_stations

    def update_suggestions_to(self, event):
        
        typed_text = self.travel_to_combobox.get()

        
        if typed_text:
            suggestions = [station for station in self.mumbai_stations if station.lower().startswith(typed_text.lower())]
            self.travel_to_combobox['values'] = suggestions  
        else:
            
            self.travel_to_combobox['values'] = self.mumbai_stations

    def get_mumbai_station_list(self):
        return [
             "Churchgate", "Marine Lines", "Charni Road", "Grant Road", "Mumbai Central",
             "Mahalaxmi", "Lower Parel", "Prabhadevi", "Dadar", "Matunga Road", "Sion",
             "Kurla", "Andheri", "Vile Parle", "Bandra", "Khar Road", "Santacruz",
             "Vile Parle", "Andheri", "Goregaon", "Malad", "Kandivali", "Borivali",
             "Dahisar", "Mira Road", "Nalasopara", "Vasai Road", "Virar", "Arnala Road",
             "Palghar", "Boisar", "Vangaon", "Dahanu Road", "Bordi", "Umroli", "Vaitarna",
             "Saphale", "Gholvad", "Kelva Road", "Asangaon", "Kelve Road", "Jawhar",
             "Kasara", "Igatpuri", "Ghoti", "Niphad", "Lasalgaon",
             "Pachora Junction", "Dhule", "Nandurbar", "Akkalkot Road", "Kinvat",
             "Kasara", "Jawhar", "Kelve Road","Asangaon", "Kelva Road", "Gholvad", "Saphale", "Vaitarna", "Umroli",
             "Bordi", "Dahanu Road", "Vangaon", "Boisar", "Palghar", "Arnala Road",
             "Virar", "Vasai Road", "Diva Junction", "Mumbra", "Kalwa", "Thane", "Mulund",
             "Nahur", "Bhandup", "Kanjurmarg", "Vikhroli", "Ghatkopar", "Vidyavihar",
             "Kurla", "Sion", "Matunga", "Dadar", "Wadala", "GTB Nagar", "Chunabhatti",
             "Kurla", "Wadala Road", "Sewri", "Cotton Green", "Reay Road", "Dockyard Road",
             "Sandhurst Road", "Masjid", "Chhatrapati Shivaji Maharaj Terminus (formerly VT)",
             "Turbhe", "Kopar Khairane", "Vashi", "Sanpada", "Juinagar", "Nerul",
             "Seawoods-Darave", "Belapur", "Kharghar", "Panvel", "Kalamboli", "Dron",
              "Nhava Sheva", "Uran"
        ]
    
    def initialize_fields(self):
        self.dob_entry.set_date(datetime.today())

    def calculate_age(self, *args):
        try:
            dob = self.dob_entry.get_date()
            today = datetime.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            self.age_entry.config(state='normal')
            self.age_entry.delete(0, tk.END)
            self.age_entry.insert(0, age)
            self.age_entry.config(state='readonly')  
        except ValueError:
            self.age_entry.delete(0, tk.END)

    def validate_inputs(self):
        if not self.name_entry.get().isalpha():
            messagebox.showerror("Validation Error", "Name must contain only letters.")
            return False
        if not self.rollno_entry.get().isalnum():
            messagebox.showerror("Validation Error", "Roll No must be alphanumeric.")
            return False
        if not self.prn_entry.get().isdigit():
            messagebox.showerror("Validation Error", "PRN must be a 16-digit numeric value.")
            return False
        try:
            dob = datetime.strptime(self.dob_entry.get(), "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Validation Error", "DOB must be a valid date (DD-MM-YYYY).")
            return False
        if self.class_combobox.get() not in [ClassEnum.CLASS1, ClassEnum.CLASS2]:
            messagebox.showerror("Validation Error", "Select a valid class.")
            return False
        valid_stations = [
        "Churchgate", "Marine Lines", "Charni Road", "Grant Road", "Mumbai Central",
        "Mahalaxmi", "Lower Parel", "Prabhadevi", "Dadar", "Matunga Road", "Sion",
        "Kurla", "Andheri", "Vile Parle", "Bandra", "Khar Road", "Santacruz",
        "Vile Parle", "Andheri", "Goregaon", "Malad", "Kandivali", "Borivali",
        "Dahisar", "Mira Road", "Nalasopara", "Vasai Road", "Virar", "Arnala Road",
        "Palghar", "Boisar", "Vangaon", "Dahanu Road", "Bordi", "Umroli", "Vaitarna",
        "Saphale", "Gholvad", "Kelva Road", "Asangaon", "Kelve Road", "Jawhar",
        "Kasara", "Igatpuri", "Ghoti", "Niphad", "Lasalgaon", "Pachora Junction", "Dhule",
        "Nandurbar", "Akkalkot Road", "Kinvat", "Kasara", "Jawhar", "Kelve Road",
        "Asangaon", "Kelva Road", "Gholvad", "Saphale", "Vaitarna", "Umroli", "Bordi",
        "Dahanu Road", "Vangaon", "Boisar", "Palghar", "Arnala Road", "Virar", "Vasai Road",
        "Diva Junction", "Mumbra", "Kalwa", "Thane", "Mulund", "Nahur", "Bhandup",
        "Kanjurmarg", "Vikhroli", "Ghatkopar", "Vidyavihar", "Kurla", "Sion", "Matunga",
        "Dadar", "Wadala", "GTB Nagar", "Chunabhatti", "Kurla", "Wadala Road", "Sewri",
        "Cotton Green", "Reay Road", "Dockyard Road", "Sandhurst Road", "Masjid",
        "Chhatrapati Shivaji Maharaj Terminus (formerly VT)", "Turbhe", "Kopar Khairane",
        "Vashi", "Sanpada", "Juinagar", "Nerul", "Seawoods-Darave", "Belapur",
        "Kharghar", "Panvel", "Kalamboli", "Dron", "Nhava Sheva", "Uran"
        ]

        travel_to = self.travel_to_combobox.get()
        travel_from = self.travel_from_combobox.get()

        if travel_to not in valid_stations:
            messagebox.showerror("Validation Error", f"Travel To station '{travel_to}' is not valid.")
            return False

        if travel_from not in valid_stations:
            messagebox.showerror("Validation Error", f"Travel From station '{travel_from}' is not valid.")
            return False        
        return True

    def add_student(self):
        if not self.validate_inputs():
            return

        name = self.name_entry.get()
        rollno = self.rollno_entry.get()
        prn = self.prn_entry.get()
        course = self.course_combobox.get()
        travel_from = self.travel_from_combobox.get()
        travel_to = self.travel_to_combobox.get()
        dob = datetime.strptime(self.dob_entry.get(), "%d-%m-%Y")
        classes= self.class_combobox.get()

        if self.is_rollno_exists(rollno):
            messagebox.showerror("Error", "Roll No already exists.")
            return

        student_data = (str(uuid.uuid4()), name, rollno, prn, course, travel_from, travel_to, dob, classes)
        self.cursor.execute('''
            INSERT INTO students (id, name, rollno, prn, course, travel_from, travel_to, dob, classes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', student_data)
        self.conn.commit()

        self.cursor.execute('''
            INSERT INTO studentdetails (username, password)
            VALUES (?, ?)
        ''',(rollno, rollno ))
        self.conn.commit()

        messagebox.showinfo("Success", "Student added successfully.")
        self.clear_entries()

    def is_rollno_exists(self, rollno):
        self.cursor.execute('SELECT 1 FROM students WHERE rollno = ?', (rollno,))
        return self.cursor.fetchone() is not None

    def ask_for_rollno_read(self):
        rollno = simpledialog.askstring("Input", "Enter Roll No:")
        student = self.get_student_by_rollno(rollno)
        if student:
            messagebox.showinfo("Student Info", f"Name: {student[1]}\nRoll No: {student[2]}\nPRN: {student[3]}\nCourse: {student[4]}\nTravel From: {student[5]}\nTravel To: {student[6]}\nDOB: {student[7]}")
        else:
            messagebox.showerror("Error", "Roll No not found.")

    def fetch_applied_passes(self):
    
        try:
            self.cursor.execute('''
                SELECT student_id, applied_date 
                FROM pass_applied 
                ORDER BY applied_date DESC
            ''')
            results = self.cursor.fetchall()

            if results:
            
                details = "Applied Passes:\n\n"
            for idx, (student_id, applied_date) in enumerate(results, start=1):
                details += f"{idx}. Student ID: {student_id}, Applied Date: {applied_date}\n"
            
                messagebox.showinfo("Applied Passes", details)
            else:
                messagebox.showinfo("Applied Passes", "No passes have been applied yet.")

        except Exception as e:
              messagebox.showerror("Error", f"An error occurred while fetching passes: {e}")


    def get_student_by_rollno(self, rollno):
        self.cursor.execute('SELECT * FROM students WHERE rollno = ?', (rollno,))
        return self.cursor.fetchone()

    def ask_for_rollno_update(self):
        rollno = simpledialog.askstring("Input", "Enter Roll No to update:")
        student = self.get_student_by_rollno(rollno)
        if student:
            self.selected_rollno = rollno
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, student[1])
            self.rollno_entry.delete(0, tk.END)
            self.rollno_entry.insert(0, student[2])
            self.prn_entry.delete(0, tk.END)
            self.prn_entry.insert(0, student[3])
            self.course_combobox.set(student[4])
            self.travel_from_combobox.delete(0, tk.END)
            self.travel_from_combobox.insert(0, student[5])
            self.travel_to_combobox.delete(0, tk.END)
            self.travel_to_combobox.insert(0, student[6])
            
            self.class_combobox.insert(0,student[8])
        
            self.dob_entry.set_date(datetime.strptime(student[7], '%Y-%m-%d %H:%M:%S'))
            
        
            self.age_entry.config(state='normal')
            self.age_entry.delete(0, tk.END)
            self.age_entry.insert(0, "")
            self.age_entry.config(state='readonly')
            self.update_button.config(state='normal')
        else:
            messagebox.showerror("Error", "Roll No not found.")

    def confirm_update(self):
        if not self.validate_inputs():
            return

        name = self.name_entry.get()
        rollno = self.rollno_entry.get()
        prn = self.prn_entry.get()
        course = self.course_combobox.get()
        travel_from = self.travel_from_combobox.get()  
        travel_to = self.travel_to_combobox.get()
        classes=self.class_combobox.get()
        dob = datetime.strptime(self.dob_entry.get(), "%d-%m-%Y")

        self.cursor.execute('''
            UPDATE students
            SET name = ?, rollno = ?, prn = ?, course = ?, travel_from = ?, travel_to = ?, dob = ?, classes=?
            WHERE rollno = ?
        ''', (name, rollno, prn, course, travel_from, travel_to, dob, classes, self.selected_rollno))
        self.conn.commit()

        messagebox.showinfo("Success", "Student updated successfully.")
        self.clear_entries()
        self.update_button.config(state='disabled')

    def ask_for_rollno_delete(self):
        rollno = simpledialog.askstring("Input", "Enter Roll No to delete:")
        if self.get_student_by_rollno(rollno):
            self.cursor.execute('DELETE FROM students WHERE rollno = ?', (rollno,))
            self.conn.commit()
            self.cursor.execute('DELETE FROM forms WHERE rollno = ?', (rollno,))
            messagebox.showinfo("Success", "Student deleted successfully.")
        else:
            messagebox.showerror("Error", "Roll No not found.")

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.rollno_entry.delete(0, tk.END)
        self.prn_entry.delete(0, tk.END)
        self.course_combobox.set('')
        self.travel_from_combobox.set("Select or type station")
        self.travel_to_combobox.set("Select or type station")
        self.dob_entry.set_date(datetime.today())
        self.age_entry.config(state='normal')
        self.age_entry.delete(0, tk.END)
        self.age_entry.config(state='readonly')
        self.class_combobox.set('')
        self.update_button.config(state='disabled')

    def generate_form(self):
        rollno = simpledialog.askstring("Input", "Enter Roll No:")
        student = self.get_student_by_rollno(rollno)
        if student:
            self.cursor.execute('SELECT to_date FROM forms WHERE rollno = ? ORDER BY id DESC LIMIT 1', (rollno,))
            existing_form = self.cursor.fetchone()
        
            if existing_form:
                existing_to_date = datetime.strptime(existing_form[0], '%d-%m-%Y')
                current_from_date = datetime.today()
            
                if existing_to_date >= current_from_date:
                    messagebox.showerror("Validation Error", "Cannot generate form: Form is already generated")
                    return
        
            generate_form_window = tk.Toplevel(self.root)
            generate_form_window.title("Generate Form")

            tk.Label(generate_form_window, text="Name").grid(row=0, column=0, padx=5, pady=5)
            tk.Label(generate_form_window, text=student[1]).grid(row=0, column=1, padx=5, pady=5)

            tk.Label(generate_form_window, text="Roll No").grid(row=1, column=0, padx=5, pady=5)
            tk.Label(generate_form_window, text=student[2]).grid(row=1, column=1, padx=5, pady=5)

            tk.Label(generate_form_window, text="Travel From").grid(row=2, column=0, padx=5, pady=5)
            tk.Label(generate_form_window, text=student[5]).grid(row=2, column=1, padx=5, pady=5)

            tk.Label(generate_form_window, text="Travel To").grid(row=3, column=0, padx=5, pady=5)
            tk.Label(generate_form_window, text=student[6]).grid(row=3, column=1, padx=5, pady=5)

            tk.Label(generate_form_window, text="Class").grid(row=4, column=0, padx=5, pady=5)
            tk.Label(generate_form_window, text=student[8]).grid(row=4, column=1, padx=5, pady=5)

            today = datetime.today()
            from_date = today.strftime('%d-%m-%Y')

            tk.Label(generate_form_window, text="From Date").grid(row=5, column=0, padx=5, pady=5)
            tk.Label(generate_form_window, text=from_date).grid(row=5, column=1, padx=5, pady=5)

            tk.Label(generate_form_window, text="To Date").grid(row=6, column=0, padx=5, pady=5)
            self.to_date_label = tk.Label(generate_form_window, text="")
            self.to_date_label.grid(row=6, column=1, padx=5, pady=5)

            tk.Label(generate_form_window, text="Period").grid(row=8, column=0, padx=5, pady=5)
            self.period_combobox = ttk.Combobox(generate_form_window, values=[PeriodEnum.QUARTERLY, PeriodEnum.MONTHLY])
            self.period_combobox.grid(row=8, column=1, padx=5, pady=5)

            self.period_combobox.bind("<<ComboboxSelected>>", self.update_to_date)

            tk.Button(generate_form_window, text="Generate", command=lambda: self.save_form_and_display_info(student,rollno)).grid(row=9, columnspan=2, padx=5, pady=5)
        else:
            messagebox.showerror("Error", "Roll No not found.")

    def save_form_and_display_info(self, student, rollno):
        period = self.period_combobox.get()
        from_date = datetime.today().strftime('%d-%m-%Y')
        to_date = self.to_date_label.cget("text")

        if student:
            self.cursor.execute('SELECT to_date FROM forms WHERE rollno = ? ORDER BY id DESC LIMIT 1', (rollno,))
            existing_form = self.cursor.fetchone()
        
            if existing_form:
                existing_to_date = datetime.strptime(existing_form[0], '%d-%m-%Y')
                current_from_date = datetime.today()
            
                if existing_to_date >= current_from_date:
                    messagebox.showerror("Validation Error", "Cannot generate form: Form is already generated")
                    return

        self.cursor.execute('''
            INSERT INTO forms (name, rollno, travel_from, travel_to, from_date, to_date, period)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (student[1], student[2], student[5], student[6], from_date, to_date, period))
        self.conn.commit()

        self.generate_pdf(student, from_date, to_date, period)

        messagebox.showinfo("Generated Info", f"From Date: {from_date}\n"
                                                f"To Date: {to_date}\n"
                                                f"Period: {period}")

    def get_next_serial_number_from_db():
        conn = sqlite3.connect('students.db')  
        cursor = conn.cursor()
        cursor.execute("SELECT serial_number FROM serial_numbers WHERE id = 1")
        row = cursor.fetchone()

        if row:
           serial_number = row[0]
           cursor.execute("UPDATE serial_numbers SET serial_number = ? WHERE id = 1", (serial_number + 1,))
        else:
           serial_number = 1
           cursor.execute("INSERT INTO serial_numbers (id, serial_number) VALUES (1, ?)", (serial_number + 1,))
        conn.commit()
        conn.close()

        return serial_number

    def generate_pdf(self, student, from_date, to_date, period):
        pdf_filename = f"{student[2]}_form.pdf" 
        document = SimpleDocTemplate(pdf_filename, pagesize=A4)
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        title_style = ParagraphStyle('Title', fontSize=12, leading=14, alignment=1)
        small_style = ParagraphStyle('Small', fontSize=8, leading=10)
    
        elements = []
        sr_number = random.randint(1000000, 9999999)
        header_text = (
        f"<b>INDIAN RAILWAYS</b> &nbsp;&nbsp;&nbsp;&nbsp;"
        f"Sr. No. A {sr_number} &nbsp;&nbsp;&nbsp;&nbsp;"
        f"99/SN99B P.L. No. 83055836"
        )
        elements.append(Paragraph(header_text, title_style))
        elements.append(Spacer(1, 12))

        certificate_text = (
        f"School Certificate to be issued only to Students of not more than 25 years of age "
        f"except otherwise permitted under the Rules.<br/><br/>"
        f"I hereby certify that <b>{student[1]}</b> regularly attends this College for the purpose of receiving education, "
        f"the institution of which I am the Principal, and his/her age this day, according to my belief "
        f"and from enquiries I have made, is <b>{self.age_entry.get()}</b> years. His/her date of birth "
        f"as entered in the College Register being <b>{student[7]}</b>. "
        f"He/She is therefore, entitled to the Season Ticket as detailed below at half the full rates charged for adults.<br/><br/>"
        )
        elements.append(Paragraph(certificate_text, normal_style))
        elements.append(Spacer(1, 12)) 

        table_data = [
        ["Class", "Period", "From", "To Station", "Class and No. of Season Ticket issued"],
        [student[8], period, student[5], student[6]]
        ]

        table = Table(table_data, colWidths=[1.5 * inch, 1.2 * inch, 1.2 * inch, 1.5 * inch, 2.5 * inch])
        table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
         ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        date_text = f"<b>Date:</b> {from_date}"
        elements.append(Paragraph(date_text, normal_style))
        elements.append(Spacer(1, 12)) 

        footer_text = (
        "<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>Name of College/School and Stamp<br/><br/><br/><br/>"
        "<br/><br/><br/><br/>Available only between Station nearest to Student's residence and Station nearest to the Outage School.<br/><br/>"
        "This column should be filled in by the Station issuing the Season Ticket.<br/><br/>"
        "If no Season Ticket is held the word 'NIL' should be inserted.<br/><br/><br/><br/>"
        "<b>Note:</b> This certificate will be valid for three days including the date of issue and if not "
        "made use of within that time must be returned by the issued for cancellation.<br/><br/><br/><br/>"
        "No fresh concession certificate should be granted by the School/College authorities to any of their students "
        "in the event of his/her season ticket being lost during the currency of the previous certificate. Such students "
        "must purchase a fresh season ticket of tariff fares during that period.<br/><br/>"
        "C.R.P.P/By/11-2019/01-19-0018-35000Bks x50Lvs."
        )
        elements.append(Paragraph(footer_text, small_style))

        document.build(elements)

        os.startfile(pdf_filename)

        self.cursor.execute('DELETE FROM pass_applied WHERE student_id = ?', (student[2],))
        self.conn.commit()

    def create_paragraph(self, text):
        style = getSampleStyleSheet()['Normal']
        paragraph = Paragraph(text, style)
        return paragraph

    def update_to_date(self, *args):
        period = self.period_combobox.get()
        if period:
            today = datetime.today()
            if period == PeriodEnum.MONTHLY:
                to_date = today + timedelta(days=30)
            elif period == PeriodEnum.QUARTERLY:
                to_date = today + timedelta(days=90)
            elif period == PeriodEnum.YEARLY:
                to_date = today + timedelta(days=365)
            else:
                return
            
            self.to_date_label.config(text=to_date.strftime('%d-%m-%Y'))

    def display_generated_info(self):
        period = self.period_combobox.get()
        from_date = datetime.today().strftime('%d-%m-%Y')
        to_date = self.to_date_label.cget("text")

        messagebox.showinfo("Generated Info", f"From Date: {from_date}\n"
                                                f"To Date: {to_date}\n"
                                                f"Period: {period}")


    def on_closing(self):
        self.conn.close()  
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentCRUDApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  
    root.mainloop()
