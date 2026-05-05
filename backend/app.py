from flask import Flask, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder=None)
CORS(app)

# Import and register route blueprints
from routes.stations import stations_bp
from routes.sessions import sessions_bp
from routes.vehicles import vehicles_bp
from routes.reviews import reviews_bp
from routes.predict import predict_bp
from routes.users import users_bp
from routes.admin import admin_bp

app.register_blueprint(stations_bp)
app.register_blueprint(sessions_bp)
app.register_blueprint(vehicles_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(users_bp)
app.register_blueprint(admin_bp)

# Serve frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'login.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    return send_from_directory(FRONTEND_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
