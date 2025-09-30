import tkinter as tk
import sqlite3
from PIL import Image, ImageTk
from tkinter import messagebox
import winsound
import threading
import time
from tkinter import ttk
import os
import pygame.mixer

class ComplexPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.goal = None
        self.exercises_by_part = {}
        self.count_var = tk.IntVar(value=0)
        self.energy_var = tk.StringVar(value="")
        self.current_page = "goal"
        self.current_part = None
        self.show_goal_selection()

    def add_back_button(self):
        if self.current_page != "goal":
            tk.Button(self, text="← Back", bg="#f0f0f0", command=self.go_back).pack(anchor="nw", padx=10, pady=10)

    def go_back(self):
        if self.current_page == "body":
            self.show_goal_selection()
        elif self.current_page == "exercise":
            self.show_body_parts()
        elif self.current_page == "detail":
            self.show_exercises(self.current_part)

    def show_goal_selection(self):
        for widget in self.winfo_children(): widget.destroy()
        self.current_page = "goal"
        self.add_back_button() 

        main_frame = tk.Frame(self, bg="white")
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="Select Your Fitness Goal", font=("Arial", 30, "bold"), bg="white").pack(pady=(50, 60))

        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(pady=20)

        btn_style = {"width": 25, "height": 8, "bg": "#d0f0ff", "font": ("Arial", 16, "bold"), "relief": "raised", "bd": 3}

        tk.Button(btn_frame, text="Bone Mobility", **btn_style, command=lambda: self.load_exercises("bone mobility")).pack(side="left", padx=50)
        tk.Button(btn_frame, text="Muscle Strengthening", **btn_style, command=lambda: self.load_exercises("muscle strengthening")).pack(side="left", padx=50)

    def load_exercises(self, goal):
        self.goal = goal
        conn = None
        try:
            conn = sqlite3.connect("fitness_app.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT target_body_part, exercise_name, exercise_steps, min_count_duration, benefit
                FROM exercises WHERE LOWER(focus_area)=? AND LOWER(exercise_type)='complex'
            """, (goal,))
            self.exercises_by_part = {}
            for row in cursor.fetchall():
                self.exercises_by_part.setdefault(row[0], []).append(row[1:])
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Failed to load exercises: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            if conn:
                conn.close()
        self.show_body_parts()

    def show_body_parts(self):
        for widget in self.winfo_children(): widget.destroy()
        self.current_page = "body"
        self.add_back_button()

        tk.Label(self, text="Select a Body Part", font=("Arial", 18, "bold"), bg="white").pack(pady=10)
        btn_frame = tk.Frame(self, bg="white"); btn_frame.pack()
        for idx, part in enumerate(self.exercises_by_part):
            img = ImageTk.PhotoImage(Image.open(f"images/body_parts/{part.lower().replace(' ','_')}.png").resize((80,80)))
            card = tk.Frame(btn_frame, bd=1, relief="solid", bg="white"); card.grid(row=idx//4, column=idx%4, padx=20, pady=20)
            tk.Label(card, image=img, bg="white").pack(); card.image=img
            tk.Button(card, text=part, width=15, bg="#f2f2f2", command=lambda p=part:self.show_exercises(p)).pack()

    def show_exercises(self, part):
        for widget in self.winfo_children(): widget.destroy()
        self.current_page = "exercise"
        self.current_part = part
        self.add_back_button()

        tk.Label(self, text=f"{part} Exercises", font=("Arial",18,"bold"), bg="white").pack(pady=10)
        for ex in self.exercises_by_part[part]:
            name, steps, duration, benefit = ex
            f = tk.Frame(self, bg="white", bd=1, relief="solid"); f.pack(fill="x", padx=20, pady=8)
            tk.Label(f, text=name, font=("Arial",14,"bold"), bg="white").pack(anchor="w", padx=10)
            tk.Button(f, text="View & Start", bg="#d0f0ff", command=lambda n=name,s=steps,d=duration,b=benefit: self.detail(n,s,d,b)).pack(anchor="e", padx=10)

    def detail(self, name, steps, duration, benefit):
        for widget in self.winfo_children(): widget.destroy()
        self.current_page = "detail"
        self.add_back_button()

        content = tk.Frame(self, bg="white")
        content.pack(fill="both", expand=True, padx=30, pady=20)

        left = tk.Frame(content, bg="white")
        left.pack(side="left", fill="both", expand=True, padx=(0, 30), anchor="n")

        right = tk.Frame(content, bg="white")
        right.pack(side="right", fill="y", padx=0, anchor="n")

        tk.Label(left, text=name, font=("Arial", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 10))

        tk.Label(left, text="Description:", font=("Arial", 14, "underline"), bg="white").pack(anchor="w", pady=(5,0))
        tk.Label(left, text=steps, wraplength=500, bg="white", justify="left", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        tk.Label(left, text="Benefit:", font=("Arial", 14, "underline"), bg="white").pack(anchor="w", pady=(5,0))
        tk.Label(left, text=benefit, wraplength=500, bg="white", justify="left", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        tk.Label(left, text=f"Duration/Count: {duration}", font=("Arial", 14, "underline"), bg="white").pack(anchor="w", pady=(5,0))
        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        tk.Label(left, text="Times done:", font=("Arial", 14, "underline"), bg="white").pack(anchor="w", pady=(5,0))
        tk.Label(left, textvariable=self.count_var, bg="white", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))

        self.current_duration_text = duration
        parts = duration.lower().split()
        show_timer = len(parts) >= 2 and 'min' in parts[1]

        timer_widget = None
        if show_timer:
            timer_widget = Timer(right)
            try:
                timer_widget.duration_target = int(parts[0]) * 60
            except ValueError:
                timer_widget.duration_target = None
            timer_widget.pack(pady=(10, 20), anchor="n")

        tk.Label(right, text="Energy Level:", font=("Arial", 14, "underline"), bg="white").pack(pady=(15,0), anchor="center")
        self.energy_var = tk.StringVar(value="")
        tk.OptionMenu(right, self.energy_var, "Low", "Medium", "High").pack(pady=5, anchor="center")

        submit_reps_val = 0
        if not show_timer and len(parts) >= 2 and 'reps' in parts[1]:
            try:
                submit_reps_val = int(parts[0])
            except ValueError:
                pass

        tk.Button(right, text="Submit", bg="#4CAF50", fg="white",
                  height=2, width=20,
                  command=lambda: self.save(name, reps=submit_reps_val, timer=timer_widget)).pack(pady=(20, 10), anchor="center")

        if show_timer:
            btn_frame_bottom = tk.Frame(right, bg="white")
            btn_frame_bottom.pack(pady=5, anchor="center")
            tk.Button(btn_frame_bottom, text="Reset", bg="#f2f2f2",
                      height=2, width=10,
                      command=timer_widget.reset).pack(side="left", padx=5)
            tk.Button(btn_frame_bottom, text="Cancel", bg="#f2f2f2",
                      height=2, width=10,
                      command=timer_widget.cancel).pack(side="left", padx=5)

    def save(self, name, reps, timer):
        current_unix_timestamp = int(time.time())

        start_time_to_save = None
        end_time_to_save = None
        calculated_duration = 0

        if timer:
            if timer.start_timestamp is not None and timer.end_timestamp is not None:
                start_time_to_save = timer.start_timestamp
                end_time_to_save = timer.end_timestamp
                calculated_duration = end_time_to_save - start_time_to_save
            else:
                messagebox.showwarning("⚠️ Warning", "Timer was not started/stopped properly. Saving with 0 duration.")
                start_time_to_save = current_unix_timestamp
                end_time_to_save = current_unix_timestamp
        else:
            start_time_to_save = current_unix_timestamp
            end_time_to_save = current_unix_timestamp
            calculated_duration = 0

        if not self.energy_var.get():
            messagebox.showerror("⚠️ Error", "Please select energy level before submitting!")
            return

        conn = None
        try:
            conn = sqlite3.connect("fitness_app.db")
            cur = conn.cursor()
            cur.execute("SELECT id FROM user_profile ORDER BY id DESC LIMIT 1")
            user = cur.fetchone()
            user_id = user[0] if user else None

            if user_id:
                cur.execute("""INSERT INTO completed_exercises
                    (user_id, exercise_name, date_completed, start_time, end_time, duration, reps_completed, energy_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, name, current_unix_timestamp, start_time_to_save, end_time_to_save, calculated_duration, reps, self.energy_var.get()))
                conn.commit()
                self.count_var.set(self.count_var.get() + 1)
                messagebox.showinfo("✅ Saved", "Exercise saved!")
            else:
                messagebox.showerror("❌", "No user profile found. Please create one in User Info.")
        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Failed to save exercise: {e}. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            if conn:
                conn.close()

