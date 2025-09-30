import tkinter as tk
import sqlite3
from tkinter import messagebox, ttk 

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.user_id = self.controller.logged_in_user_id

        # Theme management variables
        self.theme_var = tk.StringVar(value="Light") # Default theme
        self.theme_var.trace_add("write", self.apply_theme) # Call apply_theme when var changes

        self.create_widgets()
        self.load_settings() # Load any saved settings

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self, bg="white", padx=50, pady=30)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="⚙️ Settings", font=("Arial", 24, "bold"), bg="white").pack(pady=(0, 20), anchor="center")

        # --- Theme Settings ---
        theme_frame = tk.LabelFrame(main_frame, text="App Theme", font=("Arial", 16, "bold"), bg="white", bd=2, relief="groove", padx=20, pady=10)
        theme_frame.pack(pady=15, fill="x", expand=True)

        tk.Radiobutton(theme_frame, text="Light Mode", variable=self.theme_var, value="Light", font=("Arial", 12), bg="white", command=self.save_theme_setting).pack(anchor="w", pady=5)
        tk.Radiobutton(theme_frame, text="Dark Mode", variable=self.theme_var, value="Dark", font=("Arial", 12), bg="white", command=self.save_theme_setting).pack(anchor="w", pady=5)

        # --- Profile & Account Settings ---
        account_frame = tk.LabelFrame(main_frame, text="Account & Profile", font=("Arial", 16, "bold"), bg="white", bd=2, relief="groove", padx=20, pady=10)
        account_frame.pack(pady=15, fill="x", expand=True)

        tk.Button(account_frame, text="Edit Profile Info", font=("Arial", 12), bg="#d0f0ff", command=lambda: self.controller.show_page("user")).pack(pady=5, anchor="w")
        tk.Button(account_frame, text="Change Password", font=("Arial", 12), bg="#d0f0ff", command=self.show_change_password_dialog).pack(pady=5, anchor="w")
        
        # --- Notification Settings (Placeholder for now) ---
        notification_frame = tk.LabelFrame(main_frame, text="Notifications", font=("Arial", 16, "bold"), bg="white", bd=2, relief="groove", padx=20, pady=10)
        notification_frame.pack(pady=15, fill="x", expand=True)
        tk.Label(notification_frame, text="Future: Control exercise reminders, alerts.", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)

        # --- Data Management (Placeholder for now) ---
        data_frame = tk.LabelFrame(main_frame, text="Data Management", font=("Arial", 16, "bold"), bg="white", bd=2, relief="groove", padx=20, pady=10)
        data_frame.pack(pady=15, fill="x", expand=True)
        tk.Button(data_frame, text="Export My Data (CSV)", font=("Arial", 12), bg="#d0f0ff", command=lambda: messagebox.showinfo("Coming Soon", "Data export feature is under development!")).pack(pady=5, anchor="w")
        tk.Button(data_frame, text="Reset All Progress", font=("Arial", 12), bg="#ff5733", fg="white", command=lambda: messagebox.askyesno("Confirm Reset", "Are you sure you want to reset ALL your exercise progress? This cannot be undone!")).pack(pady=5, anchor="w")


    def load_settings(self):
        self.apply_theme()

    def save_theme_setting(self):
        self.apply_theme()
        messagebox.showinfo("Theme Applied", f"Theme set to {self.theme_var.get()} Mode.")

    def apply_theme(self, *args): # *args to accept trace_add arguments
        current_theme = self.theme_var.get()
        if current_theme == "Dark":
            bg_color = "#2e2e2e" # Dark background
            fg_color = "white"   # Light text
            button_bg = "#4a4a4a"
            button_fg = "white"
            frame_bg = "#3a3a3a"
        else: # Light mode
            bg_color = "white"
            fg_color = "black"
            button_bg = "#d0f0ff"
            button_fg = "black"
            frame_bg = "white" # Labels and frames will use this

        # Apply theme to self (the page frame)
        self.config(bg=bg_color)
        
        # Apply theme to all child widgets recursively
        self._apply_theme_to_widgets(self, bg_color, fg_color, button_bg, button_fg, frame_bg)

        # Special handling for controller's main window (App)
        # This part assumes controller is the App instance
        if hasattr(self.controller, 'configure'):
            self.controller.configure(bg=bg_color)
        if hasattr(self.controller, 'sidebar'):
            self.controller.sidebar.config(bg=frame_bg)
            for btn in self.controller.sidebar_buttons:
                btn.config(bg=button_bg, fg=button_fg)
        if hasattr(self.controller, 'banner'):
            self.controller.banner.config(bg=button_bg)
            for widget in self.controller.banner.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg=button_bg, fg=button_fg)
        if hasattr(self.controller, 'main_content_wrapper'):
            self.controller.main_content_wrapper.config(bg=bg_color)
        if hasattr(self.controller, 'canvas'):
            self.controller.canvas.config(bg=bg_color)
        if hasattr(self.controller, 'scrollable_frame'):
            self.controller.scrollable_frame.config(bg=bg_color)
            # Re-apply theme to currently displayed page if any
            for widget in self.controller.scrollable_frame.winfo_children():
                self._apply_theme_to_widgets(widget, bg_color, fg_color, button_bg, button_fg, frame_bg)


    def _apply_theme_to_widgets(self, parent_widget, bg_color, fg_color, button_bg, button_fg, frame_bg):
        for widget in parent_widget.winfo_children():
            try:
                if isinstance(widget, (tk.Label, tk.Radiobutton)):
                    widget.config(bg=frame_bg, fg=fg_color)
                elif isinstance(widget, tk.Button):
                    widget.config(bg=button_bg, fg=button_fg)
                elif isinstance(widget, (tk.Frame, tk.LabelFrame)):
                    widget.config(bg=frame_bg)
                elif isinstance(widget, ttk.Scrollbar): # ttk widgets might need different config
                    pass # ttk widgets are themed separately, often don't need direct bg/fg
                # Recursively apply to children
                self._apply_theme_to_widgets(widget, bg_color, fg_color, button_bg, button_fg, frame_bg)
            except tk.TclError: # Catch error if widget doesn't have config option
                pass # Some widgets (like canvas inside chart) might not have direct bg/fg config

    def show_change_password_dialog(self):
        # Simple dialog for changing password
        dialog = tk.Toplevel(self)
        dialog.title("Change Password")
        dialog.transient(self.controller) # Make it modal
        dialog.grab_set() # Grab input
        dialog.geometry("300x200")
        dialog.config(bg="white")

        tk.Label(dialog, text="New Password:", bg="white").pack(pady=10)
        new_pass_entry = tk.Entry(dialog, show="*")
        new_pass_entry.pack()

        tk.Label(dialog, text="Confirm Password:", bg="white").pack(pady=5)
        confirm_pass_entry = tk.Entry(dialog, show="*")
        confirm_pass_entry.pack()

        def save_new_password():
            new_pass = new_pass_entry.get()
            confirm_pass = confirm_pass_entry.get()

            if not new_pass or not confirm_pass:
                messagebox.showerror("Error", "Please enter both new and confirm passwords.", parent=dialog)
                return
            if new_pass != confirm_pass:
                messagebox.showerror("Error", "Passwords do not match.", parent=dialog)
                return
            
            # Hash and save to DB
            hashed_password = self.hash_password(new_pass)
            conn = None
            try:
                conn = sqlite3.connect("fitness_app.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE user_profile SET password = ? WHERE id = ?", (hashed_password, self.user_id))
                conn.commit()
                messagebox.showinfo("Success", "Password changed successfully!", parent=dialog)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to change password: {e}", parent=dialog)
            finally:
                if conn:
                    conn.close()

        tk.Button(dialog, text="Save", command=save_new_password, bg="#4CAF50", fg="white").pack(pady=10)
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy) # Handle window close button
        self.controller.wait_window(dialog) # Wait for dialog to close

    def hash_password(self, password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

