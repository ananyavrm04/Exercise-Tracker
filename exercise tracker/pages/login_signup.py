import tkinter as tk
import sqlite3
from tkinter import messagebox
import hashlib

class LoginSignupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.current_user_id = None

        self.create_widgets()

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self, bg="white", padx=50, pady=50)
        main_frame.pack(expand=True)

        tk.Label(main_frame, text="Welcome to Urban Yogi Lifestyle!", font=("Arial", 24, "bold"), bg="white", fg="#2e2e2e").pack(pady=20)

        login_frame = tk.LabelFrame(main_frame, text="Login", font=("Arial", 16, "bold"), bg="white", bd=2, relief="groove", padx=20, pady=20)
        login_frame.pack(pady=20, fill="x", expand=True)

        tk.Label(login_frame, text="Phone Number:", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        self.login_phone_entry = tk.Entry(login_frame, font=("Arial", 12), width=30)
        self.login_phone_entry.pack(anchor="w", pady=5)

        tk.Label(login_frame, text="Password:", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        self.login_password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12), width=30)
        self.login_password_entry.pack(anchor="w", pady=5)

        tk.Button(login_frame, text="Login", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=15, command=self.login_user).pack(pady=15)
        
        # New "Create Account" button on the login page
        tk.Button(login_frame, text="Create New Account", font=("Arial", 10), bg="#f0f0f0", command=lambda: self.controller.show_page("create_account")).pack(pady=10, anchor="w")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login_user(self):
        phone = self.login_phone_entry.get()
        password = self.login_password_entry.get()

        if not all([phone, password]):
            messagebox.showerror("Error", "Phone number and password are required for login.")
            return

        hashed_password = self.hash_password(password)

        conn = None
        try:
            conn = sqlite3.connect("fitness_app.db")
            cursor = conn.cursor()

            cursor.execute("SELECT id, name FROM user_profile WHERE phone_number = ? AND password = ?", (phone, hashed_password))
            user_data = cursor.fetchone()

            if user_data:
                self.controller.logged_in_user_id = user_data[0]
                messagebox.showinfo("Success", f"Welcome back, {user_data[1]}!")
                self.controller.show_page("home")
            else:
                messagebox.showerror("Login Failed", "Invalid phone number or password.")

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Database error during login: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            if conn:
                conn.close()