class Timer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.elapsed = 0
        self.running = False
        self.reps = 0
        self.duration_target = None
        self.start_timestamp = None
        self.end_timestamp = None
        self.stop_beep_flag = False
        self.beep_thread = None
        self.beep_started_after_target = False

        self.lbl = tk.Label(self, text="0d:00h:00m:00s:000ms", font=("Arial", 20))
        self.lbl.pack(pady=(10, 5))

        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=5)

        self.start_btn = tk.Button(btn_frame, text="Start", bg="#4CAF50", fg="white",
                                   height=2, width=15, command=self.start)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(btn_frame, text="Stop", bg="#FF5733", fg="white",
                                  height=2, width=15, command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(side="left", padx=5)

        self.times_up_label = None

    def start(self):
        if not self.running:
            self.running = True
            if self.start_timestamp is None:
                self.start_timestamp = time.time()
                self.elapsed = 0
            self.stop_all_beeps()
            self.beep_started_after_target = False
            self.update()
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

    def stop(self):
        if self.running:
            self.running = False
            self.end_timestamp = time.time()
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
        self.stop_all_beeps()

    def reset(self):
        self.stop()
        self.elapsed = 0
        self.start_timestamp = None
        self.end_timestamp = None
        self.lbl.config(text="0d:00h:00m:00s:000ms")
        self._clear_times_up()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.beep_started_after_target = False

    def cancel(self):
        self.reset()

    def stop_all_beeps(self):
        self.stop_beep_flag = True
        winsound.PlaySound(None, winsound.SND_PURGE)

    def _clear_times_up(self):
        if self.times_up_label:
            self.times_up_label.destroy()
            self.times_up_label = None

    def update(self):
        if self.running:
            current_time = time.time()
            if self.start_timestamp is not None:
                total_seconds = current_time - self.start_timestamp
                self.elapsed = int(total_seconds)
            else:
                total_seconds = 0

            days = int(total_seconds // 86400)
            hours = int((total_seconds % 86400) // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            milliseconds = int((total_seconds - int(total_seconds)) * 1000)

            self.lbl.config(text=f"{days}d:{hours:02d}h:{minutes:02d}m:{seconds:02d}s:{milliseconds:03d}ms")

            if self.duration_target is not None and self.elapsed >= self.duration_target:
                if not self.beep_started_after_target:
                    self.stop_beep_flag = False
                    self.beep_thread = threading.Thread(target=self.play_pattern_beep, daemon=True)
                    self.beep_thread.start()
                    self.beep_started_after_target = True

                if not self.times_up_label:
                    self.times_up_label = tk.Label(self, text="Time's up!", fg="red", font=("Arial", 14, "bold"), bg="white")
                    self.times_up_label.pack(pady=5)

            self.after(50, self.update)

    def responsive_sleep(self, duration_ms):
        steps = int(duration_ms / 10)
        for _ in range(steps):
            if self.stop_beep_flag:
                return True
            time.sleep(0.010)
        return False

    def play_pattern_beep(self):
        beep_duration = 100
        short_gap = 10
        long_gap = 800

        while not self.stop_beep_flag:
            for _ in range(3):
                winsound.Beep(1000, beep_duration)
                if self.stop_beep_flag: break
                
                if self.responsive_sleep(short_gap): break
            
            if self.stop_beep_flag: break

            if not self.stop_beep_flag:
                if self.responsive_sleep(long_gap): break