import pandas as pd
import sqlite3

# Excel se data load karo
df = pd.read_excel(r'pages/Wireframe_UYL - V1.xlsx', sheet_name='UYL Exercises')

# Sirf required columns select karo aur rename karo
df = df[['Sr. No.', 'Focus Area', 'Exercise Type', 'Target Body Part',
         'Exercise Name', 'Exercise Steps', 'Minimum Count / Duration', 'Benefit']]

df.columns = ['sr_no', 'focus_area', 'exercise_type', 'target_body_part',
              'exercise_name', 'exercise_steps', 'min_count_duration', 'benefit']

# Database me insert karo
conn = sqlite3.connect("fitness_app.db")
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO exercises 
        (focus_area, exercise_type, target_body_part, exercise_name, exercise_steps, min_count_duration, benefit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        row['focus_area'], row['exercise_type'], row['target_body_part'],
        row['exercise_name'], row['exercise_steps'], str(row['min_count_duration']), row['benefit']
    ))

conn.commit()
conn.close()

print("✅ All exercises inserted successfully!")



