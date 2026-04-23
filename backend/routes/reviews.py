from flask import Blueprint, request, jsonify
from db import get_db
import ast
import os
import re

reviews_bp = Blueprint('reviews', __name__)


def load_seed_review_rows():
    seed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'seed.sql'))
    if not os.path.exists(seed_path):
        return []

    with open(seed_path, 'r', encoding='utf-8') as seed_file:
        seed_sql = seed_file.read()

    match = re.search(
        r"INSERT INTO `Review` \(user_id, station_id, rating, review_text, review_date\) VALUES\s*(.*?);",
        seed_sql,
        re.S,
    )
    if not match:
        return []

    values_text = '[' + match.group(1).strip() + ']'
    return ast.literal_eval(values_text)


def load_seed_user_rows():
    seed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'seed.sql'))
    if not os.path.exists(seed_path):
        return []

    with open(seed_path, 'r', encoding='utf-8') as seed_file:
        seed_sql = seed_file.read()

    match = re.search(
        r"INSERT INTO `User` \(user_id, first_name, last_name, email, phone, password, role, last_lat, last_lng, last_location_updated\) VALUES\s*(.*?);",
        seed_sql,
        re.S,
    )
    if not match:
        return []

    values_text = '[' + match.group(1).strip() + ']'
    return ast.literal_eval(values_text)


def ensure_seed_users(cur, conn):
    seed_users = load_seed_user_rows()
    if not seed_users:
        return

    cur.execute("SHOW COLUMNS FROM `User`")
    user_columns = {row['Field'] for row in cur.fetchall()}

    cur.execute("SELECT user_id FROM `User`")
    existing_user_ids = {row['user_id'] for row in cur.fetchall()}

    inserts = []
    for user in seed_users:
        user_id, first_name, last_name, email, phone, password, role, last_lat, last_lng, last_location_updated = user
        if user_id in existing_user_ids:
            continue
        row = {
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'password': password,
            'role': role,
            'last_lat': last_lat,
            'last_lng': last_lng,
            'last_location_updated': last_location_updated,
        }
        inserts.append(row)

    if not inserts:
        return

    insert_columns = [
        column for column in [
            'user_id', 'first_name', 'last_name', 'email', 'phone', 'password',
            'role', 'last_lat', 'last_lng', 'last_location_updated'
        ]
        if column in user_columns
    ]
    placeholders = ', '.join(['%s'] * len(insert_columns))
    column_sql = ', '.join(f'`{column}`' for column in insert_columns)
    insert_values = [tuple(row[column] for column in insert_columns) for row in inserts]

    cur.executemany(f"""
        INSERT INTO `User` ({column_sql})
        VALUES ({placeholders})
    """, insert_values)
    conn.commit()


def ensure_seed_reviews(cur, conn):
    ensure_seed_users(cur, conn)

    cur.execute("SELECT COUNT(*) AS review_count FROM Review")
    review_count = cur.fetchone()['review_count']
    seed_rows = load_seed_review_rows()
    if not seed_rows:
        return

    cur.execute("SELECT review_text FROM Review")
    existing_texts = {row['review_text'] for row in cur.fetchall()}

    cur.execute("SELECT COALESCE(MAX(review_id), 0) + 1 AS next_review_id FROM Review")
    next_review_id = cur.fetchone()['next_review_id']

    inserts = []
    for seed_user_id, station_id, rating, review_text, review_date in seed_rows:
        if review_text in existing_texts:
            continue
        inserts.append((next_review_id, seed_user_id, station_id, rating, review_text, review_date))
        next_review_id += 1

    if inserts:
        cur.executemany("""
            INSERT INTO Review (review_id, user_id, station_id, rating, review_text, review_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, inserts)

    # If demo reviews were previously inserted while only a few users existed,
    # restore their original seeded authors now that the demo users exist.
    remaps = [(seed_user_id, review_text) for seed_user_id, _station_id, _rating, review_text, _review_date in seed_rows]
    cur.executemany("""
        UPDATE Review
        SET user_id = %s
        WHERE review_text = %s
    """, remaps)
    conn.commit()


@reviews_bp.route('/api/reviews/<int:station_id>', methods=['GET'])
def get_reviews(station_id):
    conn = get_db()
    cur = conn.cursor()
    ensure_seed_reviews(cur, conn)
    cur.execute("""
        SELECT r.review_id, r.rating, r.review_text, r.review_date,
               u.first_name, u.last_name
        FROM Review r
        JOIN User u ON r.user_id = u.user_id
        WHERE r.station_id = %s
        ORDER BY r.review_date DESC
    """, (station_id,))
    reviews = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for r in reviews:
        row = {}
        for key, val in r.items():
            if hasattr(val, 'isoformat'):
                row[key] = val.isoformat()
            elif isinstance(val, (int, float, str, type(None))):
                row[key] = val
            else:
                row[key] = float(val) if val is not None else None
        result.append(row)

    return jsonify(result)


@reviews_bp.route('/api/review', methods=['POST'])
def post_review():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    station_id = data.get('station_id')
    rating = data.get('rating')
    review_text = (data.get('review_text') or '').strip()

    if user_id in (None, '') or station_id in (None, '') or rating in (None, ''):
        return jsonify({'error': 'User, station, and rating are required'}), 400

    try:
        user_id = int(user_id)
        station_id = int(station_id)
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({'error': 'Review fields contain invalid values'}), 400

    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    if not review_text:
        return jsonify({'error': 'Review text is required'}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM `User` WHERE user_id = %s LIMIT 1", (user_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    cur.execute("SELECT station_id FROM ChargingStation WHERE station_id = %s LIMIT 1", (station_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'error': 'Station not found'}), 404

    cur.execute("SELECT COALESCE(MAX(review_id), 0) + 1 AS next_review_id FROM Review")
    review_id = cur.fetchone()['next_review_id']

    cur.execute("""
        INSERT INTO Review (review_id, user_id, station_id, rating, review_text, review_date)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """, (review_id, user_id, station_id, rating, review_text))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Review submitted successfully'})
