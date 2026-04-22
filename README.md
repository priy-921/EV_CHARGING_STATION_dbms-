# ⚡ EVFinder — EV Charging Station Finder

A complete full-stack web application for finding and managing EV charging stations in Pune, built as a DBMS Mini Project.

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Database** | MySQL 8.0 |
| **Backend** | Python Flask + Flask-CORS |
| **ML Model** | scikit-learn (Random Forest Regressor) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Maps** | Leaflet.js (OpenStreetMap) |
| **Charts** | Chart.js |

## 📁 Project Structure

```
ev-charging-project/
├── seed.sql                    # Database seed data (INSERT only)
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── db.py                   # MySQL connection helper
│   ├── requirements.txt        # Python dependencies
│   ├── routes/
│   │   ├── stations.py         # Station endpoints (Haversine search)
│   │   ├── sessions.py         # Charging session & estimate endpoints
│   │   ├── vehicles.py         # Vehicle endpoints
│   │   ├── reviews.py          # Review endpoints
│   │   └── predict.py          # ML prediction endpoint
│   └── ml/
│       ├── generate_data.py    # Training data generator
│       ├── train.py            # Random Forest model training
│       └── model.pkl           # Trained model (generated)
├── frontend/
│   ├── index.html              # Map page (Leaflet.js)
│   ├── station.html            # Station detail page
│   ├── calculator.html         # Charging calculator
│   ├── profile.html            # User profile & session history
│   ├── css/
│   │   └── style.css           # Global stylesheet
│   └── js/
│       ├── api.js              # Shared API client & utilities
│       ├── map.js              # Map page logic
│       ├── station.js          # Station page logic
│       └── calculator.js       # Calculator page logic
└── README.md
```

## 🚀 Setup & Run — Step by Step

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

### Step 1: Create the Database & Tables

Open MySQL and run:

```sql
CREATE DATABASE IF NOT EXISTS ev_charging_station;
USE ev_charging_station;

-- Create tables (run your CREATE TABLE statements first)
-- Tables needed: ChargingStation, ChargingPoint, ChargingPointStatus,
-- ChargerType, ConnectorType, OpeningHours, User, Vehicle,
-- VehicleConnector, ChargingSession, Review, AvailabilityLog
```

> **Note:** The 10 ChargingStations, 28 ChargingPoints, 5 ConnectorTypes, 5 ChargerTypes, and 5 ChargingPointStatus records should already exist.

### Step 2: Run the Seed File

```bash
mysql -u root -p ev_charging_station < seed.sql
```

Or open MySQL Workbench and run `seed.sql` manually.

### Step 3: Configure Database Password

Open `backend/db.py` and change `YOUR_PASSWORD` to your MySQL root password:

```python
passwd='YOUR_PASSWORD',  # ← Change this
```

### Step 4: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 5: Train the ML Model

```bash
cd backend/ml
python generate_data.py
python train.py
```

This will generate `training_data.csv` and `model.pkl`.

### Step 6: Start the Flask Server

```bash
cd backend
python app.py
```

The server starts at `http://localhost:5000`.

### Step 7: Open the App

Open your browser and go to:
- **Map:** [http://localhost:5000](http://localhost:5000)
- **Station Detail:** [http://localhost:5000/station.html?id=1](http://localhost:5000/station.html?id=1)
- **Calculator:** [http://localhost:5000/calculator.html](http://localhost:5000/calculator.html)
- **Profile:** [http://localhost:5000/profile.html](http://localhost:5000/profile.html)

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stations?lat=&lng=&radius=` | Find nearest stations (Haversine) |
| GET | `/api/stations/<id>` | Station detail with charging points |
| GET | `/api/stations/<id>/peak-hours` | Hourly session counts for charts |
| GET | `/api/vehicles` | List all vehicles with specs |
| GET | `/api/vehicles/<id>/connectors` | Vehicle connector compatibility |
| GET | `/api/sessions/<user_id>` | User's charging session history |
| GET | `/api/reviews/<station_id>` | Station reviews |
| POST | `/api/estimate` | Calculate charging time & cost |
| POST | `/api/session/start` | Start a charging session |
| POST | `/api/session/end` | End a charging session |
| POST | `/api/review` | Submit a review |
| POST | `/api/predict/wait` | ML predicted wait time |

## 🤖 ML Model

- **Algorithm:** Random Forest Regressor
- **Features:** station_id, hour_of_day, day_of_week, total_charging_points
- **Target:** wait_time_minutes
- **Training Data:** Generated from AvailabilityLog patterns + synthetic augmentation

## 🎨 Design

- **Background:** Clean white (#FFFFFF)
- **Accent Color:** Green (#1D9E75)
- **Font:** Inter (Google Fonts)
- **Mobile Responsive:** Yes
- **Animations:** Smooth transitions, hover effects, pulse animation on emergency button

## 📊 Database Tables

| Table | Records |
|-------|---------|
| ChargingStation | 10 (pre-existing) |
| ChargingPoint | 28 (pre-existing) |
| ConnectorType | 5 (pre-existing) |
| ChargerType | 5 (pre-existing) |
| ChargingPointStatus | 5 (pre-existing) |
| User | 20 (seeded) |
| Vehicle | 10 (seeded) |
| VehicleConnector | 17 (seeded) |
| OpeningHours | 70 (seeded) |
| ChargingSession | 300 (seeded) |
| Review | 100 (seeded) |
| AvailabilityLog | 500 (seeded) |

## 👩‍💻 Authors

DBMS Mini Project — EV Charging Station Finder
