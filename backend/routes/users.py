from flask import Blueprint, request, jsonify
from db import get_db, ensure_user_station_columns
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


def serialize_value(value):
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if isinstance(value, (int, float, str, type(None), bool)):
        return value
    return float(value) if value is not None else None


def serialize_row(row):
    return {key: serialize_value(value) for key, value in row.items()}


def as_int_or_none(value):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def station_exists(cur, station_id):
    cur.execute("SELECT station_id FROM ChargingStation WHERE station_id = %s LIMIT 1", (station_id,))
    return cur.fetchone() is not None


def admin_station_is_available(cur, station_id, user_id=None):
    cur.execute("""
        SELECT user_id
        FROM `User`
        WHERE admin_station_id = %s
          AND (%s IS NULL OR user_id <> %s)
        LIMIT 1
    """, (station_id, user_id, user_id))
    if cur.fetchone():
        return False

    cur.execute("""
        SELECT admin_user_id
        FROM AdminData
        WHERE admin_station_id = %s
          AND (%s IS NULL OR admin_user_id <> %s)
        LIMIT 1
    """, (station_id, user_id, user_id))
    return cur.fetchone() is None


def sync_account_data(cur, user_id):
    cur.execute("""
        SELECT role
        FROM `User`
        WHERE user_id = %s
        LIMIT 1
    """, (user_id,))
    user = cur.fetchone()
    if not user:
        return

    if (user.get('role') or 'user').lower() == 'admin':
        cur.execute("""
            INSERT INTO AdminData (
                admin_user_id, first_name, last_name, email, phone, password,
                admin_station_id, last_lat, last_lng, last_location_updated
            )
            SELECT user_id, first_name, last_name, email, phone, password,
                   admin_station_id, last_lat, last_lng, last_location_updated
            FROM `User`
            WHERE user_id = %s
            ON DUPLICATE KEY UPDATE
                first_name = VALUES(first_name),
                last_name = VALUES(last_name),
                email = VALUES(email),
                phone = VALUES(phone),
                password = VALUES(password),
                admin_station_id = VALUES(admin_station_id),
                last_lat = VALUES(last_lat),
                last_lng = VALUES(last_lng),
                last_location_updated = VALUES(last_location_updated)
        """, (user_id,))
        cur.execute("DELETE FROM UserData WHERE user_id = %s", (user_id,))
        return

    cur.execute("""
        INSERT INTO UserData (
            user_id, first_name, last_name, email, phone, password,
            last_lat, last_lng, last_location_updated, selected_station_id
        )
        SELECT user_id, first_name, last_name, email, phone, password,
               last_lat, last_lng, last_location_updated, selected_station_id
        FROM `User`
        WHERE user_id = %s
        ON DUPLICATE KEY UPDATE
            first_name = VALUES(first_name),
            last_name = VALUES(last_name),
            email = VALUES(email),
            phone = VALUES(phone),
            password = VALUES(password),
            last_lat = VALUES(last_lat),
            last_lng = VALUES(last_lng),
            last_location_updated = VALUES(last_location_updated),
            selected_station_id = VALUES(selected_station_id)
    """, (user_id,))
    cur.execute("DELETE FROM AdminData WHERE admin_user_id = %s", (user_id,))


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
    admin_station_id = user.get('admin_station_id')
    return {
        'user_id': user['user_id'],
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'email': user['email'],
        'phone': user['phone'],
        'role': user.get('role') or 'user',
        'last_lat': float(user['last_lat']) if user.get('last_lat') is not None else None,
        'last_lng': float(user['last_lng']) if user.get('last_lng') is not None else None,
        'last_location_updated': user['last_location_updated'].isoformat() if user.get('last_location_updated') else None,
        'admin_station_id': admin_station_id,
        'admin_station_ids': [admin_station_id] if admin_station_id else [],
        'selected_station_id': user.get('selected_station_id'),
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
    role = (data.get('role') or 'user').strip().lower()
    admin_station_id = as_int_or_none(data.get('admin_station_id'))

    if not all([first_name, last_name, email, phone, password]):
        return jsonify({'error': 'All signup fields are required'}), 400

    if role not in ('user', 'admin'):
        return jsonify({'error': 'Choose either user or administrator role'}), 400

    if role == 'admin' and not admin_station_id:
        return jsonify({'error': 'Choose the station this administrator manages'}), 400

    ensure_user_station_columns()
    conn = get_db()
    cur = conn.cursor()

    if role == 'admin':
        if not station_exists(cur, admin_station_id):
            cur.close()
            conn.close()
            return jsonify({'error': 'Selected station does not exist'}), 404
        if not admin_station_is_available(cur, admin_station_id):
            cur.close()
            conn.close()
            return jsonify({'error': 'This station already has an administrator'}), 409

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
            user_id, first_name, last_name, email, phone, password, role, admin_station_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (next_user_id, first_name, last_name, email, phone, hash_password(password), role, admin_station_id if role == 'admin' else None))
    sync_account_data(cur, next_user_id)
    conn.commit()

    cur.execute("""
        SELECT user_id, first_name, last_name, email, phone, password, role,
               last_lat, last_lng, last_location_updated, admin_station_id, selected_station_id
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
    requested_role = (data.get('role') or '').strip().lower()
    requested_station_id = as_int_or_none(data.get('admin_station_id'))

    if user_id in (None, '') or not password:
        return jsonify({'error': 'User ID and password are required'}), 400

    if requested_role and requested_role not in ('user', 'admin'):
        return jsonify({'error': 'Choose either user or administrator role'}), 400

    if requested_role == 'admin' and not requested_station_id:
        return jsonify({'error': 'Choose the station this administrator manages'}), 400

    ensure_user_station_columns()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, first_name, last_name, email, phone, password, role,
               last_lat, last_lng, last_location_updated, admin_station_id, selected_station_id
        FROM `User`
        WHERE user_id = %s
        LIMIT 1
    """, (user_id,))
    user = cur.fetchone()

    if not user or not password_matches(user.get('password'), password):
        record_login_attempt(int(user_id), False, user['user_id'] if user else None)
        cur.close()
        conn.close()
        return jsonify({'error': 'Invalid user ID or password'}), 401

    actual_role = (user.get('role') or 'user').lower()
    if requested_role and requested_role != actual_role:
        record_login_attempt(int(user_id), False, user['user_id'])
        cur.close()
        conn.close()
        return jsonify({'error': f'This account is registered as {actual_role}. Choose the correct role.'}), 403

    if actual_role == 'admin':
        if not station_exists(cur, requested_station_id):
            cur.close()
            conn.close()
            return jsonify({'error': 'Selected station does not exist'}), 404

        assigned_station_id = user.get('admin_station_id')
        if assigned_station_id and int(assigned_station_id) != requested_station_id:
            record_login_attempt(int(user_id), False, user['user_id'])
            cur.close()
            conn.close()
            return jsonify({'error': 'This administrator is assigned to a different station'}), 403

        if not assigned_station_id:
            if not admin_station_is_available(cur, requested_station_id, user['user_id']):
                record_login_attempt(int(user_id), False, user['user_id'])
                cur.close()
                conn.close()
                return jsonify({'error': 'This station already has an administrator'}), 409
            cur.execute("UPDATE `User` SET admin_station_id = %s WHERE user_id = %s", (requested_station_id, user['user_id']))
            user['admin_station_id'] = requested_station_id
        sync_account_data(cur, user['user_id'])
        conn.commit()

    record_login_attempt(int(user_id), True, user['user_id'])
    cur.close()
    conn.close()

    return jsonify({'message': 'Login successful', 'user': serialize_user(user)})


