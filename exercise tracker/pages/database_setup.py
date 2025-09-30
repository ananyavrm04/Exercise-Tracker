import sqlite3

conn = sqlite3.connect("fitness_app.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS exercises")
cursor.execute("DROP TABLE IF EXISTS user_profile")
cursor.execute("DROP TABLE IF EXISTS workout_plan")
cursor.execute("DROP TABLE IF EXISTS completed_exercises")

cursor.execute("""
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    focus_area TEXT,
    exercise_type TEXT,
    target_body_part TEXT,
    exercise_name TEXT,
    exercise_steps TEXT,
    min_count_duration TEXT,
    benefit TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    phone_number TEXT UNIQUE,
    password TEXT NOT NULL
    -- fitness_goal TEXT -- Removed this column
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS workout_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT,
    body_part TEXT,
    focus_area TEXT,
    exercise_type TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS completed_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    exercise_name TEXT,
    date_completed INTEGER DEFAULT (strftime('%s','now')),
    start_time INTEGER,
    end_time INTEGER,
    duration INTEGER,
    reps_completed INTEGER,
    energy_level TEXT
)
""")
conn.commit()
conn.close()


print("Database schema updated successfully!")


