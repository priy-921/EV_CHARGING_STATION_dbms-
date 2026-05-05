from flask import Blueprint, request, jsonify
from db import get_db, ensure_user_station_columns

admin_bp = Blueprint('admin', __name__)


def serialize_value(value):
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if isinstance(value, (int, float, str, type(None), bool)):
        return value
    return float(value) if value is not None else None


def serialize_row(row):
    return {key: serialize_value(value) for key, value in row.items()}


def get_admin_user(cur):
    admin_user_id = request.args.get('admin_user_id') or (request.get_json(silent=True) or {}).get('admin_user_id')
    if admin_user_id in (None, ''):
        return None

    cur.execute("""
        SELECT user_id, role, admin_station_id
        FROM `User` u
        WHERE user_id = %s
        LIMIT 1
    """, (admin_user_id,))
    user = cur.fetchone()
    if not user or (user.get('role') or '').lower() != 'admin':
        return None
    return user


@admin_bp.route('/api/admin/dashboard', methods=['GET'])
def get_admin_dashboard():
    ensure_user_station_columns()
    conn = get_db()
    cur = conn.cursor()

    admin_user = get_admin_user(cur)
    if not admin_user:
        cur.close()
        conn.close()
        return jsonify({'error': 'Administrator access is required'}), 403

    admin_station_id = admin_user.get('admin_station_id')
    if not admin_station_id:
        cur.close()
        conn.close()
        return jsonify({'error': 'This administrator is not assigned to a station'}), 403

    cur.execute("""
        SELECT DISTINCT u.user_id, u.first_name, u.last_name, u.email, u.phone, u.role,
               u.selected_station_id
        FROM `User` u
        LEFT JOIN ChargingSession cs ON u.user_id = cs.user_id
        LEFT JOIN ChargingPoint cp ON cs.charging_point_id = cp.charging_point_id
        WHERE (u.role IS NULL OR LOWER(u.role) <> 'admin')
          AND (u.selected_station_id = %s OR cp.station_id = %s)
        ORDER BY u.user_id
    """, (admin_station_id, admin_station_id))
    users = [serialize_row(row) for row in cur.fetchall()]

    cur.execute("""
        SELECT cs.session_id, cs.user_id, u.first_name, u.last_name, u.email, u.phone,
               cs.charging_point_id, cs.start_time, cs.end_time,
               cs.energy_consumed, cs.total_cost,
               TIMESTAMPDIFF(MINUTE, cs.start_time, COALESCE(cs.end_time, NOW())) AS duration_minutes,
               s.station_id, s.name AS station_name, s.street, s.city, s.state,
               cp.power_rating, cp.price,
               ct.name AS connector_name, cht.name AS charger_name,
               cps.status_name
        FROM ChargingSession cs
        JOIN `User` u ON cs.user_id = u.user_id
        JOIN ChargingPoint cp ON cs.charging_point_id = cp.charging_point_id
        JOIN ChargingStation s ON cp.station_id = s.station_id
        LEFT JOIN ConnectorType ct ON cp.connector_type_id = ct.connector_type_id
        LEFT JOIN ChargerType cht ON cp.charger_type_id = cht.charger_type_id
        LEFT JOIN ChargingPointStatus cps ON cp.status_id = cps.status_id
        WHERE s.station_id = %s
        ORDER BY cs.start_time DESC
        LIMIT 500
    """, (admin_station_id,))
    sessions = [serialize_row(row) for row in cur.fetchall()]

    cur.execute("""
        SELECT s.station_id, s.name AS station_name, s.street, s.city, s.state, s.zip,
               s.latitude, s.longitude, s.contact,
               cp.charging_point_id, cp.power_rating, cp.price,
               ct.connector_type_id, ct.name AS connector_name,
               cht.charger_type_id, cht.name AS charger_name,
               cps.status_name,
               active.session_id AS active_session_id,
               active.user_id AS active_user_id,
               active.first_name AS active_first_name,
               active.last_name AS active_last_name,
               active.start_time AS active_start_time
        FROM ChargingStation s
        JOIN ChargingPoint cp ON s.station_id = cp.station_id
        LEFT JOIN ConnectorType ct ON cp.connector_type_id = ct.connector_type_id
        LEFT JOIN ChargerType cht ON cp.charger_type_id = cht.charger_type_id
        LEFT JOIN ChargingPointStatus cps ON cp.status_id = cps.status_id
        LEFT JOIN (
            SELECT cs.session_id, cs.user_id, cs.charging_point_id, cs.start_time,
                   u.first_name, u.last_name
            FROM ChargingSession cs
            JOIN `User` u ON cs.user_id = u.user_id
            WHERE cs.end_time IS NULL
        ) active ON cp.charging_point_id = active.charging_point_id
        WHERE s.station_id = %s
        ORDER BY s.station_id, cp.charging_point_id
    """, (admin_station_id,))
    station_rows = [serialize_row(row) for row in cur.fetchall()]

    stations_by_id = {}
    for row in station_rows:
        station = stations_by_id.setdefault(row['station_id'], {
            'station_id': row['station_id'],
            'station_name': row['station_name'] or f"EV Charging Station #{row['station_id']}",
            'street': row['street'],
            'city': row['city'],
            'state': row['state'],
            'zip': row['zip'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'contact': row['contact'],
            'charging_points': []
        })
        station['charging_points'].append({
            'charging_point_id': row['charging_point_id'],
            'power_rating': row['power_rating'],
            'price': row['price'],
            'connector_type_id': row['connector_type_id'],
            'connector_name': row['connector_name'],
            'charger_type_id': row['charger_type_id'],
            'charger_name': row['charger_name'],
            'status_name': row['status_name'],
            'active_session_id': row['active_session_id'],
            'active_user_id': row['active_user_id'],
            'active_user_name': ' '.join(part for part in [row['active_first_name'], row['active_last_name']] if part),
            'active_start_time': row['active_start_time']
        })

    cur.close()
    conn.close()

    active_sessions = [session for session in sessions if not session.get('end_time')]
    total_energy = sum(float(session.get('energy_consumed') or 0) for session in sessions)
    total_revenue = sum(float(session.get('total_cost') or 0) for session in sessions)

    return jsonify({
        'summary': {
            'total_users': len([user for user in users if (user.get('role') or '').lower() != 'admin']),
            'total_admins': 1,
            'total_sessions': len(sessions),
            'active_sessions': len(active_sessions),
            'total_energy': round(total_energy, 2),
            'total_revenue': round(total_revenue, 2),
            'total_stations': len(stations_by_id),
            'total_charging_points': len(station_rows)
        },
        'users': users,
        'sessions': sessions,
        'stations': list(stations_by_id.values())
    })
