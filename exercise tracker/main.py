import tkinter as tk
import tkinter.messagebox as messagebox
import sqlite3
from tkinter import ttk
from PIL import Image, ImageTk
import pygame.mixer

from pages.home import HomePage
from pages.simple import SimplePage
from pages.medium import MediumPage
from pages.complex import ComplexPage
from pages.user import UserPage
from pages.workout import WorkoutPage
from pages.login_signup import LoginSignupPage
from pages.create_account import CreateAccountPage
from pages.progress import ProgressPage
from pages.settings import SettingsPage
from pages.recommendations import RecommendationsPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Exercise Tracker")
        self.geometry("1000x600")
        self.configure(bg="white")

        self.logged_in_user_id = None

        self.sidebar = tk.Frame(self, width=200, bg="#f0f0f0")
        self.sidebar.pack(side="left", fill="y")

        self.banner = tk.Frame(self, height=60, bg="#ffd700")
        self.banner.pack(side="top", fill="x")

        tk.Label(
            self.banner,
            text="Urban Yogi Lifestyle",
            font=("Arial", 22, "bold"),
            bg="#ffd700",
            fg="black"
        ).pack(pady=10)

        self.main_content_wrapper = tk.Frame(self, bg="white")
        self.main_content_wrapper.pack(side="right", expand=True, fill="both")

        self.canvas = tk.Canvas(self.main_content_wrapper, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_content_wrapper, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window_id, width=e.width)
        )

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.sidebar_buttons = []
        self.sidebar_buttons.append(self.add_sidebar_button("🏠 Home", lambda: self.show_page("home")))
        self.sidebar_buttons.append(self.add_sidebar_button("📆 Workout Plan", lambda: self.show_page("workout")))
        self.sidebar_buttons.append(self.add_sidebar_button("🙍 User Info", lambda: self.show_page("user")))
        self.sidebar_buttons.append(self.add_sidebar_button("📊 Progress", lambda: self.show_page("progress")))
        self.sidebar_buttons.append(self.add_sidebar_button("🤖 Recommendations", lambda: self.show_page("recommendations")))
        self.sidebar_buttons.append(self.add_sidebar_button("⚙️ Settings", lambda: self.show_page("settings")))
        
        self.disable_sidebar_buttons()

        self.current_theme_colors = {
            "theme_name": "Light",
            "bg_color": "white",
            "fg_color": "black",
            "button_bg": "#f0f0f0",
            "button_fg": "black",
            "frame_bg": "white"
        }
        
        try:
            pygame.mixer.init()
        except Exception as e:
            messagebox.showerror("Pygame Error", f"Failed to initialize Pygame mixer: {e}")

        self.show_page("login_signup")

    def add_sidebar_button(self, text, command):
        button = tk.Button(self.sidebar, text=text, anchor="w", bg="#f0f0f0",
                            relief="flat", padx=20, command=command)
        button.pack(fill="x", pady=5)
        return button

    def enable_sidebar_buttons(self):
        for button in self.sidebar_buttons:
            button.config(state=tk.NORMAL)

    def disable_sidebar_buttons(self):
        for button in self.sidebar_buttons:
            button.config(state=tk.DISABLED)

    def show_page(self, page_name):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        user_age = None
        if self.logged_in_user_id and page_name not in ["login_signup", "create_account"]:
            conn = None
            try:
                conn = sqlite3.connect("fitness_app.db")
                cursor = conn.cursor()
                cursor.execute("SELECT age FROM user_profile WHERE id = ?", (self.logged_in_user_id,))
                age_row = cursor.fetchone()
                if age_row:
                    user_age = age_row[0]
            except Exception as e:
                print(f"Error fetching user age: {e}")
            finally:
                if conn:
                    conn.close()

        if user_age:
            if page_name == "complex":
                if user_age >= 60:
                    messagebox.showwarning("⚠️ Suggestion", "You're advised to follow SIMPLE exercises due to your age.")
                    return
                elif user_age > 40:
                    messagebox.showinfo("💡 Suggestion", "You might find MEDIUM exercises more suitable than COMPLEX.")
            elif page_name == "medium" and user_age >= 60:
                messagebox.showwarning("⚠️ Suggestion", "You're advised to follow SIMPLE exercises due to your age.")
                return

        page = None
        if page_name == "login_signup":
            page = LoginSignupPage(self.scrollable_frame, self)
            self.disable_sidebar_buttons()
        elif page_name == "create_account":
            page = CreateAccountPage(self.scrollable_frame, self)
            self.disable_sidebar_buttons()
        elif page_name == "home":
            if self.logged_in_user_id is None:
                messagebox.showwarning("Access Denied", "Please login to access this page.")
                self.show_page("login_signup")
                return
            page = HomePage(self.scrollable_frame, self)
            self.enable_sidebar_buttons()
        elif page_name == "simple":
            if self.logged_in_user_id is None:
                messagebox.showwarning("Access Denied", "Please login to access this page.")
                self.show_page("login_signup")
                return
            page = SimplePage(self.scrollable_frame, self)
        elif page_name == "medium":
            if self.logged_in_user_id is None:
                messagebox.showwarning("Access Denied", "Please login to access this page.")
                self.show_page("login_signup")
                return
            page = MediumPage(self.scrollable_frame, self)
        elif page_name == "complex":
            if self.logged_in_user_id is None:
                messagebox.showwarning("Access Denied", "Please login to access this page.")
                self.show_page("login_signup")
                return
            page = ComplexPage(self.scrollable_frame, self)
        elif page_name == "user":
            if self.logged_in_user_id is None:
                messagebox.showwarning("Access Denied", "Please login to access this page.")
                self.show_page("login_signup")
                return
            page = UserPage(self.scrollable_frame, self)
        elif page_name == "workout":
            if self.logged_in_user_id is None:
                messagebox.showwarning("Access Denied", "Please login to access this page.")
                self.show_page("login_signup")
                return
            page = WorkoutPage(self.scrollable_frame, self)
        elif page_name == "progress":
            if self.logged_in_user_id is None:
                messagebox.showwarning("Access Denied", "Please login to access this page.")
                self.show_page("login_signup")
                return
            page = ProgressPage(self.scrollable_frame, self)
        elif page_name == "recommendations":
            if self.logged_in_user_id is None:
                messagebox.showwarning("Access Denied", "Please login to access this page.")
                self.show_page("login_signup")
                return
            page = RecommendationsPage(self.scrollable_frame, self)
        elif page_name == "settings":
            if self.logged_in_user_id is None:
                messagebox.showwarning("Access Denied", "Please login to access this page.")
                self.show_page("login_signup")
                return
            page = SettingsPage(self.scrollable_frame, self)
        else:
            page = tk.Label(self.scrollable_frame, text="Page not found", font=("Arial", 16))

        if page:
            page.pack(fill="both", expand=True)
        self.canvas.yview_moveto(0)

        if hasattr(page, 'apply_theme'):
            page.apply_theme(self.current_theme_colors['bg_color'], 
                             self.current_theme_colors['fg_color'], 
                             self.current_theme_colors['button_bg'], 
                             self.current_theme_colors['button_fg'], 
                             self.current_theme_colors['frame_bg'])
        else:
            self._apply_theme_to_widgets(page, self.current_theme_colors['bg_color'], 
                                         self.current_theme_colors['fg_color'], 
                                         self.current_theme_colors['button_bg'], 
                                         self.current_theme_colors['button_fg'], 
                                         self.current_theme_colors['frame_bg'])


    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _apply_theme_to_widgets(self, parent_widget, bg_color, fg_color, button_bg, button_fg, frame_bg):
        preserved_button_bgs = ["#4CAF50", "#FF5733", "#007bff", "#ffc107", "#d0f0ff", "#f2f2f2"]
        for widget in parent_widget.winfo_children():
            if isinstance(widget, ttk.Widget):
                pass
            else:
                try:
                    if isinstance(widget, (tk.Label, tk.Radiobutton, tk.Checkbutton, tk.OptionMenu)):
                        widget.config(background=frame_bg, foreground=fg_color)
                    elif isinstance(widget, tk.Button):
                        current_widget_bg = widget.cget("background")
                        if current_widget_bg in preserved_button_bgs:
                            if fg_color == "white" and current_widget_bg == "#f2f2f2":
                                widget.config(foreground="black")
                            elif fg_color == "black" and current_widget_bg == "#d0f0ff":
                                widget.config(foreground="black")
                            else:
                                widget.config(foreground=button_fg)
                        else:
                            widget.config(background=button_bg, foreground=button_fg)
                    elif isinstance(widget, (tk.Frame, tk.LabelFrame)):
                        widget.config(background=frame_bg)
                    elif isinstance(widget, tk.Entry):
                        widget.config(background=frame_bg, foreground=fg_color, insertbackground=fg_color)
                    elif isinstance(widget, tk.Canvas):
                        widget.config(background=frame_bg)
                    
                except tk.TclError:
                    pass
            
            self._apply_theme_to_widgets(widget, bg_color, fg_color, button_bg, button_fg, frame_bg)

    def set_app_theme(self, theme_name):
        if theme_name == "Dark":
            self.current_theme_colors = {
                "theme_name": "Dark",
                "bg_color": "#2e2e2e",
                "fg_color": "white",
                "button_bg": "#4a4a4a",
                "button_fg": "white",
                "frame_bg": "#3a3a3a"
            }
        else:
            self.current_theme_colors = {
                "theme_name": "Light",
                "bg_color": "white",
                "fg_color": "black",
                "button_bg": "#f0f0f0",
                "button_fg": "black",
                "frame_bg": "white"
            }
        
        self.configure(bg=self.current_theme_colors['bg_color'])
        self.sidebar.config(bg=self.current_theme_colors['frame_bg'])
        self.banner.config(bg=self.current_theme_colors['button_bg'])
        for widget in self.banner.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=self.current_theme_colors['button_bg'], fg=self.current_theme_colors['button_fg'])

        for btn in self.sidebar_buttons:
            btn.config(bg=self.current_theme_colors['button_bg'], fg=self.current_theme_colors['button_fg'])
        
        self.main_content_wrapper.config(bg=self.current_theme_colors['bg_color'])
        self.canvas.config(bg=self.current_theme_colors['bg_color'])
        self.scrollable_frame.config(bg=self.current_theme_colors['bg_color'])

        current_page_widgets = self.scrollable_frame.winfo_children()
        if current_page_widgets:
            self._apply_theme_to_widgets(current_page_widgets[0], 
                                         self.current_theme_colors['bg_color'], 
                                         self.current_theme_colors['fg_color'], 
                                         self.current_theme_colors['button_bg'], 
                                         self.current_theme_colors['button_fg'], 
                                         self.current_theme_colors['frame_bg'])


if __name__ == "__main__":
    app = App()
    app.mainloop()


