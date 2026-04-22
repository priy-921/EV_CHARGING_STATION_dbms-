"""
Train Random Forest Regressor for wait time prediction.
"""
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

def train_model():
    data_path = os.path.join(os.path.dirname(__file__), 'training_data.csv')

    if not os.path.exists(data_path):
        print("Training data not found. Run generate_data.py first.")
        print("Running generate_data.py...")
        from generate_data import generate_training_data
        generate_training_data()

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} training samples")

    features = ['station_id', 'hour_of_day', 'day_of_week', 'total_charging_points']
    target = 'wait_time_minutes'

    X = df[features].values
    y = df[target].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    print("Training Random Forest Regressor...")
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\nModel Performance:")
    print(f"  MAE:  {mae:.2f} minutes")
    print(f"  R²:   {r2:.4f}")

    # Feature importance
    importances = model.feature_importances_
    print(f"\nFeature Importances:")
    for feat, imp in zip(features, importances):
        print(f"  {feat}: {imp:.4f}")

    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    joblib.dump(model, model_path)
    print(f"\nModel saved to {model_path}")

    return model


if __name__ == '__main__':
    train_model()
