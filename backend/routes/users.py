from flask import Blueprint, request, jsonify
from db import get_db
import hashlib

users_bp = Blueprint('users', __name__)


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def password_matches(stored_password, plain_password):
    if not stored_password:
        return False
    return stored_password == plain_password or stored_password == hash_password(plain_password)


def mask_password(password):
    if not password:
        return ''
    return '*' * max(8, min(len(password), 16))


def ensure_auth_tables():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS LoginAudit (
            audit_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NULL,
            user_id_input INT NOT NULL,
            success TINYINT(1) NOT NULL DEFAULT 0,
            event_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(64) NULL,
            FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE SET NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PasswordResetAudit (
            reset_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            user_id_input INT NOT NULL,
            reset_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(64) NULL,
            FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS SignupAudit (
            signup_audit_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            email VARCHAR(255) NOT NULL,
            event_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(64) NULL,
            FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def record_login_attempt(user_id_input, success, user_id=None):
    ensure_auth_tables()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO LoginAudit (user_id, user_id_input, success, ip_address)
        VALUES (%s, %s, %s, %s)
    """, (user_id, user_id_input, 1 if success else 0, request.remote_addr))
    conn.commit()
    cur.close()
    conn.close()


def record_password_reset(user_id_input, user_id):
    ensure_auth_tables()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO PasswordResetAudit (user_id, user_id_input, ip_address)
        VALUES (%s, %s, %s)
    """, (user_id, user_id_input, request.remote_addr))
    conn.commit()
    cur.close()
    conn.close()


def record_signup(user_id, email):
    ensure_auth_tables()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO SignupAudit (user_id, email, ip_address)
        VALUES (%s, %s, %s)
    """, (user_id, email, request.remote_addr))
    conn.commit()
    cur.close()
    conn.close()


def serialize_user(user):
    return {
        'user_id': user['user_id'],
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'email': user['email'],
        'phone': user['phone'],
        'role': user.get('role', 'user'),
        'last_lat': float(user['last_lat']) if user.get('last_lat') is not None else None,
        'last_lng': float(user['last_lng']) if user.get('last_lng') is not None else None,
        'last_location_updated': user['last_location_updated'].isoformat() if user.get('last_location_updated') else None,
        'masked_password': mask_password(user.get('password'))
    }


@users_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    email = (data.get('email') or '').strip()
    phone = (data.get('phone') or '').strip()
    password = data.get('password') or ''

    if not all([first_name, last_name, email, phone, password]):
        return jsonify({'error': 'All signup fields are required'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM `User` WHERE email = %s OR phone = %s LIMIT 1", (email, phone))
    existing_user = cur.fetchone()
    if existing_user:
        cur.close()
        conn.close()
        return jsonify({'error': 'A user with this email or phone already exists'}), 409

    cur.execute("SELECT COALESCE(MAX(user_id), 0) + 1 AS next_user_id FROM `User`")
    next_user_id = cur.fetchone()['next_user_id']

    cur.execute("""
        INSERT INTO `User` (
            user_id, first_name, last_name, email, phone, password
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (next_user_id, first_name, last_name, email, phone, hash_password(password)))
    conn.commit()

    cur.execute("""
        SELECT user_id, first_name, last_name, email, phone, password
        FROM `User`
        WHERE user_id = %s
    """, (next_user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    record_signup(next_user_id, email)
    return jsonify({'message': 'Signup successful', 'user': serialize_user(user)})


@users_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    password = data.get('password') or ''

    if user_id in (None, '') or not password:
        return jsonify({'error': 'User ID and password are required'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, first_name, last_name, email, phone, password
        FROM `User`
        WHERE user_id = %s
        LIMIT 1
    """, (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user or not password_matches(user.get('password'), password):
        record_login_attempt(int(user_id), False, user['user_id'] if user else None)
        return jsonify({'error': 'Invalid user ID or password'}), 401

    record_login_attempt(int(user_id), True, user['user_id'])

    return jsonify({'message': 'Login successful', 'user': serialize_user(user)})


@users_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    email = (data.get('email') or '').strip()
    new_password = data.get('new_password') or ''

    if user_id in (None, '') or not email or not new_password:
        return jsonify({'error': 'User ID, email, and new password are required'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, first_name, last_name, email, phone
        FROM `User`
        WHERE user_id = %s AND email = %s
        LIMIT 1
    """, (user_id, email))
    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        return jsonify({'error': 'No account found for this user ID and email'}), 404

    cur.execute("UPDATE `User` SET password = %s WHERE user_id = %s", (hash_password(new_password), user['user_id']))
    conn.commit()
    cur.close()
    conn.close()
    record_password_reset(int(user_id), user['user_id'])

    return jsonify({'message': 'Password reset successful. Please log in with your new password.'})


@users_bp.route('/api/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, first_name, last_name, email, phone, password
        FROM `User`
        WHERE user_id = %s
        LIMIT 1
    """, (user_id,))
    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    cur.execute("""
        SELECT vehicle_id, model, brand, battery_capacity, max_ac_kw, max_dc_kw, segment
        FROM Vehicle
        WHERE user_id = %s
        ORDER BY vehicle_id
    """, (user_id,))
    vehicles = cur.fetchall()

    cur.close()
    conn.close()

    serialized_vehicles = []
    for vehicle in vehicles:
        serialized_vehicles.append({
            'vehicle_id': vehicle['vehicle_id'],
            'model': vehicle['model'],
            'brand': vehicle['brand'],
            'battery_capacity': float(vehicle['battery_capacity']) if vehicle.get('battery_capacity') is not None else None,
            'max_ac_kw': float(vehicle['max_ac_kw']) if vehicle.get('max_ac_kw') is not None else None,
            'max_dc_kw': float(vehicle['max_dc_kw']) if vehicle.get('max_dc_kw') is not None else None,
            'segment': vehicle['segment']
        })

    return jsonify({
        'user': serialize_user(user),
        'vehicles': serialized_vehicles
    })
