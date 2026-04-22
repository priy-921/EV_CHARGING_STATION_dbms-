from flask import Blueprint, jsonify
from db import get_db

vehicles_bp = Blueprint('vehicles', __name__)

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


@vehicles_bp.route('/api/vehicles/<int:vehicle_id>/connectors', methods=['GET'])
def get_vehicle_connectors(vehicle_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT ct.connector_type_id, ct.name AS connector_name
        FROM VehicleConnector vc
        JOIN ConnectorType ct ON vc.connector_type_id = ct.connector_type_id
        WHERE vc.vehicle_id = %s
    """, (vehicle_id,))
    connectors = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(connectors)
