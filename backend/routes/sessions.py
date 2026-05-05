from flask import Blueprint, request, jsonify
from db import get_db, ensure_user_station_columns
from datetime import datetime

sessions_bp = Blueprint('sessions', __name__)


def build_station_name(row):
    street = row.get('street') or row.get('address') or ''
    city = row.get('city') or ''
    locality = street.split(',')[0].strip() if street else city
    fallback_name = f"{locality} EV Charging Station" if locality else f"EV Charging Station #{row.get('station_id')}"
    return row.get('station_name') or fallback_name


def get_status_id(cur, status_name, fallback_id):
    cur.execute("""
        SELECT status_id
        FROM ChargingPointStatus
        WHERE LOWER(status_name) = LOWER(%s)
        LIMIT 1
    """, (status_name,))
    status = cur.fetchone()
    return status['status_id'] if status else fallback_id


def get_next_session_id(cur):
    cur.execute("SELECT COALESCE(MAX(session_id), 0) + 1 AS next_session_id FROM ChargingSession")
    return cur.fetchone()['next_session_id']


def get_admin_station_id(cur, user_id):
    if user_id in (None, ''):
        return None

    cur.execute("""
        SELECT role, admin_station_id
        FROM `User`
        WHERE user_id = %s
        LIMIT 1
    """, (user_id,))
    user = cur.fetchone()
    if not user or (user.get('role') or '').lower() != 'admin':
        return None
    return user.get('admin_station_id')


