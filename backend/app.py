from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import datetime
import os
import traceback

app = Flask(__name__)
CORS(app)  

@app.route('/')
def home():
    return jsonify({"message": "Doctor Survey Predictor API is running!"}), 200

def load_data():
    try:
        if os.path.exists('dummy_npi_data.xlsx'):
            data = pd.read_excel('dummy_npi_data.xlsx')
            print("Data loaded successfully. Columns:", data.columns.tolist())
            print("Sample data:", data.head(2).to_dict('records'))
            return data
        else:
            print("Data file not found, creating dummy data instead")
            return create_dummy_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        traceback.print_exc()
        return create_dummy_data()

def create_dummy_data():
    npis = [f"NPI{i}" for i in range(1, 101)]
    specialties = np.random.choice(['Cardiology', 'Neurology', 'Pediatrics', 'Oncology', 'Family Medicine'], 100)
    regions = np.random.choice(['Northeast', 'Midwest', 'South', 'West'], 100)
    
    login_hours = np.random.randint(6, 22, 100)
    login_minutes = np.random.randint(0, 60, 100)
    login_times = [f"{h:02d}:{m:02d}" for h, m in zip(login_hours, login_minutes)]
    
    time_spent = np.random.randint(5, 61, 100)
    
    completed = np.random.choice([0, 1], 100, p=[0.3, 0.7])
    
    data = pd.DataFrame({
        'NPI': npis,
        'Speciality': specialties,
        'Region': regions,
        'Login Time': login_times,
        'Time Spent': time_spent,
        'Count of Attempts': np.random.randint(1, 10, 100)
    })
    
    return data

# ----------- Train Model -------------
def train_model(data):
   
    column_mapping = {
        'npi': ['NPI', 'npi'],
        'specialty': ['Speciality', 'Specialty', 'specialty'],
        'region': ['Region', 'region'],
        'login_time': ['Login Time', 'login_time'],
        'logout_time': ['Logout Time', 'logout_time'],
        'time_spent': ['Time Spent', 'time_spent'],
        'attempts': ['Count of Attempts', 'attempts']
    }
    
    actual_columns = {}
    for key, possible_names in column_mapping.items():
        for name in possible_names:
            if name in data.columns:
                actual_columns[key] = name
                break
        if key not in actual_columns:
            print(f"Warning: Could not find column for {key}")
    
    print(f"Using columns: {actual_columns}")
    
    
    try:
        data['login_hour'] = data[actual_columns['login_time']].apply(
            lambda x: int(str(x).split(':')[0]) if isinstance(x, str) and ':' in str(x) else 12
        )
        data['login_minute'] = data[actual_columns['login_time']].apply(
            lambda x: int(str(x).split(':')[1]) if isinstance(x, str) and ':' in str(x) else 0
        )
    except Exception as e:
        print(f"Error processing login time: {e}")
        data['login_hour'] = np.random.randint(8, 18, len(data))
        data['login_minute'] = np.random.randint(0, 60, len(data))
    
    if 'time_spent' in actual_columns:
        data['time_spent_minutes'] = data[actual_columns['time_spent']]
    elif 'login_time' in actual_columns and 'logout_time' in actual_columns:
        try:
            data['time_spent_minutes'] = data.apply(
                lambda row: (pd.to_datetime(row[actual_columns['logout_time']], errors='coerce') - 
                             pd.to_datetime(row[actual_columns['login_time']], errors='coerce')).total_seconds() / 60 
                if pd.notna(row[actual_columns['login_time']]) and pd.notna(row[actual_columns['logout_time']]) 
                else 30, axis=1
            )
        except Exception as e:
            print(f"Error calculating time spent: {e}")
            data['time_spent_minutes'] = np.random.randint(5, 60, len(data))
    else:
        data['time_spent_minutes'] = np.random.randint(5, 60, len(data))
    
    if 'attempts' in actual_columns:
        max_attempts = data[actual_columns['attempts']].max()
        if max_attempts > 0:
            data['completed_survey'] = data[actual_columns['attempts']] / max_attempts
        else:
            data['completed_survey'] = np.random.choice([0, 1], len(data), p=[0.3, 0.7])
    else:
        data['completed_survey'] = np.random.choice([0, 1], len(data), p=[0.3, 0.7])
    

    X = data[['login_hour', 'login_minute', actual_columns['specialty'], 
              actual_columns['region'], 'time_spent_minutes']]
    y = data['completed_survey']
    
    numeric_features = ['login_hour', 'login_minute', 'time_spent_minutes']
    categorical_features = [actual_columns['specialty'], actual_columns['region']]
    
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # -------------- Create and train the model --------------
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    model.fit(X, y)
    return model, actual_columns


def predict_doctors(model, data, input_time, column_mapping):
    hour, minute = map(int, input_time.split(':'))
    
    # -------------- Process login time --------------
    try:
        data['login_hour'] = data[column_mapping['login_time']].apply(
            lambda x: int(str(x).split(':')[0]) if isinstance(x, str) and ':' in str(x) else 12
        )
        data['login_minute'] = data[column_mapping['login_time']].apply(
            lambda x: int(str(x).split(':')[1]) if isinstance(x, str) and ':' in str(x) else 0
        )
    except Exception as e:
        print(f"Error processing login time for prediction: {e}")
        data['login_hour'] = np.random.randint(8, 18, len(data))
        data['login_minute'] = np.random.randint(0, 60, len(data))
    

    data['hour_diff'] = np.minimum(
        np.abs(data['login_hour'] - hour),
        24 - np.abs(data['login_hour'] - hour)
    )
    
    if 'time_spent_minutes' not in data.columns:
        if 'time_spent' in column_mapping:
            data['time_spent_minutes'] = data[column_mapping['time_spent']]
        else:
            data['time_spent_minutes'] = np.random.randint(5, 60, len(data))
    
    X_pred = data[['login_hour', 'login_minute', column_mapping['specialty'], 
                   column_mapping['region'], 'time_spent_minutes']]
    
    proba = model.predict_proba(X_pred)[:, 1]  

    time_factor = 1 / (1 + data['hour_diff'])
    adjusted_proba = proba * time_factor
    

    data['likelihood_score'] = (adjusted_proba * 100).round(1)
    

    top_doctors = data.sort_values('likelihood_score', ascending=False).head(20)
    
    results = []
    for _, row in top_doctors.iterrows():
        results.append({
            'npi': str(row[column_mapping['npi']]),
            'specialty': str(row[column_mapping['specialty']]),
            'region': str(row[column_mapping['region']]),
            'likelihood_score': float(row['likelihood_score'])
        })
    
    if results:
        print("Sample result:", results[0])
    
    return results

# Initialize data and model
print("Loading data...")
data = load_data()
print(f"Training model on {len(data)} records...")
model, column_mapping = train_model(data)
print("Model training complete")


@app.route('/predict', methods=['GET'])
def get_predictions():
    time = request.args.get('time', '09:00')
    
    try:

        try:
            hour, minute = map(int, time.split(':'))
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise ValueError("Invalid time format")
            time = f"{hour:02d}:{minute:02d}"  
        except ValueError:
            return jsonify({
                'success': False,
                'error': "Invalid time format. Please use HH:MM (24-hour format)"
            }), 400
            
        doctors = predict_doctors(model, data.copy(), time, column_mapping)
        return jsonify({
            'success': True,
            'time': time,
            'doctors': doctors
        })
    except Exception as e:
        print(f"Error in prediction: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run()
