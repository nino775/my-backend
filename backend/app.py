from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import random
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load AI Models
diet_model_path = 'diet_model.h5'
workout_model_path = 'workout_model.h5'

try:
    diet_model = tf.keras.models.load_model(diet_model_path)
    workout_model = tf.keras.models.load_model(workout_model_path)
    print("Models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    exit(1)

# Load datasets
nutrition_data = pd.read_csv('nuitup.csv')  # Replace with the actual path
workout_data = pd.read_csv('strong.csv')  # Replace with the actual path

# Preprocess Nutrition Data
nutrition_data['Calories'] = pd.to_numeric(nutrition_data['Calories'], errors='coerce')
nutrition_data['Fat'] = nutrition_data['Fat'].str.replace(' g', '').astype(float)
nutrition_data['Protein'] = nutrition_data['Protein'].str.replace(' g', '').astype(float)
nutrition_data['Carbohydrates'] = nutrition_data['Carbohydrates'].str.replace(' g', '').astype(float)
nutrition_data = nutrition_data.dropna()

# Preprocess Workout Data
def duration_to_minutes(duration):
    try:
        if isinstance(duration, str):
            # Handle "Xh Ym" format
            if 'h' in duration and 'm' in duration:
                h, m = map(int, duration.replace('h', '').replace('m', '').split())
                return h * 60 + m
            # Handle "Xh" format
            elif 'h' in duration:
                h = int(duration.replace('h', '').strip())
                return h * 60
            # Handle "Xm" format
            elif 'm' in duration:
                m = int(duration.replace('m', '').strip())
                return m
        return 0  # Default for unexpected formats or missing values
    except ValueError:
        return 0  # Handle cases where the string cannot be parsed


# API Endpoints
@app.route('/predict/diet', methods=['POST'])
def predict_diet():
    try:
        data = request.get_json(force=True)
        print("Received Data:", data)  # Log the received data

        if 'calories' not in data:
            print("Error: 'calories' not provided")
            return jsonify({'error': 'Please provide the desired calorie intake'}), 400

        total_calories = int(data['calories'])
        print(f"Total Calories Requested: {total_calories}")

        # Split calories into meals
        meal_distribution = {
            "Breakfast": 0.25 * total_calories,  # 25% for breakfast
            "Lunch": 0.35 * total_calories,      # 35% for lunch
            "Dinner": 0.30 * total_calories,     # 30% for dinner
            "Snack": 0.10 * total_calories       # 10% for snacks
        }
        print(f"Meal Distribution: {meal_distribution}")

        # Generate diet plan
        diet_plan = []
        for meal, calories in meal_distribution.items():
            try:
                # Randomly select foods
                selected_items = nutrition_data.sample(3).to_dict('records')  # Sample 3 items per meal
            except ValueError:
                print("Error: Insufficient data in the nutrition dataset!")
                selected_items = [{"name": "Placeholder Food", "calories": 0}] * 3

            diet_plan.append({
                "meal": meal,
                "calories": int(calories),
                "items": [{"name": item["name"], "calories": item["Calories"]} for item in selected_items]
            })

        print("Generated Diet Plan:", diet_plan)  # Log the final diet plan
        return jsonify({'recommendation': diet_plan})

    except Exception as e:
        print("Error in /predict/diet:", str(e))
        return jsonify({'error': str(e)}), 400



import random

@app.route('/predict/workout', methods=['POST'])
def predict_workout():
    try:
        data = request.get_json(force=True)
        print("Received Data:", data)  # Debugging input data

        # Validate input
        if 'goal' not in data:
            return jsonify({'error': 'Please provide your fitness goal (e.g., strength, cardio).'}), 400

        goal = data['goal'].lower()
        print(f"Fitness Goal: {goal}")

        # Simulate model prediction (replace with actual model prediction)
        try:
            input_data = np.random.rand(57).tolist()  # Randomized input data for model
            input_tensor = tf.convert_to_tensor([input_data], dtype=tf.float32)
            prediction = workout_model.predict(input_tensor).tolist()[0]
        except Exception as e:
            print(f"Model Prediction Error: {e}")
            prediction = [0.5, 0.6, 0.7, 0.8, 0.9]  # Placeholder predictions for testing

        print("Model Prediction:", prediction)

        # Generate workout plan with 5 unique exercises
        selected_exercises = set()
        workout_plan = []
        while len(workout_plan) < 5:
            # Randomly sample an exercise
            workout = workout_data.sample(1).to_dict('records')[0]
            exercise_name = workout.get("Exercise Name", "Unknown Exercise")

            if exercise_name not in selected_exercises:
                selected_exercises.add(exercise_name)
                scaled_sets = random.randint(2, 4)  # Random sets between 2 and 4
                scaled_reps = random.randint(6, 12)  # Random reps between 6 and 12
                duration = random.randint(5, 15)  # Random duration between 5 and 15 minutes

                # Remove NaN or invalid values
                workout = {key: (value if pd.notna(value) else None) for key, value in workout.items()}

                workout_plan.append({
                    "exercise": exercise_name,
                    "sets": scaled_sets,
                    "reps": scaled_reps,
                    "duration": f"{duration} min"
                })

        print("Generated Workout Plan:", workout_plan)
        return jsonify({'recommendation': workout_plan})

    except Exception as e:
        print(f"Error in /predict/workout: {e}")
        return jsonify({'error': str(e)}), 400





if __name__ == '__main__':
    app.run(port=5000, debug=True)
