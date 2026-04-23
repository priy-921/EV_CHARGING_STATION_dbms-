from flask import Blueprint, request, jsonify
from db import get_db
import math

stations_bp = Blueprint('stations', __name__)


def add_station_display_fields(station):
    street = station.get('street') or station.get('address') or ''
    city = station.get('city') or ''
    state = station.get('state') or ''
    zip_code = station.get('zip') or station.get('pincode') or ''
    contact = station.get('contact') or station.get('contact_number') or ''
    locality = street.split(',')[0].strip() if street else city
    fallback_name = f"{locality} EV Charging Station" if locality else f"EV Charging Station #{station.get('station_id')}"

    station['name'] = station.get('name') or fallback_name
    station['display_name'] = station['name']
    station['address'] = station.get('address') or street
    station['street'] = street
    station['pincode'] = station.get('pincode') or zip_code
    station['zip'] = zip_code
    station['contact_number'] = station.get('contact_number') or contact
    station['contact'] = contact
    station['full_address'] = ', '.join(part for part in [street, city, state, zip_code] if part)
    return station


@stations_bp.route('/api/stations', methods=['GET'])
def get_stations():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', default=50, type=float)
    connector_ids_raw = request.args.get('connector_ids', '')
    connector_ids = []
    for raw_id in connector_ids_raw.split(','):
        raw_id = raw_id.strip()
        if not raw_id:
            continue
        try:
            connector_ids.append(int(raw_id))
        except ValueError:
            return jsonify({'error': 'connector_ids must be comma-separated numbers'}), 400

    connector_clause = ''
    exists_clause = ''
    if connector_ids:
        placeholders = ', '.join(['%s'] * len(connector_ids))
        connector_clause = f" AND cp.connector_type_id IN ({placeholders})"
        exists_clause = f"""
            WHERE EXISTS (
                SELECT 1
                FROM ChargingPoint cp_filter
                WHERE cp_filter.station_id = s.station_id
                  AND cp_filter.connector_type_id IN ({placeholders})
            )
        """

    conn = get_db()
    cur = conn.cursor()

    if lat and lng:
        # Haversine formula in SQL (distance in km)
        query = f"""
            SELECT s.*,
                (6371 * ACOS(
                    COS(RADIANS(%s)) * COS(RADIANS(s.latitude)) *
                    COS(RADIANS(s.longitude) - RADIANS(%s)) +
                    SIN(RADIANS(%s)) * SIN(RADIANS(s.latitude))
                )) AS distance,
                (SELECT COUNT(*) FROM ChargingPoint cp
                 JOIN ChargingPointStatus cps ON cp.status_id = cps.status_id
                 WHERE cp.station_id = s.station_id AND cps.status_name = 'Available'
                 {connector_clause}
                ) AS available_points,
                (SELECT COUNT(*) FROM ChargingPoint cp WHERE cp.station_id = s.station_id {connector_clause}) AS total_points
            FROM ChargingStation s
            {exists_clause}
            HAVING distance <= %s
            ORDER BY distance ASC
        """
        cur.execute(query, (lat, lng, lat, *connector_ids, *connector_ids, *connector_ids, radius))
    else:
        query = f"""
            SELECT s.*,
                (SELECT COUNT(*) FROM ChargingPoint cp
                 JOIN ChargingPointStatus cps ON cp.status_id = cps.status_id
                 WHERE cp.station_id = s.station_id AND cps.status_name = 'Available'
                 {connector_clause}
                ) AS available_points,
                (SELECT COUNT(*) FROM ChargingPoint cp WHERE cp.station_id = s.station_id {connector_clause}) AS total_points
            FROM ChargingStation s
            {exists_clause}
        """
        cur.execute(query, (*connector_ids, *connector_ids, *connector_ids))

    stations = cur.fetchall()
    cur.close()
    conn.close()

    # Convert Decimal types to float for JSON serialization
    result = []
    for s in stations:
        row = {}
        for key, val in s.items():
            if isinstance(val, (int, float, str, type(None))):
                row[key] = val
            else:
                row[key] = float(val) if val is not None else None
        result.append(add_station_display_fields(row))

    return jsonify(result)


@stations_bp.route('/api/stations/<int:station_id>', methods=['GET'])
def get_station_detail(station_id):
    conn = get_db()
    cur = conn.cursor()

    # Station info
    cur.execute("SELECT * FROM ChargingStation WHERE station_id = %s", (station_id,))
    station = cur.fetchone()
    if not station:
        cur.close()
        conn.close()
        return jsonify({'error': 'Station not found'}), 404

    # Charging points with connector type, charger type, and status
    cur.execute("""
        SELECT cp.charging_point_id, cp.power_rating, cp.price,
               ct.connector_type_id, ct.name AS connector_name,
               cht.charger_type_id, cht.name AS charger_name,
               cps.status_id, cps.status_name,
               active.session_id AS active_session_id,
               active.user_id AS active_user_id
        FROM ChargingPoint cp
        LEFT JOIN ConnectorType ct ON cp.connector_type_id = ct.connector_type_id
        LEFT JOIN ChargerType cht ON cp.charger_type_id = cht.charger_type_id
        LEFT JOIN ChargingPointStatus cps ON cp.status_id = cps.status_id
        LEFT JOIN (
            SELECT charging_point_id, MIN(session_id) AS session_id, MIN(user_id) AS user_id
            FROM ChargingSession
            WHERE end_time IS NULL
            GROUP BY charging_point_id
        ) active ON cp.charging_point_id = active.charging_point_id
        WHERE cp.station_id = %s
    """, (station_id,))
    points = cur.fetchall()

    # Opening hours
    cur.execute("SELECT * FROM OpeningHours WHERE station_id = %s ORDER BY FIELD(day_of_week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')", (station_id,))
    hours = cur.fetchall()

    cur.close()
    conn.close()

    # Serialize
    def serialize(obj):
        result = {}
        for key, val in obj.items():
            if isinstance(val, (int, float, str, type(None), bool)):
                result[key] = val
            elif hasattr(val, 'isoformat'):
                result[key] = str(val)
            else:
                result[key] = float(val) if val is not None else None
        return result

    return jsonify({
        'station': add_station_display_fields(serialize(station)),
        'charging_points': [serialize(p) for p in points],
        'opening_hours': [serialize(h) for h in hours]
    })


@stations_bp.route('/api/stations/<int:station_id>/peak-hours', methods=['GET'])
def get_peak_hours(station_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT HOUR(cs.start_time) AS hour, COUNT(*) AS session_count
        FROM ChargingSession cs
        JOIN ChargingPoint cp ON cs.charging_point_id = cp.charging_point_id
        WHERE cp.station_id = %s
        GROUP BY HOUR(cs.start_time)
        ORDER BY hour ASC
    """, (station_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Fill all 24 hours
    hour_counts = {i: 0 for i in range(24)}
    for r in rows:
        hour_counts[int(r['hour'])] = int(r['session_count'])

    return jsonify({'hours': list(hour_counts.keys()), 'counts': list(hour_counts.values())})
