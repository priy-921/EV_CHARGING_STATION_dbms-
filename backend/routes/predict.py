from flask import Blueprint, request, jsonify
import os
import joblib

predict_bp = Blueprint('predict', __name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml', 'model.pkl')

@predict_bp.route('/api/predict/wait', methods=['POST'])
def predict_wait():
    data = request.get_json()
    station_id = data.get('station_id')
    hour = data.get('hour')
    day_of_week = data.get('day_of_week')

    if not os.path.exists(MODEL_PATH):
        return jsonify({'wait_minutes': 10, 'note': 'ML model not trained yet, returning default'})

    try:
        model = joblib.load(MODEL_PATH)
        # Get total charging points for station
        from db import get_db
        conn = get_db()
        cur = conn.cursor()
        #how many charging points exists at a specific station
        cur.execute("SELECT COUNT(*) AS cnt FROM ChargingPoint WHERE station_id = %s", (station_id,))
        result = cur.fetchone()
        total_points = result['cnt'] if result else 3
        cur.close()
        conn.close()

        import numpy as np
        features = np.array([[station_id, hour, day_of_week, total_points]])
        prediction = model.predict(features)[0]
        wait_minutes = max(0, round(prediction, 1))

        return jsonify({'wait_minutes': wait_minutes})
    except Exception as e:
        return jsonify({'wait_minutes': 10, 'error': str(e)})
