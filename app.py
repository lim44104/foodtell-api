from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import logging
import json
import re
from config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests (important for Android)

# Load config
app.config.from_object(Config)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return "✅ Restaurant API is running!"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(app.config['DATABASE_URI'])
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Query all restaurants
        cursor.execute("""
            SELECT restaurantid, name, rating, pricerange, address, phoneno,
                   websiteurl, menuurl, reservationurl, eaterycategory, description,
                   tags, reviewkeywords, openinghours, latlng, reviewcount,
                   featuredimage, mall
            FROM restaurant
        """)
        rows = cursor.fetchall()

        restaurant_list = []

        for row in rows:
            def parse_json(val):
                if val is None:
                    return None
                try:
                    return json.loads(val)
                except Exception:
                    return val

            def clean(val):
                return None if str(val).strip() in ("NaN", "nan", "None", "") else val

            # Fix: Parse latlng string safely
            lat, lng = None, None
            if row['latlng']:
                try:
                    match = re.findall(r"[-+]?[0-9]*\.?[0-9]+", str(row['latlng']))
                    if len(match) == 2:
                        lat = float(match[0])
                        lng = float(match[1])
                    else:
                        logger.warning(f"Unexpected latlng format: {row['latlng']}")
                except Exception as e:
                    logger.warning(f"Failed to parse latlng: {row['latlng']} - {e}")

            restaurant = {
                'restaurantid': row['restaurantid'],
                'name': row['name'],
                'rating': float(row['rating']) if row['rating'] is not None else None,
                'pricerange': clean(row['pricerange']),
                'address': row['address'],
                'phoneno': clean(row['phoneno']),
                'websiteurl': row['websiteurl'],
                'menuurl': parse_json(row['menuurl']),
                'reservationurl': row['reservationurl'],
                'eaterycategory': row['eaterycategory'],
                'description': clean(row['description']),
                'tags': parse_json(row['tags']),
                'reviewkeywords': parse_json(row['reviewkeywords']),
                'openinghours': parse_json(row['openinghours']),
                'latitude': lat,
                'longitude': lng,
                'reviewcount': row['reviewcount'],
                'featuredimage': row['featuredimage'],
                'mall': row['mall']
            }
            restaurant_list.append(restaurant)

        cursor.close()
        conn.close()

        return jsonify(restaurant_list), 200

    except Exception as e:
        logger.error(f"Error fetching restaurants: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
