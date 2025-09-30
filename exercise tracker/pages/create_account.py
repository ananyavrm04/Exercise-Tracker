import tkinter as tk
import sqlite3
from tkinter import messagebox
import hashlib

class CreateAccountPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        self.create_widgets()

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self, bg="white", padx=50, pady=20)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="Create Your Account", font=("Arial", 24, "bold"), bg="white", fg="#2e2e2e").pack(pady=(0, 20))

        tk.Button(main_frame, text="← Back to Login", bg="#f0f0f0", command=lambda: self.controller.show_page("login_signup")).pack(anchor="nw", padx=0, pady=10)

        form_frame = tk.LabelFrame(main_frame, text="Personal Details", font=("Arial", 16, "bold"), bg="white", bd=2, relief="groove", padx=20, pady=20)
        form_frame.pack(pady=20, fill="x", expand=True)

        tk.Label(form_frame, text="Name:", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        self.name_entry = tk.Entry(form_frame, font=("Arial", 12), width=40)
        self.name_entry.pack(anchor="w", pady=5)

        tk.Label(form_frame, text="Age:", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        self.age_entry = tk.Entry(form_frame, font=("Arial", 12), width=40)
        self.age_entry.pack(anchor="w", pady=5)

        tk.Label(form_frame, text="Gender:", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        self.gender_var = tk.StringVar(self)
        self.gender_var.set("Select Gender")
        self.gender_option_menu = tk.OptionMenu(form_frame, self.gender_var, "Male", "Female", "Prefer not to say") # Updated options
        self.gender_option_menu.config(font=("Arial", 12), bg="white", width=38)
        self.gender_option_menu.pack(anchor="w", pady=5)

        tk.Label(form_frame, text="Phone Number:", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        self.phone_entry = tk.Entry(form_frame, font=("Arial", 12), width=40)
        self.phone_entry.pack(anchor="w", pady=5)

        tk.Label(form_frame, text="Password:", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        self.password_entry = tk.Entry(form_frame, show="*", font=("Arial", 12), width=40)
        self.password_entry.pack(anchor="w", pady=5)

        tk.Button(main_frame, text="Register Account", font=("Arial", 14, "bold"), bg="#007bff", fg="white", width=20, command=self.register_user).pack(pady=20)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self):
        name = self.name_entry.get()
        age = self.age_entry.get()
        gender = self.gender_var.get()
        phone = self.phone_entry.get()
        password = self.password_entry.get()

        if gender == "Select Gender":
            messagebox.showerror("Error", "Please select your gender.")
            return

        if not all([name, age, gender, phone, password]):
            messagebox.showerror("Error", "All fields are required for registration.")
            return

        try:
            age = int(age)
            if not phone.isdigit() or len(phone) < 10:
                messagebox.showerror("Error", "Please enter a valid phone number (at least 10 digits).")
                return

            hashed_password = self.hash_password(password)

            conn = None
            try:
                conn = sqlite3.connect("fitness_app.db")
                cursor = conn.cursor()

                cursor.execute("SELECT id FROM user_profile WHERE phone_number = ?", (phone,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Phone number already registered. Please login.")
                    return

                # Removed fitness_goal from INSERT query
                cursor.execute("""
                    INSERT INTO user_profile (name, age, gender, phone_number, password)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, age, gender, phone, hashed_password))
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully! Please login.")
                self.controller.show_page("login_signup")

            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Phone number already registered. Please login.")
            except sqlite3.OperationalError as e:
                messagebox.showerror("Database Error", f"Database error during registration: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            finally:
                if conn:
                    conn.close()

        except ValueError:
            messagebox.showerror("Error", "Age must be a number.")

