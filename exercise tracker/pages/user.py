import tkinter as tk
import sqlite3
from tkinter import messagebox

class UserPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.user_id = self.controller.logged_in_user_id
        self.user_data = {}

        self.create_widgets()
        self.load_user_profile()

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self, bg="white", padx=50, pady=20)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="Your Profile", font=("Arial", 24, "bold"), bg="white").pack(pady=(0, 20))

        form_frame = tk.Frame(main_frame, bg="white")
        form_frame.pack(pady=10, anchor="center")

        labels_text = ["Name:", "Age:", "Gender:", "Phone Number:"] # Removed "Fitness Goal:"
        self.entries = {}

        for i, text in enumerate(labels_text):
            tk.Label(form_frame, text=text, bg="white", font=("Arial", 12)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            
            if text == "Gender:":
                self.gender_var = tk.StringVar(self)
                self.gender_option_menu = tk.OptionMenu(form_frame, self.gender_var, "Male", "Female", "Prefer not to say") # Added "Prefer not to say"
                self.gender_option_menu.config(font=("Arial", 12), bg="white", width=20)
                self.gender_option_menu.grid(row=i, column=1, sticky="ew", pady=5, padx=10)
                self.entries["Gender"] = self.gender_var
            else:
                entry = tk.Entry(form_frame, font=("Arial", 12), width=30, state='readonly')
                entry.grid(row=i, column=1, sticky="ew", pady=5, padx=10)
                self.entries[text.replace(":", "")] = entry

        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(pady=20, anchor="center")

        self.edit_button = tk.Button(button_frame, text="Edit Profile", bg="#007bff", fg="white",
                                     font=("Arial", 12, "bold"), width=15, command=self.toggle_edit_mode)
        self.edit_button.pack(side="left", padx=10)

        self.save_button = tk.Button(button_frame, text="Save Changes", bg="#4CAF50", fg="white",
                                     font=("Arial", 12, "bold"), width=15, command=self.save_profile, state=tk.DISABLED)
        self.save_button.pack(side="left", padx=10)

        self.status_label = tk.Label(main_frame, text="", bg="white", fg="green", font=("Arial", 10))
        self.status_label.pack(pady=10)


    def load_user_profile(self):
        if not self.user_id:
            messagebox.showerror("Error", "No user logged in.")
            return

        conn = None
        try:
            conn = sqlite3.connect("fitness_app.db")
            cursor = conn.cursor()
            # Removed fitness_goal from SELECT query
            cursor.execute("SELECT name, age, gender, phone_number FROM user_profile WHERE id = ?", (self.user_id,))
            user_data = cursor.fetchone()

            if user_data:
                self.user_data = {
                    "Name": user_data[0],
                    "Age": user_data[1],
                    "Gender": user_data[2],
                    "Phone Number": user_data[3],
                    # "Fitness Goal": user_data[4] # Removed
                }
                self.display_user_data()
            else:
                messagebox.showerror("Error", "User profile not found in database.")

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Failed to load profile: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            if conn:
                conn.close()

    def display_user_data(self):
        for key, entry_widget in self.entries.items():
            value = self.user_data.get(key, "")
            if isinstance(entry_widget, tk.StringVar):
                entry_widget.set(value if value else "Select Gender") # Adjusted default for Gender
            else:
                entry_widget.config(state='normal')
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, value)
                entry_widget.config(state='readonly')

    def toggle_edit_mode(self):
        if self.edit_button.cget("text") == "Edit Profile":
            self.edit_button.config(text="Cancel Edit", bg="#ffc107")
            self.save_button.config(state=tk.NORMAL)
            for key, entry_widget in self.entries.items():
                if key == "Phone Number":
                    entry_widget.config(state='readonly')
                elif isinstance(entry_widget, tk.StringVar):
                    self.gender_option_menu.config(state='normal')
                else:
                    entry_widget.config(state='normal')
        else:
            self.edit_button.config(text="Edit Profile", bg="#007bff")
            self.save_button.config(state=tk.DISABLED)
            self.load_user_profile() # Reload original data to discard changes
            for key, entry_widget in self.entries.items():
                if isinstance(entry_widget, tk.StringVar):
                    self.gender_option_menu.config(state='disabled')
                else:
                    entry_widget.config(state='readonly')


    def save_profile(self):
        new_name = self.entries["Name"].get()
        new_age = self.entries["Age"].get()
        new_gender = self.entries["Gender"].get()
        new_phone_number = self.entries["Phone Number"].get() # Retain for validation if needed, though readonly

        if new_gender == "Select Gender":
            messagebox.showerror("Error", "Please select your gender.")
            return

        if not all([new_name, new_age, new_gender, new_phone_number]): # Removed new_fitness_goal
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            new_age = int(new_age)
            if not str(new_phone_number).isdigit() or len(str(new_phone_number)) < 10:
                messagebox.showerror("Error", "Please enter a valid phone number.")
                return

            conn = None
            try:
                conn = sqlite3.connect("fitness_app.db")
                cursor = conn.cursor()
                # Removed fitness_goal from UPDATE query
                cursor.execute("""
                    UPDATE user_profile
                    SET name = ?, age = ?, gender = ?
                    WHERE id = ?
                """, (new_name, new_age, new_gender, self.user_id))
                conn.commit()
                # Update local user_data dictionary
                self.user_data = {
                    "Name": new_name,
                    "Age": new_age,
                    "Gender": new_gender,
                    "Phone Number": new_phone_number,
                }
                self.status_label.config(text="Profile updated successfully!", fg="green")
                self.toggle_edit_mode()
            except sqlite3.OperationalError as e:
                messagebox.showerror("Database Error", f"Failed to update profile: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            finally:
                if conn:
                    conn.close()

        except ValueError:
            messagebox.showerror("Error", "Age must be a number.")



