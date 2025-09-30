import sqlite3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
import time

def get_recommendations(user_id, db_path="fitness_app.db", num_recommendations=3,
                        simple_progress=0.0, medium_progress=0.0, complex_progress=0.0):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # --- Load all exercises ---
        cursor.execute("SELECT exercise_name, focus_area, exercise_type, target_body_part FROM exercises")
        all_exercises_data = cursor.fetchall()
        all_exercises_df = pd.DataFrame(all_exercises_data,
                                        columns=['exercise_name', 'focus_area', 'exercise_type', 'target_body_part'])

        # --- Load user completed exercises ---
        cursor.execute("""
            SELECT e.exercise_name, e.focus_area, e.exercise_type, e.target_body_part, ce.energy_level, ce.date_completed
            FROM completed_exercises ce
            JOIN exercises e ON ce.exercise_name = e.exercise_name
            WHERE ce.user_id = ?
            ORDER BY ce.date_completed DESC
        """, (user_id,))
        user_completed_data = cursor.fetchall()
        user_completed_df = pd.DataFrame(user_completed_data,
                                         columns=['exercise_name', 'focus_area', 'exercise_type',
                                                  'target_body_part', 'energy_level', 'date_completed'])

        if all_exercises_df.empty:
            return [("No exercises available in the library.", "")]

        # --- Feature Engineering ---
        all_unique_features_flat = []
        for _, row in all_exercises_df.iterrows():
            if pd.notna(row['focus_area']) and str(row['focus_area']).strip():
                all_unique_features_flat.append(str(row['focus_area']).strip())
            if pd.notna(row['exercise_type']) and str(row['exercise_type']).strip():
                all_unique_features_flat.append(str(row['exercise_type']).strip())
            if pd.notna(row['target_body_part']) and str(row['target_body_part']).strip():
                all_unique_features_flat.append(str(row['target_body_part']).strip())

        mlb = MultiLabelBinarizer()
        mlb.fit([list(set(all_unique_features_flat))])

        features_for_all_exercises_transform = []
        for _, row in all_exercises_df.iterrows():
            current_features = []
            if pd.notna(row['focus_area']) and str(row['focus_area']).strip():
                current_features.append(str(row['focus_area']).strip())
            if pd.notna(row['exercise_type']) and str(row['exercise_type']).strip():
                current_features.append(str(row['exercise_type']).strip())
            if pd.notna(row['target_body_part']) and str(row['target_body_part']).strip():
                current_features.append(str(row['target_body_part']).strip())
            features_for_all_exercises_transform.append(current_features)

        features_matrix = mlb.transform(features_for_all_exercises_transform)
        features_df = pd.DataFrame(features_matrix, columns=mlb.classes_,
                                   index=all_exercises_df['exercise_name'])

        # --- Recommendation Strategy ---
        recommendation_strategy = "default"
        is_eligible_for_complex = False

        if not user_completed_df.empty and medium_progress >= 50.0:
            one_week_ago = time.time() - 7 * 86400
            last_week_data = user_completed_df[user_completed_df['date_completed'] >= one_week_ago]

            if not last_week_data.empty:
                medium_high_energy_count = last_week_data[
                    (last_week_data['exercise_type'].str.lower() == 'medium') &
                    (last_week_data['energy_level'].str.lower() == 'high')
                ].shape[0]

                medium_total = last_week_data[
                    last_week_data['exercise_type'].str.lower() == 'medium'
                ].shape[0]

                if medium_total > 0 and (medium_high_energy_count / medium_total) >= 0.7:
                    is_eligible_for_complex = True

        if is_eligible_for_complex:
            recommendation_strategy = "complex_and_simple"
        elif user_completed_df.empty:
            recommendation_strategy = "new_user"

        recommended_exercises_output = []
        added_recommendations_set = set()

        # Exclude already completed
        completed_exercise_names = user_completed_df['exercise_name'].unique()
        uncompleted_exercises_df = all_exercises_df[
            ~all_exercises_df['exercise_name'].isin(completed_exercise_names)
        ].copy()

        if uncompleted_exercises_df.empty:
            return [("You've completed all available exercises! Great job!", "")]

        # --- Case 1: New User ---
        if recommendation_strategy == "new_user":
            user_age = None
            cursor.execute("SELECT age FROM user_profile WHERE id = ?", (user_id,))
            age_row = cursor.fetchone()
            if age_row:
                user_age = age_row[0]

            if user_age is not None:
                if user_age >= 60:
                    suggested_type = 'simple'
                elif user_age > 40:
                    suggested_type = 'medium'
                else:
                    suggested_type = 'complex'

                recs_from_type = uncompleted_exercises_df[
                    uncompleted_exercises_df['exercise_type'].str.lower() == suggested_type
                ].copy()

                if not recs_from_type.empty:
                    for _, rec in recs_from_type.sample(
                            n=min(num_recommendations, len(recs_from_type))).iterrows():
                        recommended_exercises_output.append((rec['exercise_name'], rec['exercise_type']))
                    return recommended_exercises_output

            return [("Complete your first exercise to get personalized recommendations!", "")]

        # --- Case 2: Complex + Simple Mix ---
        elif recommendation_strategy == "complex_and_simple":
            complex_recs = uncompleted_exercises_df[
                uncompleted_exercises_df['exercise_type'].str.lower() == 'complex'
            ].copy()
            if not complex_recs.empty:
                for _, rec in complex_recs.sample(n=min(2, len(complex_recs))).iterrows():
                    recommended_exercises_output.append((rec['exercise_name'], rec['exercise_type']))
                    added_recommendations_set.add(rec['exercise_name'])

            if len(recommended_exercises_output) < num_recommendations:
                simple_recs = uncompleted_exercises_df[
                    uncompleted_exercises_df['exercise_type'].str.lower() == 'simple'
                ].copy()
                simple_recs = simple_recs[~simple_recs['exercise_name'].isin(added_recommendations_set)]
                if not simple_recs.empty:
                    for _, rec in simple_recs.sample(
                            n=min(num_recommendations - len(recommended_exercises_output), len(simple_recs))
                    ).iterrows():
                        recommended_exercises_output.append((rec['exercise_name'], rec['exercise_type']))
                        added_recommendations_set.add(rec['exercise_name'])

            if len(recommended_exercises_output) < num_recommendations:
                fallback_recs = uncompleted_exercises_df[
                    ~uncompleted_exercises_df['exercise_name'].isin(added_recommendations_set)
                ].copy()
                for _, rec in fallback_recs.sample(
                        n=min(num_recommendations - len(recommended_exercises_output), len(fallback_recs))
                ).iterrows():
                    recommended_exercises_output.append((rec['exercise_name'], rec['exercise_type']))
                    added_recommendations_set.add(rec['exercise_name'])

            return recommended_exercises_output

        # --- Case 3: Default (similarity-based) ---
        else:
            uncompleted_features_df = features_df.loc[uncompleted_exercises_df['exercise_name']]
            user_profile_features = np.zeros(len(mlb.classes_))

            for _, row in user_completed_df.iterrows():
                exercise_name = row['exercise_name']
                energy_level = str(row['energy_level']).lower()
                if exercise_name in features_df.index:
                    # Always reduce to 1D vector (fix for duplicates)
                    exercise_vector = features_df.loc[exercise_name]
                    if isinstance(exercise_vector, pd.DataFrame):
                        exercise_vector = exercise_vector.iloc[0].values
                    else:
                        exercise_vector = exercise_vector.values

                    if energy_level == 'high':
                        user_profile_features += exercise_vector * 1.5
                    elif energy_level == 'medium':
                        user_profile_features += exercise_vector * 1.0
                    else:
                        user_profile_features += exercise_vector * 0.5

            if np.sum(user_profile_features) > 0:
                user_profile_features /= np.sum(user_profile_features)
            else:
                return [("Complete some exercises to get personalized recommendations!", "")]

            similarities = cosine_similarity(user_profile_features.reshape(1, -1), uncompleted_features_df)
            recommended_indices = similarities.argsort()[0][::-1]

            for idx in recommended_indices:
                exercise_name = uncompleted_features_df.index[idx]
                if exercise_name not in added_recommendations_set:
                    ex_type = all_exercises_df[
                        all_exercises_df['exercise_name'] == exercise_name
                    ]['exercise_type'].iloc[0]
                    recommended_exercises_output.append((exercise_name, ex_type))
                    added_recommendations_set.add(exercise_name)
                if len(recommended_exercises_output) >= num_recommendations:
                    break

            if not recommended_exercises_output:
                return [("No specific recommendations at this time.", "")]
            return recommended_exercises_output

    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        return [("Could not generate recommendations at this time.", "")]
    finally:
        if conn:
            conn.close()


