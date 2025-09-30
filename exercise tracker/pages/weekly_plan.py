import sqlite3
import random
from datetime import date, timedelta

def generate_weekly_plan(goal):
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()

    today = date.today()

    # Check if workout plan was already generated this week
    cursor.execute("""
        SELECT MAX(generated_on) FROM workout_plan 
        WHERE focus_area = ?
    """, (goal.lower(),))
    result = cursor.fetchone()[0]

    if result:
        last_generated = date.fromisoformat(result)
        if (today - last_generated).days < 7:
            print("⏳ Plan already generated this week. Skipping regeneration.")
            conn.close()
            return

    # Delete old plan
    cursor.execute("DELETE FROM workout_plan WHERE focus_area = ?", (goal.lower(),))

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day in days:
        cursor.execute("""
            SELECT target_body_part, exercise_name, exercise_type, benefit
            FROM exercises
            WHERE LOWER(focus_area) = ?
            ORDER BY RANDOM()
            LIMIT 1
        """, (goal.lower(),))
        
        row = cursor.fetchone()
        if row:
            target_body_part, exercise_name, exercise_type, benefit = row
            cursor.execute("""
                INSERT INTO workout_plan 
                (day, focus_area, target_body_part, exercise_name, exercise_type, benefit, generated_on)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (day, goal, target_body_part, exercise_name, exercise_type, benefit, today.isoformat()))

    conn.commit()
    conn.close()
    print(f" Weekly plan generated for {goal} on {today}.")


