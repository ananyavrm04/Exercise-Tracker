import tkinter as tk
import sqlite3
from datetime import date
import tkinter.messagebox as messagebox

class WorkoutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")

        tk.Label(self, text="🗓️ Weekly Workout Plan", font=("Arial", 20, "bold"), bg="white").pack(pady=15)

        table = tk.Frame(self, bg="white")
        table.pack(padx=20, pady=10)

        headers = ["Day", "Exercise", "Type", "Target Body Part", "Benefit"]
        for i, h in enumerate(headers):
            tk.Label(table, text=h, font=("Arial", 10, "bold"), bg="#d0f0ff", width=25).grid(row=0, column=i, padx=5, pady=10)

        conn = None
        try:
            conn = sqlite3.connect("fitness_app.db")
            cursor = conn.cursor()

            cursor.execute("SELECT fitness_goal FROM user_profile ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()

            goal = None
            if row and row[0]:
                goal = str(row[0]).strip().lower()

            if goal:
                cursor.execute("""
                    SELECT day, exercise_name, exercise_type, target_body_part, benefit
                    FROM workout_plan
                    WHERE LOWER(focus_area) = ?
                    ORDER BY
                        CASE day
                            WHEN 'Monday' THEN 1
                            WHEN 'Tuesday' THEN 2
                            WHEN 'Wednesday' THEN 3
                            WHEN 'Thursday' THEN 4
                            WHEN 'Friday' THEN 5
                            WHEN 'Saturday' THEN 6
                            WHEN 'Sunday' THEN 7
                        END
                """, (goal,))

                for row_idx, row_data in enumerate(cursor.fetchall(), start=1):
                    bg = "#f9f9f9" if row_idx % 2 == 0 else "white"
                    for col_idx, val in enumerate(row_data):
                        tk.Label(table, text=val, wraplength=220, anchor="w", justify="left", bg=bg).grid(
                            row=row_idx, column=col_idx, sticky="w", padx=5, pady=6
                        )
            else:
                tk.Label(self, text="No fitness goal found. Please set your profile and goal in 'User Info'.",
                         font=("Arial", 12), fg="red", bg="white").pack(pady=20)

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Failed to load workout plan: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            if conn:
                conn.close()

