from flask import Blueprint, request, jsonify
from db import get_db
from datetime import datetime

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/api/estimate', methods=['POST'])
def estimate_charge():
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    charging_point_id = data.get('charging_point_id')
    battery_pct = data.get('battery_pct', 20)
    target_pct = data.get('target_pct', 80)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT battery_capacity, max_ac_kw, max_dc_kw FROM Vehicle WHERE vehicle_id = %s", (vehicle_id,))
    vehicle = cur.fetchone()
    if not vehicle:
        cur.close(); conn.close()
        return jsonify({'error': 'Vehicle not found'}), 404

    cur.execute("""
        SELECT cp.power_rating, cp.price, cht.name AS charger_name
        FROM ChargingPoint cp
        LEFT JOIN ChargerType cht ON cp.charger_type_id = cht.charger_type_id
        WHERE cp.charging_point_id = %s
    """, (charging_point_id,))
    point = cur.fetchone()
    if not point:
        cur.close(); conn.close()
        return jsonify({'error': 'Charging point not found'}), 404

    cur.close()
    conn.close()

    battery_capacity = float(vehicle['battery_capacity'])
    kwh_needed = ((target_pct - battery_pct) / 100.0) * battery_capacity

    # Determine if DC or AC charger
    charger_name = point.get('charger_name', '') or ''
    is_dc = 'DC' in charger_name.upper()

    if is_dc and vehicle['max_dc_kw']:
        max_vehicle_rate = float(vehicle['max_dc_kw'])
    else:
        max_vehicle_rate = float(vehicle['max_ac_kw'])

    power_rating = float(point['power_rating'])
    charge_rate = min(power_rating, max_vehicle_rate)

    if charge_rate <= 0:
        return jsonify({'error': 'Cannot charge: incompatible charger'}), 400

    minutes = round((kwh_needed / charge_rate) * 60)
    cost = round(kwh_needed * float(point['price']), 2)

    return jsonify({
        'kwh_needed': round(kwh_needed, 2),
        'charge_rate_kw': charge_rate,
        'minutes': max(0, minutes),
        'cost': max(0, cost)
    })


@sessions_bp.route('/api/session/start', methods=['POST'])
def start_session():
    data = request.get_json()
    user_id = data.get('user_id')
    charging_point_id = data.get('charging_point_id')

    conn = get_db()
    cur = conn.cursor()

    # Update status to "In Use" (status_id = 2)
    cur.execute("UPDATE ChargingPoint SET status_id = 2 WHERE charging_point_id = %s", (charging_point_id,))

    # Insert session
    cur.execute("""
        INSERT INTO ChargingSession (charging_point_id, user_id, start_time)
        VALUES (%s, %s, NOW())
    """, (charging_point_id, user_id))

    session_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Session started', 'session_id': session_id})


@sessions_bp.route('/api/session/end', methods=['POST'])
def end_session():
    data = request.get_json()
    session_id = data.get('session_id')
    energy_consumed = data.get('energy_consumed', 0)

    conn = get_db()
    cur = conn.cursor()

    # Get session info
    cur.execute("""
        SELECT cs.charging_point_id, cp.price
        FROM ChargingSession cs
        JOIN ChargingPoint cp ON cs.charging_point_id = cp.charging_point_id
        WHERE cs.session_id = %s
    """, (session_id,))
    session = cur.fetchone()

    if not session:
        cur.close(); conn.close()
        return jsonify({'error': 'Session not found'}), 404

    total_cost = round(energy_consumed * float(session['price']), 2)

    # Update session
    cur.execute("""
        UPDATE ChargingSession
        SET end_time = NOW(), energy_consumed = %s, total_cost = %s
        WHERE session_id = %s
    """, (energy_consumed, total_cost, session_id))

    # Update status to "Available" (status_id = 1)
    cur.execute("UPDATE ChargingPoint SET status_id = 1 WHERE charging_point_id = %s", (session['charging_point_id'],))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Session ended', 'total_cost': total_cost})


@sessions_bp.route('/api/sessions/<int:user_id>', methods=['GET'])
def get_user_sessions(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT cs.session_id, cs.start_time, cs.end_time, cs.energy_consumed, cs.total_cost,
               s.name AS station_name, cp.power_rating,
               TIMESTAMPDIFF(MINUTE, cs.start_time, cs.end_time) AS duration_minutes
        FROM ChargingSession cs
        JOIN ChargingPoint cp ON cs.charging_point_id = cp.charging_point_id
        JOIN ChargingStation s ON cp.station_id = s.station_id
        WHERE cs.user_id = %s
        ORDER BY cs.start_time DESC
    """, (user_id,))
    sessions = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for s in sessions:
        row = {}
        for key, val in s.items():
            if hasattr(val, 'isoformat'):
                row[key] = val.isoformat()
            elif isinstance(val, (int, float, str, type(None))):
                row[key] = val
            else:
                row[key] = float(val) if val is not None else None
        result.append(row)

    return jsonify(result)
