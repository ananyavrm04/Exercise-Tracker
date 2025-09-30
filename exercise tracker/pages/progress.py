import tkinter as tk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta


class ProgressPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.user_id = self.controller.logged_in_user_id

        self.create_widgets()
        self.load_monthly_progress()
        self.load_weekly_progress()  # <-- add weekly chart

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.main_frame = tk.Frame(self, bg="white", padx=50, pady=30)
        self.main_frame.pack(expand=True, fill="both")

        tk.Label(
            self.main_frame,
            text="📊 Your Progress Overview",
            font=("Arial", 24, "bold"),
            bg="white"
        ).pack(pady=(0, 20), anchor="center")

        # Labels
        self.total_workouts_label = tk.Label(
            self.main_frame, text="Total Workouts This Month: --",
            font=("Arial", 14), bg="white"
        )
        self.total_workouts_label.pack(pady=5, anchor="w")

        self.avg_duration_label = tk.Label(
            self.main_frame, text="Avg. Duration This Month: --",
            font=("Arial", 14), bg="white"
        )
        self.avg_duration_label.pack(pady=5, anchor="w")

        self.streak_label = tk.Label(
            self.main_frame, text="Current Streak: -- days",
            font=("Arial", 14), bg="white"
        )
        self.streak_label.pack(pady=5, anchor="w")

        tk.Frame(self.main_frame, height=20, bg="white").pack()

        # Graph frames
        self.monthly_graph_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief="solid")
        self.monthly_graph_frame.pack(pady=20, fill="both", expand=True)

        self.weekly_graph_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief="solid")
        self.weekly_graph_frame.pack(pady=20, fill="both", expand=True)

    def load_monthly_progress(self):
        if not self.user_id:
            return

        conn = None
        try:
            conn = sqlite3.connect("fitness_app.db")
            cursor = conn.cursor()
            today = datetime.now().date()

            monthly_data = {}
            for i in range(6):
                month_start_date = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
                month_end_date = (month_start_date.replace(month=month_start_date.month % 12 + 1, day=1) - timedelta(days=1))

                month_start_timestamp = int(datetime.combine(month_start_date, datetime.min.time()).timestamp())
                month_end_timestamp = int(datetime.combine(month_end_date, datetime.max.time()).timestamp())

                cursor.execute("""
                    SELECT COUNT(DISTINCT exercise_name), SUM(duration)
                    FROM completed_exercises
                    WHERE user_id = ? AND date_completed BETWEEN ? AND ?
                """, (self.user_id, month_start_timestamp, month_end_timestamp))

                result = cursor.fetchone()
                total_exercises_month = result[0] if result and result[0] else 0
                total_duration_month = result[1] if result and result[1] else 0

                month_name = month_start_date.strftime('%b %y')
                monthly_data[month_name] = {
                    'count': total_exercises_month,
                    'duration': total_duration_month
                }

            months_sorted = sorted(monthly_data.keys(), key=lambda x: datetime.strptime(x, '%b %y'))
            monthly_counts = [monthly_data[m]['count'] for m in months_sorted]

            # Update labels
            current_month_start_date = today.replace(day=1)
            current_month_start_timestamp = int(datetime.combine(current_month_start_date, datetime.min.time()).timestamp())
            current_month_end_timestamp = int(datetime.combine(today, datetime.max.time()).timestamp())

            cursor.execute("""
                SELECT COUNT(DISTINCT exercise_name), SUM(duration)
                FROM completed_exercises
                WHERE user_id = ? AND date_completed BETWEEN ? AND ?
            """, (self.user_id, current_month_start_timestamp, current_month_end_timestamp))
            current_month_result = cursor.fetchone()
            current_month_total_workouts = current_month_result[0] if current_month_result and current_month_result[0] else 0
            current_month_total_duration = current_month_result[1] if current_month_result and current_month_result[1] else 0

            current_month_avg_duration_min = round(current_month_total_duration / current_month_total_workouts / 60, 1) if current_month_total_workouts > 0 else 0

            # streak
            current_streak = 0
            for i in range(365):
                check_date = today - timedelta(days=i)
                start_ts = int(datetime.combine(check_date, datetime.min.time()).timestamp())
                end_ts = int(datetime.combine(check_date, datetime.max.time()).timestamp())

                cursor.execute("""
                    SELECT COUNT(DISTINCT exercise_name) FROM completed_exercises
                    WHERE user_id = ? AND date_completed BETWEEN ? AND ?
                """, (self.user_id, start_ts, end_ts))
                day_count = cursor.fetchone()[0]

                if day_count > 0:
                    current_streak += 1
                else:
                    if i == 0 or current_streak > 0:
                        break

            self.total_workouts_label.config(text=f"Total Workouts This Month: {current_month_total_workouts}")
            self.avg_duration_label.config(text=f"Avg. Duration This Month: {current_month_avg_duration_min} min")
            self.streak_label.config(text=f"Current Streak: {current_streak} days")

            # Clear old graph
            for widget in self.monthly_graph_frame.winfo_children():
                widget.destroy()

            if len(months_sorted) > 0 and max(monthly_counts) > 0:
                fig = plt.Figure(figsize=(7, 3.5), dpi=100)
                ax = fig.add_subplot(111)
                ax.bar(months_sorted, monthly_counts, color="#5eaaa8")
                ax.set_ylim(bottom=0)
                ax.set_title("Monthly Exercises Completed", fontsize=12)
                ax.set_xlabel("Month", fontsize=10)
                ax.set_ylabel("Exercises Count", fontsize=10)
                ax.grid(axis='y', linestyle='--', alpha=0.3)

                chart = FigureCanvasTkAgg(fig, master=self.monthly_graph_frame)
                chart.draw()
                chart.get_tk_widget().pack(fill="both", expand=True)
            else:
                tk.Label(self.monthly_graph_frame, text="No monthly workout data available yet.",
                         font=("Arial", 12), bg="white", fg="gray").pack(pady=20)

        except Exception as e:
            tk.Label(self.main_frame, text=f"Error: {e}", fg="red", bg="white").pack(pady=20)
        finally:
            if conn:
                conn.close()

    def load_weekly_progress(self):
        """Weekly chart moved here from HomePage"""
        if not self.user_id:
            return

        conn = None
        try:
            conn = sqlite3.connect("fitness_app.db")
            cursor = conn.cursor()
            today = datetime.now().date()

            dates_for_week = [(today - timedelta(days=i)).strftime("%b %d") for i in range(6, -1, -1)]
            weekly_completed_data = {}
            for i in range(7):
                current_date = today - timedelta(days=i)
                day_start = int(datetime.combine(current_date, datetime.min.time()).timestamp())
                day_end = int(datetime.combine(current_date, datetime.max.time()).timestamp())

                cursor.execute("""
                    SELECT COUNT(DISTINCT exercise_name) FROM completed_exercises
                    WHERE user_id = ? AND date_completed BETWEEN ? AND ?
                """, (self.user_id, day_start, day_end))
                weekly_completed_data[current_date] = cursor.fetchone()[0]

            graph_data_for_week = [weekly_completed_data.get((today - timedelta(days=i)), 0) for i in range(6, -1, -1)]

            for widget in self.weekly_graph_frame.winfo_children():
                widget.destroy()

            fig = plt.Figure(figsize=(7, 3), dpi=100)
            ax = fig.add_subplot(111)
            bars = ax.bar(dates_for_week, graph_data_for_week, color="#5eaaa8")
            ax.set_ylim(bottom=0)
            ax.set_title("Your Weekly Progress", fontsize=12)
            ax.set_xlabel("Date", fontsize=10)
            ax.set_ylabel("Exercises Count", fontsize=10)
            ax.grid(axis="y", linestyle="--", alpha=0.3)

            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f"{height}", xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3), textcoords="offset points",
                                ha="center", va="bottom", fontsize=8)

            chart = FigureCanvasTkAgg(fig, master=self.weekly_graph_frame)
            chart.draw()
            chart.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            tk.Label(self.weekly_graph_frame, text=f"No weekly workout data available: {e}",
                     font=("Arial", 12), bg="white", fg="gray").pack(pady=20)
        finally:
            if conn:
                conn.close()



