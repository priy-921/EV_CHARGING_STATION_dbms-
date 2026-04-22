from flask import Blueprint, request, jsonify
from db import get_db
import math

stations_bp = Blueprint('stations', __name__)

@stations_bp.route('/api/stations', methods=['GET'])
def get_stations():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', default=50, type=float)

    conn = get_db()
    cur = conn.cursor()

    if lat and lng:
        # Haversine formula in SQL (distance in km)
        query = """
            SELECT s.*,
                (6371 * ACOS(
                    COS(RADIANS(%s)) * COS(RADIANS(s.latitude)) *
                    COS(RADIANS(s.longitude) - RADIANS(%s)) +
                    SIN(RADIANS(%s)) * SIN(RADIANS(s.latitude))
                )) AS distance,
                (SELECT COUNT(*) FROM ChargingPoint cp
                 JOIN ChargingPointStatus cps ON cp.status_id = cps.status_id
                 WHERE cp.station_id = s.station_id AND cps.status_name = 'Available'
                ) AS available_points,
                (SELECT COUNT(*) FROM ChargingPoint cp WHERE cp.station_id = s.station_id) AS total_points
            FROM ChargingStation s
            HAVING distance <= %s
            ORDER BY distance ASC
        """
        cur.execute(query, (lat, lng, lat, radius))
    else:
        query = """
            SELECT s.*,
                (SELECT COUNT(*) FROM ChargingPoint cp
                 JOIN ChargingPointStatus cps ON cp.status_id = cps.status_id
                 WHERE cp.station_id = s.station_id AND cps.status_name = 'Available'
                ) AS available_points,
                (SELECT COUNT(*) FROM ChargingPoint cp WHERE cp.station_id = s.station_id) AS total_points
            FROM ChargingStation s
        """
        cur.execute(query)

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
        result.append(row)

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
               cps.status_id, cps.status_name
        FROM ChargingPoint cp
        LEFT JOIN ConnectorType ct ON cp.connector_type_id = ct.connector_type_id
        LEFT JOIN ChargerType cht ON cp.charger_type_id = cht.charger_type_id
        LEFT JOIN ChargingPointStatus cps ON cp.status_id = cps.status_id
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
        'station': serialize(station),
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
