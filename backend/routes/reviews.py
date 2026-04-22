from flask import Blueprint, request, jsonify
from db import get_db

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/api/reviews/<int:station_id>', methods=['GET'])
def get_reviews(station_id):
    conn = get_db()
    cur = conn.cursor()
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
    data = request.get_json()
    user_id = data.get('user_id')
    station_id = data.get('station_id')
    rating = data.get('rating')
    review_text = data.get('review_text', '')

    if not all([user_id, station_id, rating]):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Review (user_id, station_id, rating, review_text, review_date)
        VALUES (%s, %s, %s, %s, NOW())
    """, (user_id, station_id, rating, review_text))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Review submitted successfully'})