def charging_point_belongs_to_station(cur, charging_point_id, station_id):
    cur.execute("""
        SELECT charging_point_id
        FROM ChargingPoint
        WHERE charging_point_id = %s AND station_id = %s
        LIMIT 1
    """, (charging_point_id, station_id))
    return cur.fetchone() is not None


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
    data = request.get_json() or {}
    user_id = data.get('user_id')
    charging_point_id = data.get('charging_point_id')
    session_id = data.get('session_id')
    admin_user_id = data.get('admin_user_id')

    if user_id in (None, '') or charging_point_id in (None, ''):
        return jsonify({'error': 'User and charging point are required'}), 400

    ensure_user_station_columns()
    conn = get_db()
    cur = conn.cursor()

    admin_station_id = get_admin_station_id(cur, admin_user_id)
    if not admin_station_id:
        cur.close(); conn.close()
        return jsonify({'error': 'Only administrators can start charging sessions'}), 403

    if not charging_point_belongs_to_station(cur, charging_point_id, admin_station_id):
        cur.close(); conn.close()
        return jsonify({'error': 'Administrators can only manage their assigned station'}), 403

    in_use_status_id = get_status_id(cur, 'In Use', 2)

    if session_id:
        cur.execute("""
            SELECT session_id, user_id, charging_point_id, end_time
            FROM ChargingSession
            WHERE session_id = %s AND charging_point_id = %s
            LIMIT 1
        """, (session_id, charging_point_id))
        session = cur.fetchone()
        if not session:
            cur.close(); conn.close()
            return jsonify({'error': 'Booking/session not found'}), 404
        if int(session['user_id']) != int(user_id):
            cur.close(); conn.close()
            return jsonify({'error': 'This booking belongs to another user'}), 403
        if session.get('end_time'):
            cur.close(); conn.close()
            return jsonify({'error': 'This session is already completed'}), 400

        cur.execute("UPDATE ChargingPoint SET status_id = %s WHERE charging_point_id = %s", (in_use_status_id, charging_point_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Booked session started', 'session_id': int(session_id)})

    cur.execute("""
        SELECT cp.charging_point_id, cps.status_name
        FROM ChargingPoint cp
        LEFT JOIN ChargingPointStatus cps ON cp.status_id = cps.status_id
        WHERE cp.charging_point_id = %s
        LIMIT 1
    """, (charging_point_id,))
    point = cur.fetchone()
    if not point:
        cur.close(); conn.close()
        return jsonify({'error': 'Charging point not found'}), 404
    if point.get('status_name') != 'Available':
        cur.close(); conn.close()
        return jsonify({'error': 'Charging point is not available'}), 400

    cur.execute("""
        SELECT session_id
        FROM ChargingSession
        WHERE charging_point_id = %s AND end_time IS NULL
        LIMIT 1
    """, (charging_point_id,))
    if cur.fetchone():
        cur.close(); conn.close()
        return jsonify({'error': 'Charging point already has an active booking/session'}), 409

    session_id = get_next_session_id(cur)
    cur.execute("""
        INSERT INTO ChargingSession (session_id, charging_point_id, user_id, start_time)
        VALUES (%s, %s, %s, NOW())
    """, (session_id, charging_point_id, user_id))

    cur.execute("UPDATE ChargingPoint SET status_id = %s WHERE charging_point_id = %s", (in_use_status_id, charging_point_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Session started', 'session_id': session_id})


@sessions_bp.route('/api/session/book', methods=['POST'])
def book_session():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    charging_point_id = data.get('charging_point_id')

    if user_id in (None, '') or charging_point_id in (None, ''):
        return jsonify({'error': 'User and charging point are required'}), 400

    ensure_user_station_columns()
    conn = get_db()
    cur = conn.cursor()

    reserved_status_id = get_status_id(cur, 'Reserved', 4)

    cur.execute("""
        SELECT cp.charging_point_id, cp.station_id, cps.status_name
        FROM ChargingPoint cp
        LEFT JOIN ChargingPointStatus cps ON cp.status_id = cps.status_id
        WHERE cp.charging_point_id = %s
        LIMIT 1
    """, (charging_point_id,))
    point = cur.fetchone()
    if not point:
        cur.close(); conn.close()
        return jsonify({'error': 'Charging point not found'}), 404
    if point.get('status_name') != 'Available':
        cur.close(); conn.close()
        return jsonify({'error': 'Only available charging points can be booked'}), 400

    cur.execute("""
        SELECT session_id
        FROM ChargingSession
        WHERE charging_point_id = %s AND end_time IS NULL
        LIMIT 1
    """, (charging_point_id,))
    if cur.fetchone():
        cur.close(); conn.close()
        return jsonify({'error': 'Charging point already has an active booking/session'}), 409

    session_id = get_next_session_id(cur)
    cur.execute("""
        INSERT INTO ChargingSession (session_id, charging_point_id, user_id, start_time)
        VALUES (%s, %s, %s, NOW())
    """, (session_id, charging_point_id, user_id))

    cur.execute("UPDATE ChargingPoint SET status_id = %s WHERE charging_point_id = %s", (reserved_status_id, charging_point_id))
    cur.execute("UPDATE `User` SET selected_station_id = %s WHERE user_id = %s", (point['station_id'], user_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Charging point booked', 'session_id': session_id})


@sessions_bp.route('/api/session/end', methods=['POST'])
def end_session():
    data = request.get_json() or {}
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    admin_user_id = data.get('admin_user_id')
    energy_consumed = data.get('energy_consumed', 0)

    if session_id in (None, ''):
        return jsonify({'error': 'Session ID is required'}), 400

    try:
        energy_consumed = float(energy_consumed or 0)
    except (TypeError, ValueError):
        return jsonify({'error': 'Energy consumed must be a valid number'}), 400

    if energy_consumed < 0:
        return jsonify({'error': 'Energy consumed cannot be negative'}), 400

    ensure_user_station_columns()
    conn = get_db()
    cur = conn.cursor()

    admin_station_id = get_admin_station_id(cur, admin_user_id)
    if not admin_station_id:
        cur.close(); conn.close()
        return jsonify({'error': 'Only administrators can end charging sessions'}), 403

    # Get session info
    cur.execute("""
        SELECT cs.charging_point_id, cs.user_id, cs.end_time, cp.price, cp.station_id
        FROM ChargingSession cs
        JOIN ChargingPoint cp ON cs.charging_point_id = cp.charging_point_id
        WHERE cs.session_id = %s
    """, (session_id,))
    session = cur.fetchone()

    if not session:
        cur.close(); conn.close()
        return jsonify({'error': 'Session not found'}), 404

    if int(session['station_id']) != int(admin_station_id):
        cur.close(); conn.close()
        return jsonify({'error': 'Administrators can only manage their assigned station'}), 403

    if user_id not in (None, '') and int(session['user_id']) != int(user_id):
        cur.close(); conn.close()
        return jsonify({'error': 'This session belongs to another user'}), 403

    if session.get('end_time'):
        cur.close(); conn.close()
        return jsonify({'error': 'Session is already completed'}), 400

    total_cost = round(energy_consumed * float(session['price']), 2)

    # Update session
    cur.execute("""
        UPDATE ChargingSession
        SET end_time = NOW(), energy_consumed = %s, total_cost = %s
        WHERE session_id = %s
    """, (energy_consumed, total_cost, session_id))

    available_status_id = get_status_id(cur, 'Available', 1)
    cur.execute("UPDATE ChargingPoint SET status_id = %s WHERE charging_point_id = %s", (available_status_id, session['charging_point_id']))

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
               s.station_id, s.name AS station_name, s.street, s.city, cp.power_rating,
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
        row['station_name'] = build_station_name(row)
        row.pop('street', None)
        row.pop('city', None)
        row.pop('station_id', None)
        result.append(row)

    return jsonify(result)
