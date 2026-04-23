from flask import Blueprint, request, jsonify
from db import get_db

vehicles_bp = Blueprint('vehicles', __name__)


def serialize_vehicle(vehicle):
    return {
        'vehicle_id': vehicle['vehicle_id'],
        'user_id': vehicle['user_id'],
        'model': vehicle['model'],
        'brand': vehicle['brand'],
        'battery_capacity': float(vehicle['battery_capacity']) if vehicle.get('battery_capacity') is not None else None,
        'max_ac_kw': float(vehicle['max_ac_kw']) if vehicle.get('max_ac_kw') is not None else None,
        'max_dc_kw': float(vehicle['max_dc_kw']) if vehicle.get('max_dc_kw') is not None else None,
        'segment': vehicle['segment']
    }


def infer_connector_ids(vehicle):
    segment = (vehicle.get('segment') or '').upper()
    max_dc_kw = vehicle.get('max_dc_kw')

    if segment in ('2W', '3W'):
        return [3]

    connector_ids = [2]
    if max_dc_kw not in (None, '') and float(max_dc_kw or 0) > 0:
        connector_ids.append(4)
    return connector_ids


def ensure_vehicle_connectors(cur, vehicle):
    cur.execute("SELECT connector_type_id FROM VehicleConnector WHERE vehicle_id = %s", (vehicle['vehicle_id'],))
    existing = [row['connector_type_id'] for row in cur.fetchall()]
    if existing:
        return existing

    connector_ids = infer_connector_ids(vehicle)
    if not connector_ids:
        return []

    cur.executemany("""
        INSERT INTO VehicleConnector (vehicle_id, connector_type_id)
        VALUES (%s, %s)
    """, [(vehicle['vehicle_id'], connector_id) for connector_id in connector_ids])
    return connector_ids


@vehicles_bp.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.vehicle_id, v.user_id, v.model, v.brand, v.battery_capacity,
               v.max_ac_kw, v.max_dc_kw, v.segment
        FROM Vehicle v
        ORDER BY v.vehicle_id
    """)
    vehicles = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for v in vehicles:
        row = {}
        for key, val in v.items():
            if isinstance(val, (int, float, str, type(None))):
                row[key] = val
            else:
                row[key] = float(val) if val is not None else None
        result.append(row)

    return jsonify(result)


@vehicles_bp.route('/api/vehicles', methods=['POST'])
def create_vehicle():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    brand = (data.get('brand') or '').strip()
    model = (data.get('model') or '').strip()
    segment = (data.get('segment') or '').strip()
    battery_capacity = data.get('battery_capacity')
    max_ac_kw = data.get('max_ac_kw')
    max_dc_kw = data.get('max_dc_kw')

    if user_id in (None, '') or not all([brand, model, segment]) or battery_capacity in (None, '') or max_ac_kw in (None, ''):
        return jsonify({'error': 'User, brand, model, segment, battery capacity, and AC charging limit are required'}), 400

    try:
        user_id = int(user_id)
        battery_capacity = float(battery_capacity)
        max_ac_kw = float(max_ac_kw)
        max_dc_kw = float(max_dc_kw) if max_dc_kw not in (None, '') else None
    except (TypeError, ValueError):
        return jsonify({'error': 'Vehicle numeric fields must contain valid numbers'}), 400

    if battery_capacity <= 0 or max_ac_kw <= 0 or (max_dc_kw is not None and max_dc_kw <= 0):
        return jsonify({'error': 'Charging and battery values must be greater than zero'}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM `User` WHERE user_id = %s LIMIT 1", (user_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    cur.execute("SELECT COALESCE(MAX(vehicle_id), 0) + 1 AS next_vehicle_id FROM Vehicle")
    next_vehicle_id = cur.fetchone()['next_vehicle_id']

    cur.execute("""
        INSERT INTO Vehicle (vehicle_id, user_id, model, brand, battery_capacity, max_ac_kw, max_dc_kw, segment)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (next_vehicle_id, user_id, model, brand, battery_capacity, max_ac_kw, max_dc_kw, segment))
    ensure_vehicle_connectors(cur, {
        'vehicle_id': next_vehicle_id,
        'segment': segment,
        'max_dc_kw': max_dc_kw,
    })
    conn.commit()

    cur.execute("""
        SELECT vehicle_id, user_id, model, brand, battery_capacity, max_ac_kw, max_dc_kw, segment
        FROM Vehicle
        WHERE vehicle_id = %s
    """, (next_vehicle_id,))
    vehicle = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify({'message': 'Vehicle added successfully', 'vehicle': serialize_vehicle(vehicle)}), 201


@vehicles_bp.route('/api/vehicles/<int:vehicle_id>/connectors', methods=['GET'])
def get_vehicle_connectors(vehicle_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT vehicle_id, segment, max_dc_kw
        FROM Vehicle
        WHERE vehicle_id = %s
        LIMIT 1
    """, (vehicle_id,))
    vehicle = cur.fetchone()
    if not vehicle:
        cur.close()
        conn.close()
        return jsonify({'error': 'Vehicle not found'}), 404

    connector_ids = ensure_vehicle_connectors(cur, vehicle)
    conn.commit()

    cur.execute("""
        SELECT ct.connector_type_id, ct.name AS connector_name
        FROM ConnectorType ct
        WHERE ct.connector_type_id IN %s
        ORDER BY ct.connector_type_id
    """, (tuple(connector_ids) or (0,),))
    connectors = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(connectors)
