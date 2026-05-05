# EVFinder - EV Charging Station Finder

## Mini Project Report Content

### Title

EVFinder: EV Charging Station Finder and Management System

### Abstract

EVFinder is a full-stack web application developed as a DBMS mini project to help electric vehicle users find nearby charging stations, check charger availability, calculate charging cost and time, book or start charging sessions, manage their vehicle profile, view charging history, and submit station reviews. The system uses a MySQL database to store users, vehicles, stations, charging points, connector types, charger types, charging sessions, reviews, opening hours, and availability logs. A Python Flask backend provides REST API endpoints, while the frontend is built using HTML, CSS, and vanilla JavaScript. The map interface uses Leaflet.js with OpenStreetMap, and Chart.js is used to display station peak-hour analytics. The project also includes a machine learning module using a Random Forest Regressor to predict estimated waiting time based on station, hour, day, and number of charging points.

The main aim of this project is to create a database-driven EV charging management platform that improves the user experience for EV owners and demonstrates practical DBMS concepts such as relational schema design, primary keys, foreign keys, many-to-many relationships, joins, aggregation queries, transaction records, and data-driven decision support.

### Introduction

The adoption of electric vehicles is increasing, and one of the major challenges for EV users is finding reliable charging infrastructure. Users need information such as station location, connector compatibility, charger status, pricing, reviews, charging history, and waiting time. Without a centralized system, it becomes difficult to plan charging sessions efficiently.

EVFinder solves this problem by providing a single platform where users can log in, find nearby EV charging stations on a map, filter stations based on compatible connectors, view station details, estimate charging cost and time, book charging points, start and end sessions, and review stations. The system is backed by a structured MySQL database and uses a Flask API layer to connect the frontend with the database.

### Problem Statement

To design and implement a database management system for EV charging stations that allows users to locate charging stations, check charging point details, manage vehicles, calculate charging requirements, record charging sessions, and view station reviews and peak usage trends.

### Objectives

- To design a normalized relational database for EV charging station management.
- To store and manage users, vehicles, stations, charging points, connector types, charger types, charging sessions, reviews, opening hours, and availability logs.
- To provide a user-friendly frontend for login, station search, charging calculator, station details, and profile management.
- To calculate charging time and cost based on vehicle battery capacity, charger power, and price per kWh.
- To implement station search using latitude, longitude, radius, and the Haversine distance formula.
- To support connector compatibility between vehicles and charging stations.
- To allow users to book, start, and end charging sessions.
- To display peak-hour analytics for each station.
- To train and integrate a machine learning model for wait-time prediction.
- To demonstrate practical DBMS concepts such as primary keys, foreign keys, joins, junction tables, aggregation, and transaction records.

### Scope of the Project

The project focuses on EV charging stations in Pune. It supports user authentication, vehicle management, map-based station discovery, connector-based filtering, charging point booking, active charging sessions, charging cost estimation, review submission, and usage analytics. The system can be extended to support online payment, admin dashboards, real-time IoT charger updates, and route planning.

### Functional Requirements of the System

This system will contain details of EV users, vehicles, charging stations, charging points, connector types, charger types, charging sessions, reviews, and charger availability. It must allow users to register, log in, manage vehicle details, search nearby charging stations, check availability, estimate charging time and cost, book charging points, start and end sessions, and view charging history.

The functions performed by the system would be the following:

1. To allow new EV users to register themselves in the system.
2. To allow registered users to log into the system.
3. To allow users to reset their password when required.
4. To allow users to add and view their electric vehicle details.
5. To allow users to search for nearby charging stations using location and radius.
6. To allow users to filter charging stations based on compatible connector types.
7. To allow users to view station details such as address, opening hours, chargers, price, reviews, and wait time.
8. To allow users to calculate estimated charging time, energy required, and total cost.
9. To allow users to book, start, and end charging sessions.
10. To allow users to view their charging session history.
11. To allow users to submit ratings and reviews for charging stations.
12. To allow the system to display peak-hour analytics and predicted wait time.

#### Possible Users of the System with Privileges

The main users of the EV Charging Station Finder and Management System are EV users, registered customers, and system/database administrators.

#### EV User

An EV user is anyone who wants to find a suitable charging station for an electric vehicle. The user can register, log in, search stations, view charger availability, calculate charging cost and time, book or start sessions, and submit reviews. No special technical training is required; the user only needs to operate simple forms, buttons, and search options.

