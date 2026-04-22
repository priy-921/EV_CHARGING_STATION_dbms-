"""
Generate synthetic training data from AvailabilityLog patterns for ML model.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from db import get_db

def generate_training_data():
    conn = get_db()
    cur = conn.cursor()

    # Get availability logs
    cur.execute("""
        SELECT al.charging_point_id, al.status, al.logged_at,
               cp.station_id
        FROM AvailabilityLog al
        JOIN ChargingPoint cp ON al.charging_point_id = cp.charging_point_id
        ORDER BY al.logged_at
    """)
    logs = cur.fetchall()

    # Get station charging point counts
    cur.execute("""
        SELECT station_id, COUNT(*) AS total_points
        FROM ChargingPoint
        GROUP BY station_id
    """)
    station_points = {row['station_id']: row['total_points'] for row in cur.fetchall()}

    cur.close()
    conn.close()

    if not logs:
        print("No availability logs found. Generating purely synthetic data...")
        return generate_synthetic_fallback(station_points)

    # Process logs into features
    data = []
    for log in logs:
        logged_at = log['logged_at']
        station_id = log['station_id']
        hour = logged_at.hour
        day_of_week = logged_at.weekday()  # 0=Monday
        total_points = station_points.get(station_id, 3)

        # Estimate wait time based on status and time patterns
        is_busy = log['status'] == 'In Use'
        is_peak = hour in [8, 9, 18, 19, 20]
        is_weekend = day_of_week >= 5

        base_wait = 0
        if is_busy:
            base_wait = np.random.uniform(10, 40)
        if is_peak:
            base_wait += np.random.uniform(5, 20)
        if is_weekend:
            base_wait += np.random.uniform(0, 10)

        # More chargers = less wait
        base_wait = max(0, base_wait - (total_points * 0.5))
        wait_time = round(base_wait + np.random.normal(0, 3), 1)
        wait_time = max(0, wait_time)

        data.append({
            'station_id': station_id,
            'hour_of_day': hour,
            'day_of_week': day_of_week,
            'total_charging_points': total_points,
            'wait_time_minutes': wait_time
        })

    df = pd.DataFrame(data)

    # Augment with more synthetic data
    for station_id in station_points:
        for hour in range(8, 22):
            for day in range(7):
                total_points = station_points.get(station_id, 3)
                is_peak = hour in [8, 9, 18, 19, 20]
                is_weekend = day >= 5

                base = 5 if is_peak else 2
                if is_weekend:
                    base += 3
                base = max(0, base - (total_points * 0.3))
                wait = max(0, round(base + np.random.normal(0, 2), 1))

                data.append({
                    'station_id': station_id,
                    'hour_of_day': hour,
                    'day_of_week': day,
                    'total_charging_points': total_points,
                    'wait_time_minutes': wait
                })

    df = pd.DataFrame(data)
    output_path = os.path.join(os.path.dirname(__file__), 'training_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} training samples -> {output_path}")
    return df


def generate_synthetic_fallback(station_points):
    """Fallback if no availability logs exist."""
    data = []
    if not station_points:
        station_points = {i: 3 for i in range(1, 11)}

    for station_id in station_points:
        for hour in range(24):
            for day in range(7):
                total_points = station_points.get(station_id, 3)
                is_peak = hour in [8, 9, 18, 19, 20]
                is_weekend = day >= 5

                base = 8 if is_peak else 3
                if is_weekend:
                    base += 4
                base = max(0, base - (total_points * 0.3))
                wait = max(0, round(base + np.random.normal(0, 3), 1))

                data.append({
                    'station_id': station_id,
                    'hour_of_day': hour,
                    'day_of_week': day,
                    'total_charging_points': total_points,
                    'wait_time_minutes': wait
                })

    df = pd.DataFrame(data)
    output_path = os.path.join(os.path.dirname(__file__), 'training_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} synthetic training samples -> {output_path}")
    return df


if __name__ == '__main__':
    generate_training_data()
