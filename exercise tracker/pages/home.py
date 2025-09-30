import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from datetime import datetime, timedelta, time as dt_time
from utils.recommender import get_recommendations
from tkinter import ttk


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        user_name = "User"
        overall_progress_percentage = 0.0
        simple_progress_percentage = 0.0
        medium_progress_percentage = 0.0
        complex_progress_percentage = 0.0

        conn = None
        try:
            conn = sqlite3.connect("fitness_app.db")
            cursor = conn.cursor()

            user_id = self.controller.logged_in_user_id
            if user_id:
                cursor.execute("SELECT name FROM user_profile WHERE id = ?", (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    user_name = user_data[0]

            cursor.execute("SELECT COUNT(DISTINCT exercise_name) FROM exercises")
            total_unique_exercises_overall = cursor.fetchone()[0]

            if user_id and total_unique_exercises_overall > 0:
                cursor.execute(
                    "SELECT COUNT(DISTINCT exercise_name) FROM completed_exercises WHERE user_id = ?",
                    (user_id,),
                )
                completed_unique_exercises_overall = cursor.fetchone()[0]
                overall_progress_percentage = (
                    completed_unique_exercises_overall / total_unique_exercises_overall
                ) * 100
                overall_progress_percentage = round(overall_progress_percentage, 1)

            def calculate_type_progress(exercise_type):
                if not user_id:
                    return 0.0

                cursor.execute(
                    "SELECT COUNT(DISTINCT exercise_name) FROM exercises WHERE LOWER(exercise_type) = ?",
                    (exercise_type,),
                )
                total_type_exercises = cursor.fetchone()[0]

                if total_type_exercises == 0:
                    return 0.0

                cursor.execute(
                    """
                    SELECT COUNT(DISTINCT ce.exercise_name)
                    FROM completed_exercises ce
                    JOIN exercises e ON ce.exercise_name = e.exercise_name
                    WHERE ce.user_id = ? AND LOWER(e.exercise_type) = ?
                """,
                    (user_id, exercise_type),
                )
                completed_type_exercises = cursor.fetchone()[0]

                return round((completed_type_exercises / total_type_exercises) * 100, 1)

            simple_progress_percentage = calculate_type_progress("simple")
            medium_progress_percentage = calculate_type_progress("medium")
            complex_progress_percentage = calculate_type_progress("complex")

        except Exception as e:
            print(f"Error on Home Page: {e}")
        finally:
            if conn:
                conn.close()

        # --- UI Layout ---
        main_content_frame = ttk.Frame(self, padding="30 30 30 30")
        main_content_frame.pack(expand=True, fill="both")

        # Top Section: Welcome (Left) + Recommendations Table (Right)
        top_section_frame = ttk.Frame(main_content_frame)
        top_section_frame.pack(fill="x", pady=(0, 20))

        # Left: Welcome Message
        welcome_frame = ttk.Frame(top_section_frame)
        welcome_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        self.full_text = f"Welcome, {user_name}!... (Your Progress % : {overall_progress_percentage})"
        self.animated_label = ttk.Label(welcome_frame, text="", font=("Arial", 28, "bold"))
        self.animated_label.pack(pady=(0, 10), anchor="w")

        self.animate_index = 0
        self.animate_text()

        # Right: Recommendations Table
        rec_frame = ttk.Frame(top_section_frame, relief="solid", borderwidth=1, padding="10 10 10 10")
        rec_frame.pack(side="right", fill="both", expand=True)

        ttk.Label(
            rec_frame,
            text="Your Personalized Recommendations",
            font=("Arial", 16, "bold"),
            foreground="green"
        ).pack(pady=(0, 10))

        recs = get_recommendations(self.controller.logged_in_user_id)

        # Parse into (exercise_name, type)
        parsed_recs = []
        for r in recs:
            if isinstance(r, tuple) and len(r) == 2:
                parsed_recs.append(r)
            elif isinstance(r, str):
                if "(" in r and ")" in r:
                    name, etype = r.rsplit("(", 1)
                    parsed_recs.append((name.strip(), etype.strip(") ")))
                else:
                    parsed_recs.append((r.strip(), "Unknown"))

        # Table
        table_frame = tk.Frame(rec_frame, bg="white")
        table_frame.pack(fill="both", expand=True)

        headers = ["Category", "Exercise Name", "Action"]
        for col, header in enumerate(headers):
            tk.Label(
                table_frame,
                text=header,
                font=("Arial", 12, "bold"),
                bg="#e6e6e6",
                relief="solid",
                borderwidth=1,
                width=20
            ).grid(row=0, column=col, sticky="nsew")

        # Populate rows
        for i, (name, etype) in enumerate(parsed_recs, start=1):
            bg_color = "#ffffff" if i % 2 == 0 else "#f9f9f9"

            tk.Label(
                table_frame,
                text=etype.capitalize() if etype else "N/A",
                font=("Arial", 11),
                bg=bg_color,
                relief="solid",
                borderwidth=1,
                width=15
            ).grid(row=i, column=0, sticky="nsew")

            tk.Label(
                table_frame,
                text=name,
                font=("Arial", 11),
                bg=bg_color,
                relief="solid",
                borderwidth=1,
                width=30,
                anchor="w"
            ).grid(row=i, column=1, sticky="nsew")

            btn = tk.Button(
                table_frame,
                text="Go ▶",
                bg="#4CAF50",
                fg="white",
                font=("Arial", 9, "bold"),
                command=lambda t=etype.lower(): self.controller.show_page(t) if t in ["simple", "medium", "complex"] else None
            )
            btn.grid(row=i, column=2, sticky="nsew")

        for col in range(3):
            table_frame.grid_columnconfigure(col, weight=1)

        # Levels (below)
        ttk.Label(
            main_content_frame,
            text="What would you like to do today?",
            font=("Arial", 22, "bold"),
        ).pack(pady=(20, 25), anchor="center")

        levels_frame = ttk.Frame(main_content_frame)
        levels_frame.pack(pady=(0, 20), anchor="center")
        self.levels_frame = levels_frame

        levels = [
            ("Simple", f"images/simple.png", "simple", simple_progress_percentage),
            ("Medium", f"images/medium.png", "medium", medium_progress_percentage),
            ("Complex", f"images/complex.png", "complex", complex_progress_percentage),
        ]

        for label_text, img_path, page_name, progress_val in levels:
            img = Image.open(img_path)
            img = img.resize((200, 140))
            photo = ImageTk.PhotoImage(img)

            card_frame = ttk.Frame(levels_frame, relief="raised", padding="10 10 10 10")
            card_frame.pack(side="left", padx=30, expand=True)

            tk.Button(
                card_frame, image=photo, command=lambda p=page_name: controller.show_page(p), bd=0
            ).pack(pady=(0, 5))
            ttk.Label(card_frame, text=f"{label_text} ({progress_val}%)", font=("Arial", 12)).pack(
                pady=(0, 10)
            )

            setattr(self, f"{label_text.lower()}_img", photo)

    def animate_text(self):
        if self.animate_index <= len(self.full_text):
            current = self.full_text[: self.animate_index]
            self.animated_label.config(text=current)
            self.animate_index += 1
            self.after(100, self.animate_text)

    def apply_theme(self, bg_color, fg_color, button_bg, button_fg, frame_bg):
        self.config(bg=bg_color)
        style = ttk.Style()
        style.theme_use("default")

        style.configure(".", background=frame_bg, foreground=fg_color)
        style.configure("TFrame", background=frame_bg)
        style.configure("TLabel", background=frame_bg, foreground=fg_color)
        style.configure("Card.TFrame", background=frame_bg)
        style.configure("Card.TLabel", background=frame_bg, foreground=fg_color)

        self.animated_label.config(background=frame_bg, foreground=fg_color)