Privileges of EV users:

- Register and log into the system.
- Add and view vehicle details.
- Search and filter nearby charging stations.
- View station, charger, price, status, and review details.
- Book, start, and end charging sessions.
- View charging session history.
- Use charging calculator, reviews, peak-hour chart, and wait-time prediction.

#### Registered Customer

A registered customer is an EV user who has created an account and saved vehicle information. The system uses saved vehicle details to identify compatible connectors and provide better station filtering.

Privileges of registered customers:

- Access all EV user features.
- Maintain vehicle records and profile details.
- View session history, total energy consumed, amount spent, and estimated CO2 savings.
- Get connector-compatible station filtering based on saved vehicles.

#### System/Database Administrator

The system/database administrator is responsible for maintaining the backend database and ensuring that station, charger, user, and session data remain consistent. In this project, a separate admin dashboard is not implemented, but the database supports administrative maintenance through MySQL and backend logic.

Privileges of system/database administrators:

- Manage database tables and records.
- Add or update charging station and charging point data.
- Monitor users, vehicles, sessions, reviews, and availability logs.
- Check login, signup, and password reset audit records.
- Maintain connector, charger, status, and ML training data.

#### System Privileges and Automated Functions

Apart from direct user actions, the system calculates distance using the Haversine formula, computes charging cost and time, updates charging point status during booking/session actions, generates peak-hour analytics, creates audit records, and predicts wait time using the trained machine learning model.

### Technology Stack

| Layer | Technology Used |
|---|---|
| Database | MySQL 8.0 |
| Backend | Python Flask |
| API Support | Flask-CORS |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Maps | Leaflet.js and OpenStreetMap |
| Charts | Chart.js |
| Machine Learning | scikit-learn Random Forest Regressor |
| Data Processing | pandas, NumPy |
| Model Storage | joblib |

### Project Structure

```text
ev-charging-station/
|-- seed.sql
|-- README.md
|-- DATABASE_DEMO_SCRIPT.md
|-- backend/
|   |-- app.py
|   |-- db.py
|   |-- requirements.txt
|   |-- routes/
|   |   |-- stations.py
|   |   |-- sessions.py
|   |   |-- vehicles.py
|   |   |-- reviews.py
|   |   |-- users.py
|   |   |-- predict.py
|   |-- ml/
|       |-- generate_data.py
|       |-- train.py
|       |-- training_data.csv
|       |-- model.pkl
|-- frontend/
|   |-- login.html
|   |-- index.html
|   |-- station.html
|   |-- calculator.html
|   |-- profile.html
|   |-- css/
|   |   |-- style.css
|   |-- js/
|       |-- api.js
|       |-- login.js
|       |-- map.js
|       |-- station.js
|       |-- calculator.js
```

### System Architecture

The system follows a three-tier architecture:

1. Frontend Layer: The user interacts with HTML pages such as login, map, station details, calculator, and profile. JavaScript files call backend APIs and update the UI dynamically.
2. Backend Layer: Flask exposes REST API endpoints for authentication, station search, session handling, vehicle management, reviews, and wait-time prediction.
3. Database Layer: MySQL stores all persistent records including user details, station details, vehicle data, sessions, reviews, and availability logs.

The frontend sends HTTP requests to the Flask backend. The backend uses the database helper in `db.py` to connect to MySQL, execute SQL queries, and return JSON responses to the frontend.

### Main Features Implemented

#### User Authentication

The system includes login, signup, and password reset features. Existing users can log in using user ID and password. New users can create an account, and the backend stores passwords using SHA-256 hashing for newly created or reset passwords. The system also creates audit tables for login attempts, password resets, and signup events.

