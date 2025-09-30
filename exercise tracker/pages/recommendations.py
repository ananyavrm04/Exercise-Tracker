import tkinter as tk
from tkinter import ttk
import sqlite3
from utils.recommender import get_recommendations

class RecommendationsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.pack(expand=True, fill="both")
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="30 30 30 30")
        main_frame.pack(expand=True, fill="both")

        ttk.Label(
            main_frame,
            text="Your Personalized Recommendations",
            font=("Arial", 24, "bold"),
            foreground="#4CAF50"
        ).pack(pady=(10, 20))

        recs = []
        user_id = self.controller.logged_in_user_id
        if user_id:
            try:
                conn = sqlite3.connect("fitness_app.db")
                cursor = conn.cursor()

                # --- calculate progress ---
                def get_progress(ex_type):
                    cursor.execute(f"SELECT COUNT(DISTINCT exercise_name) FROM exercises WHERE LOWER(exercise_type) = ?", (ex_type,))
                    total = cursor.fetchone()[0]
                    cursor.execute("""SELECT COUNT(DISTINCT ce.exercise_name)
                                      FROM completed_exercises ce
                                      JOIN exercises e ON ce.exercise_name = e.exercise_name
                                      WHERE ce.user_id = ? AND LOWER(e.exercise_type) = ?""", (user_id, ex_type))
                    completed = cursor.fetchone()[0]
                    return round((completed / total) * 100, 1) if total > 0 else 0.0

                simple_progress = get_progress("simple")
                medium_progress = get_progress("medium")
                complex_progress = get_progress("complex")

                conn.close()

                # --- get recommendations ---
                recs = get_recommendations(
                    user_id,
                    db_path="fitness_app.db",
                    num_recommendations=5,
                    simple_progress=simple_progress,
                    medium_progress=medium_progress,
                    complex_progress=complex_progress
                )

                # --- format output safely ---
                recommendation_list = []
                for rec in recs:
                    if isinstance(rec, tuple):
                        name, etype = rec
                        if etype:  # only show if not empty
                            recommendation_list.append(f"• {name} ({etype.capitalize()})")
                        else:
                            recommendation_list.append(f"• {name}")
                    else:
                        recommendation_list.append(f"• {rec}")

            except Exception as e:
                recommendation_list = [f"Error loading recommendations: {e}"]
        else:
            recommendation_list = ["Login to get personalized recommendations!"]

        for rec_text in recommendation_list:
            ttk.Label(main_frame, text=rec_text, font=("Arial", 16), wraplength=700, justify="left").pack(pady=(2, 2), anchor="w")