@users_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    email = (data.get('email') or '').strip()
    new_password = data.get('new_password') or ''

    if user_id in (None, '') or not email or not new_password:
        return jsonify({'error': 'User ID, email, and new password are required'}), 400

    ensure_user_station_columns()
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
    sync_account_data(cur, user['user_id'])
    conn.commit()
    cur.close()
    conn.close()
    record_password_reset(int(user_id), user['user_id'])

    return jsonify({'message': 'Password reset successful. Please log in with your new password.'})


@users_bp.route('/api/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    ensure_user_station_columns()
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, first_name, last_name, email, phone, password, role,
               last_lat, last_lng, last_location_updated, admin_station_id, selected_station_id
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


@users_bp.route('/api/users/<int:user_id>/selected-station', methods=['POST'])
def select_station(user_id):
    data = request.get_json() or {}
    station_id = as_int_or_none(data.get('station_id'))

    if not station_id:
        return jsonify({'error': 'Station ID is required'}), 400

    ensure_user_station_columns()
    conn = get_db()
    cur = conn.cursor()

    if not station_exists(cur, station_id):
        cur.close()
        conn.close()
        return jsonify({'error': 'Selected station does not exist'}), 404

    cur.execute("""
        SELECT user_id, role
        FROM `User`
        WHERE user_id = %s
        LIMIT 1
    """, (user_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    if (user.get('role') or 'user').lower() == 'admin':
        cur.close()
        conn.close()
        return jsonify({'error': 'Administrators do not select user stations'}), 403

    cur.execute("UPDATE `User` SET selected_station_id = %s WHERE user_id = %s", (station_id, user_id))
    sync_account_data(cur, user_id)
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Selected station updated', 'station_id': station_id})


@users_bp.route('/api/users/<int:user_id>/notifications/unread', methods=['GET'])
def get_unread_notifications(user_id):
    ensure_user_station_columns()
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT un.notification_id, un.user_id, un.session_id, un.notification_type, un.message,
               un.billing_amount, un.is_read, un.created_at,
               cs.start_time, cs.end_time, cs.energy_consumed, cs.total_cost,
               TIMESTAMPDIFF(MINUTE, cs.start_time, cs.end_time) AS duration_minutes,
               cp.charging_point_id, cp.power_rating, cp.price,
               s.station_id, s.name AS station_name, s.street, s.city, s.state, s.zip,
               u.first_name, u.last_name, u.email, u.phone
        FROM UserNotification un
        LEFT JOIN ChargingSession cs ON un.session_id = cs.session_id
        LEFT JOIN ChargingPoint cp ON cs.charging_point_id = cp.charging_point_id
        LEFT JOIN ChargingStation s ON cp.station_id = s.station_id
        LEFT JOIN `User` u ON un.user_id = u.user_id
        WHERE un.user_id = %s AND un.is_read = 0
        ORDER BY un.created_at ASC
        LIMIT 10
    """, (user_id,))
    notifications = [serialize_row(row) for row in cur.fetchall()]

    cur.close()
    conn.close()
    return jsonify(notifications)


@users_bp.route('/api/users/<int:user_id>/notifications/read', methods=['POST'])
def mark_notifications_read(user_id):
    data = request.get_json() or {}
    notification_ids = data.get('notification_ids') or []

    notification_ids = [as_int_or_none(notification_id) for notification_id in notification_ids]
    notification_ids = [notification_id for notification_id in notification_ids if notification_id]

    if not notification_ids:
        return jsonify({'message': 'No notifications to mark'})

    ensure_user_station_columns()
    conn = get_db()
    cur = conn.cursor()
    placeholders = ', '.join(['%s'] * len(notification_ids))
    cur.execute(f"""
        UPDATE UserNotification
        SET is_read = 1
        WHERE user_id = %s AND notification_id IN ({placeholders})
    """, (user_id, *notification_ids))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Notifications marked as read'})