Implemented APIs:

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/reset-password`

Additional audit tables:

- `LoginAudit`
- `PasswordResetAudit`
- `SignupAudit`

#### Station Search and Map View

The map page allows users to view EV charging stations. The backend supports station search using latitude, longitude, and radius. It uses the Haversine formula to calculate distance between the user's location and charging stations. Stations are ordered by nearest distance.

Implemented API:

- `GET /api/stations?lat=&lng=&radius=&connector_ids=`

Key functions:

- Nearby station search
- Radius-based filtering
- Available charging point count
- Total charging point count
- Connector-based station filtering

#### Station Detail Page

The station detail page shows station address, contact information, charging points, connector type, charger type, status, power rating, price, opening hours, peak-hour chart, predicted wait time, and user reviews.

Implemented APIs:

- `GET /api/stations/<station_id>`
- `GET /api/stations/<station_id>/peak-hours`
- `GET /api/reviews/<station_id>`
- `POST /api/review`

#### Vehicle Management

Users can view vehicles saved in their profile and add new vehicles. Vehicles store brand, model, segment, battery capacity, AC charging limit, and DC charging limit. The backend also infers connector compatibility when required.

Implemented APIs:

- `GET /api/vehicles`
- `POST /api/vehicles`
- `GET /api/vehicles/<vehicle_id>/connectors`
- `GET /api/users/<user_id>/profile`

#### Charging Calculator

The calculator estimates the energy required, charging speed, charging time, and total cost. It considers:

- Vehicle battery capacity
- Current battery percentage
- Target battery percentage
- Charger power rating
- Vehicle AC/DC charging limit
- Charger price per kWh

Formula used:

```text
kWh required = ((target percentage - current percentage) / 100) * battery capacity
charging rate = minimum(charger power rating, vehicle supported charging rate)
time in minutes = (kWh required / charging rate) * 60
cost = kWh required * price per kWh
```

Implemented API:

- `POST /api/estimate`

#### Charging Session Booking and Management

The system allows users to book a charging point, start a session, start a booked session, and end a session. When a session starts, the charging point status changes to "In Use". When the session ends, energy consumed and total cost are stored, and the point becomes "Available" again.

Implemented APIs:

- `POST /api/session/book`
- `POST /api/session/start`
- `POST /api/session/end`
- `GET /api/sessions/<user_id>`

#### Profile and Session History

The profile page displays user details, saved vehicles, total sessions, monthly sessions, total energy used, estimated CO2 saved, and charging session history. Users can add new vehicles from this page.

#### Reviews

Users can submit station reviews with a rating from 1 to 5 and review text. The station detail page displays reviews with reviewer names and dates. Seeded demo reviews are also restored automatically if missing.

Implemented APIs:

- `GET /api/reviews/<station_id>`
- `POST /api/review`

#### Peak-Hour Analytics

The station detail page shows hourly session counts using Chart.js. The backend groups charging sessions by hour and returns counts for all 24 hours.

Implemented API:

- `GET /api/stations/<station_id>/peak-hours`

#### Machine Learning Wait-Time Prediction

The project includes a machine learning module that predicts estimated waiting time in minutes. The model uses a Random Forest Regressor.

Features used:

- `station_id`
- `hour_of_day`
- `day_of_week`
- `total_charging_points`

Target variable:

- `wait_time_minutes`

ML files:

- `backend/ml/generate_data.py`
- `backend/ml/train.py`
- `backend/ml/training_data.csv`
- `backend/ml/model.pkl`

Implemented API:

- `POST /api/predict/wait`

If the model file is not found, the backend returns a default wait time of 10 minutes.

### Database Design

The database name used in the project is:

```sql
ev_charging_station
```

The database contains master tables, transaction tables, relationship tables, and audit tables.

### Database Tables

#### 1. User

Stores registered user details.

Important attributes:

- `user_id`
- `first_name`
- `last_name`
- `email`
- `phone`
- `password`
- `role`
- `last_lat`
- `last_lng`
- `last_location_updated`

Relationships:

- One user can own multiple vehicles.
- One user can have multiple charging sessions.
- One user can submit multiple reviews.

#### 2. Vehicle

Stores electric vehicle details.

Important attributes:

- `vehicle_id`
- `user_id`
- `model`
- `brand`
- `battery_capacity`
- `max_ac_kw`
- `max_dc_kw`
- `segment`

Relationships:

- Many vehicles belong to one user.
- One vehicle can support multiple connector types through `VehicleConnector`.

#### 3. ConnectorType

Stores connector standards.

Examples:

- Type 1 J1772
- Type 2 Mennekes
- Bharat AC-001
- CCS2 Combo 2
- CHAdeMO

#### 4. ChargerType

Stores charger technology categories.

Examples:

- Type 2 AC
- CCS2 DC
- Bharat AC-001
- Bharat DC-001
- CHAdeMO DC

#### 5. VehicleConnector

Junction table between `Vehicle` and `ConnectorType`.

Purpose:

- Represents many-to-many relationship.
- One vehicle can support many connectors.
- One connector can be supported by many vehicles.

#### 6. ChargingStation

Stores station-level information.

Important attributes:

- `station_id`
- `name`
- `street`
- `city`
- `state`
- `zip`
- `contact`
- `latitude`
- `longitude`

Purpose:

- Represents a physical charging station.
- Latitude and longitude support map search.

#### 7. OpeningHours

Stores opening and closing time for each station and day.

Important attributes:

- `hours_id`
- `station_id`
- `day_of_week`
- `open_time`
- `close_time`

#### 8. ChargingPointStatus

Master table for charging point status.

Statuses:

- Available
- In Use
- Out of Service
- Faulted
- Reserved

#### 9. ChargingPoint

Stores individual chargers available inside a station.

Important attributes:

- `charging_point_id`
- `station_id`
- `connector_type_id`
- `charger_type_id`
- `status_id`
- `power_rating`
- `price`

Relationships:

- Each station can have many charging points.
- Each charging point has one connector type, one charger type, and one status.
- Charging sessions happen on charging points.

#### 10. ChargingSession

Stores charging transaction data.

Important attributes:

- `session_id`
- `charging_point_id`
- `user_id`
- `start_time`
- `end_time`
- `energy_consumed`
- `total_cost`

Purpose:

- Maintains user charging history.
- Supports billing and analytics.
- Used for peak-hour charts.

#### 11. Review

Stores user feedback for stations.

Important attributes:

- `review_id`
- `user_id`
- `station_id`
- `rating`
- `review_text`
- `review_date`

#### 12. AvailabilityLog

Stores historical availability data for charging points.

Important attributes:

- `log_id`
- `charging_point_id`
- `status`
- `logged_at`

Purpose:

- Used for tracking charger availability patterns.
- Used for generating machine learning training data.

#### 13. LoginAudit

Stores login attempt records.

Important attributes:

- `audit_id`
- `user_id`
- `user_id_input`
- `success`
- `event_time`
- `ip_address`

#### 14. PasswordResetAudit

Stores password reset records.

Important attributes:

- `reset_id`
- `user_id`
- `user_id_input`
- `reset_time`
- `ip_address`

#### 15. SignupAudit

Stores signup event records.

Important attributes:

- `signup_audit_id`
- `user_id`
- `email`
- `event_time`
- `ip_address`

### Relationships

- `User` to `Vehicle`: One-to-many
- `User` to `ChargingSession`: One-to-many
- `User` to `Review`: One-to-many
- `Vehicle` to `ConnectorType`: Many-to-many through `VehicleConnector`
- `ChargingStation` to `ChargingPoint`: One-to-many
- `ChargingStation` to `OpeningHours`: One-to-many
- `ChargingStation` to `Review`: One-to-many
- `ConnectorType` to `ChargingPoint`: One-to-many
- `ChargerType` to `ChargingPoint`: One-to-many
- `ChargingPointStatus` to `ChargingPoint`: One-to-many
- `ChargingPoint` to `ChargingSession`: One-to-many
- `ChargingPoint` to `AvailabilityLog`: One-to-many

### Data Seeded in the Project

The `seed.sql` file adds sample data for demonstration and testing.

| Table | Records |
|---|---:|
| ChargingStation | 10 pre-existing records |
| ChargingPoint | 28 pre-existing records |
| ConnectorType | 5 pre-existing records |
| ChargerType | 5 pre-existing records |
| ChargingPointStatus | 5 pre-existing records |
| User | 20 seeded records |
| Vehicle | 10 seeded records |
| VehicleConnector | 17 seeded records |
| OpeningHours | 70 seeded records |
| ChargingSession | 300 generated records |
| Review | 100 seeded records |
| AvailabilityLog | 500 generated records |

### Important SQL Concepts Used

- Primary keys for unique identification.
- Foreign keys for referential integrity.
- Junction table for many-to-many relationship between vehicles and connectors.
- Joins for combining station, charger, connector, status, user, and review data.
- Aggregate functions such as `COUNT`.
- `GROUP BY` for peak-hour analytics.
- `ORDER BY` for sorting stations, reviews, sessions, and hours.
- Stored procedures in `seed.sql` for generating charging sessions and availability logs.
- Subqueries for calculating available and total charging points.
- Haversine formula in SQL for location-based distance calculation.

### Backend Implementation

The backend is implemented in Flask. The main file is `backend/app.py`, which registers all route blueprints and serves frontend files. The database connection logic is written in `backend/db.py`.

Database connection details:

- Database: `ev_charging_station`
- User: configurable through `EVFINDER_DB_USER`
- Password: configurable through `EVFINDER_DB_PASSWORD`
- Supported connection attempts:
  - `/private/tmp/mysql.sock`
  - `/tmp/mysql.sock`
  - `127.0.0.1:3306`
  - `localhost:3306`

The backend runs on:

```text
http://localhost:8000
```

### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/signup` | Create new user |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/reset-password` | Reset password |
| GET | `/api/users/<user_id>/profile` | Get user profile and vehicles |
| GET | `/api/stations` | Search stations |
| GET | `/api/stations/<station_id>` | Get station details |
| GET | `/api/stations/<station_id>/peak-hours` | Get peak-hour data |
| GET | `/api/vehicles` | List all vehicles |
| POST | `/api/vehicles` | Add a new vehicle |
| GET | `/api/vehicles/<vehicle_id>/connectors` | Get vehicle-compatible connectors |
| POST | `/api/estimate` | Estimate charging time and cost |
| POST | `/api/session/book` | Book charging point |
| POST | `/api/session/start` | Start session |
| POST | `/api/session/end` | End session |
| GET | `/api/sessions/<user_id>` | Get user session history |
| GET | `/api/reviews/<station_id>` | Get reviews |
| POST | `/api/review` | Submit review |
| POST | `/api/predict/wait` | Predict wait time |

### Frontend Pages

#### 1. Login Page

File: `frontend/login.html`

Features:

- Login form
- Signup form
- Password reset modal
- Stores logged-in user in browser local storage

#### 2. Map Page

File: `frontend/index.html`

Features:

- Displays stations on Leaflet map
- Shows station cards
- Search by location/name
- Find nearest fast charger
- Filter stations by connector compatibility
- Uses browser geolocation

#### 3. Station Detail Page

File: `frontend/station.html`

Features:

- Station details
- Charging point list
- Charger status badges
- Compatible vehicle selection
- Book/start/end session buttons
- Charging estimate form
- Wait-time prediction
- Peak-hour chart
- Review display and review submission

#### 4. Charging Calculator Page

File: `frontend/calculator.html`

Features:

- Select vehicle and charger
- Enter current and target battery percentage
- Calculate estimated kWh, time, charge rate, and cost

#### 5. Profile Page

File: `frontend/profile.html`

Features:

- User details
- Vehicle list
- Add vehicle form
- Charging session history
- Statistics such as total sessions, monthly sessions, total energy, spend, and CO2 saved

### Algorithms and Logic Used

#### Haversine Formula

Used to calculate distance between the user's current location and station coordinates.

```text
distance = 6371 * acos(
    cos(radians(user_lat)) * cos(radians(station_lat)) *
    cos(radians(station_lng) - radians(user_lng)) +
    sin(radians(user_lat)) * sin(radians(station_lat))
)
```

#### Charging Cost and Time Estimation

The backend calculates required energy, charge rate, charging duration, and total cost.

```text
kWh required = ((target_pct - battery_pct) / 100) * battery_capacity
charge rate = min(charging point power rating, vehicle max supported rate)
minutes = (kWh required / charge rate) * 60
cost = kWh required * price per kWh
```

#### Connector Compatibility

The system checks or infers connector compatibility using vehicle segment and DC charging capability.

- Two-wheelers and three-wheelers usually use Bharat AC-001.
- Four-wheelers use Type 2 Mennekes.
- Four-wheelers with DC support also use CCS2.

#### Peak-Hour Analytics

Charging sessions are grouped by start hour:

```sql
SELECT HOUR(start_time), COUNT(*)
FROM ChargingSession
GROUP BY HOUR(start_time);
```

#### ML Wait-Time Prediction

Random Forest Regressor predicts wait time using:

```text
station_id, hour_of_day, day_of_week, total_charging_points
```

### Testing

The project was tested through browser-based testing and API behavior checks.

Test cases covered:

| Test Case | Expected Result |
|---|---|
| User login with valid credentials | User is redirected to map page |
| Signup with new email/phone | New user is created |
| Signup with existing email/phone | Error message is shown |
| Station search with location | Nearby stations are displayed |
| Connector filter | Only compatible stations are shown |
| Open station detail page | Station, chargers, reviews, chart, and estimate section load |
| Book available charging point | Point status changes to Reserved |
| Start available charging point | Point status changes to In Use |
| End session | Session stores energy/cost and point becomes Available |
| Add vehicle | Vehicle appears in profile |
| Submit review | Review is saved and displayed |
| Charging calculator | kWh, time, rate, and cost are calculated |
| Wait-time prediction | Predicted wait time is displayed |

### Advantages

- Centralized database for EV charging station management.
- Location-based charging station discovery.
- Connector compatibility improves user convenience.
- Charging calculator helps users estimate time and cost.
- Booking and session management simulate real charging workflows.
- Review system helps users evaluate stations.
- Peak-hour analytics helps identify busy periods.
- ML-based wait-time prediction adds intelligent decision support.
- Clean responsive frontend with map and chart integration.

### Limitations

- The project uses demo/sample data instead of live charger IoT data.
- Payment gateway integration is not included.
- Admin dashboard is not implemented.
- Real-time charger status updates are simulated through database status changes.
- Password hashing is implemented, but a production system should use stronger password hashing such as bcrypt or Argon2.
- The ML model is trained on generated/synthetic data and can be improved with real historical usage data.

### Future Scope

- Add admin dashboard for managing stations, chargers, users, and reports.
- Integrate real-time IoT charger status updates.
- Add online payment and invoice generation.
- Add route planning with charging stops.
- Add notification system for booking confirmation and charger availability.
- Improve ML model using real historical demand and traffic data.
- Add support for multiple cities.
- Add station owner login and station management features.
- Add advanced analytics such as revenue reports and charger utilization.

### Conclusion

EVFinder successfully implements a DBMS-based EV charging station finder and management system. It demonstrates the use of relational database design, table relationships, foreign keys, many-to-many mapping, joins, aggregate queries, transaction records, and data analytics. The project connects a MySQL database with a Flask backend and an interactive frontend to provide a practical EV charging workflow. Users can log in, manage vehicles, find stations, check charger availability, calculate charging cost and time, book or start sessions, view session history, submit reviews, and see wait-time predictions. Overall, the project shows how DBMS concepts can be applied to a real-world electric vehicle charging use case.

### References

- MySQL Documentation
- Flask Documentation
- Leaflet.js Documentation
- OpenStreetMap
- Chart.js Documentation
- scikit-learn Documentation
- pandas and NumPy Documentation

### Suggested Screenshots to Add in the Final Report

- Login page
- Signup form
- Map page with station markers
- Station detail page
- Charging point list with status
- Charging calculator output
- Peak-hour chart
- Review section
- Profile page with vehicle list
- Session history table
- MySQL table data or ER diagram

### Suggested ER Diagram Entities

Use the following entities in the ER diagram:

- User
- Vehicle
- VehicleConnector
- ConnectorType
- ChargerType
- ChargingStation
- OpeningHours
- ChargingPointStatus
- ChargingPoint
- ChargingSession
- Review
- AvailabilityLog
- LoginAudit
- PasswordResetAudit
- SignupAudit

Main ER relationships:

- User owns Vehicle
- User creates ChargingSession
- User writes Review
- Vehicle supports ConnectorType through VehicleConnector
- ChargingStation has ChargingPoint
- ChargingStation has OpeningHours
- ChargingStation receives Review
- ChargingPoint uses ConnectorType
- ChargingPoint uses ChargerType
- ChargingPoint has ChargingPointStatus
- ChargingPoint records ChargingSession
- ChargingPoint records AvailabilityLog

### Short Viva Explanation

Our project is an EV Charging Station Finder and Management System. It is built using MySQL, Flask, HTML, CSS, and JavaScript. The database stores users, vehicles, stations, charging points, connector types, charger types, sessions, reviews, opening hours, and availability logs. The user can log in, find nearby stations on a map, filter stations based on compatible connectors, view station details, calculate charging cost and time, book or start charging sessions, end sessions, view history, and submit reviews. We also added peak-hour analytics using Chart.js and wait-time prediction using a Random Forest machine learning model. The project demonstrates DBMS concepts like primary keys, foreign keys, many-to-many relationships, joins, aggregation, and transaction management.
