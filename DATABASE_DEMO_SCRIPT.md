# EV Charging Station Database Demo Script

## 1. Intro Script

Good morning ma'am.

Our project is an **EV Charging Station Management System**.  
This database is designed to manage the complete workflow of electric vehicle charging, starting from users and their vehicles, to charging stations, charging points, charging sessions, reviews, and availability tracking.

The main purpose of this database is to make it possible to:

- store EV users and their vehicles
- store charging station details and charger types
- track which connector and charger a vehicle can use
- calculate charging time and cost
- record charging sessions
- store user reviews
- track charger availability over time

So overall, this database supports both the **operational side** of the system and the **user experience side** of the system.

## 2. What This SQL File Contains

This SQL file is a MySQL dump. It contains:

- database structure using `CREATE TABLE`
- relationships using `FOREIGN KEY`
- indexing using `PRIMARY KEY`, `UNIQUE KEY`, and `KEY`
- some master data and sample records using `INSERT INTO`

At the top of the file, MySQL temporarily disables some checks like foreign key checks and unique checks.  
This is done so the database can be imported smoothly without dependency errors while tables are being created and populated.

## 3. Table-by-Table Explanation Script

### 3.1 `User`

This table stores all registered users of the system.

Important columns:

- `user_id`: unique ID of the user
- `first_name`, `last_name`: user name
- `email`: unique email
- `phone`: unique phone number
- `password`: login password
- `role`: defines whether the person is a normal user or admin

Key points to say:

- This is the main identity table.
- One user can own multiple vehicles.
- One user can create multiple charging sessions.
- One user can also give multiple reviews.

### 3.2 `Vehicle`

This table stores EV details linked to each user.

Important columns:

- `vehicle_id`: unique vehicle ID
- `user_id`: foreign key linking vehicle to user
- `model`, `brand`: vehicle information
- `battery_capacity`: total battery size in kWh
- `max_ac_kw`: maximum AC charging supported
- `max_dc_kw`: maximum DC charging supported
- `segment`: whether it is 2-wheeler or 4-wheeler

Key points to say:

- This table helps us estimate charging time.
- Vehicle charging limits are important because even if the charger is fast, the vehicle may accept only a lower rate.

### 3.3 `ConnectorType`

This is a master table for connector standards.

Examples:

- Type 1 J1772
- Type 2 Mennekes
- Bharat AC-001
- CCS2 Combo 2
- CHAdeMO

Key points to say:

- It standardizes connector names.
- It avoids repeating connector text in many places.

### 3.4 `ChargerType`

This is another master table, but for charger technology/type.

Examples:

- Type 2 AC
- CCS2 DC
- Bharat AC-001
- Bharat DC-001
- CHAdeMO DC

Key points to say:

- `ConnectorType` tells us the plug format.
- `ChargerType` tells us the charging technology category, such as AC or DC.

### 3.5 `VehicleConnector`

This is a junction table between `Vehicle` and `ConnectorType`.

Columns:

- `vehicle_id`
- `connector_type_id`

Primary key:

- composite key on both columns

Key points to say:

- One vehicle can support multiple connector types.
- One connector type can be supported by many vehicles.
- This is a many-to-many relationship.

### 3.6 `ChargingStation`

This table stores station-level location information.

Important columns:

- `station_id`
- `street`, `city`, `state`, `zip`
- `contact`
- `latitude`, `longitude`
- `name`

Key points to say:

- This table represents the physical station.
- One station can have multiple charging points.
- Latitude and longitude help in map-based search and nearest-station features.

### 3.7 `OpeningHours`

This table stores the working hours of each charging station for each day.

Important columns:

- `hours_id`
- `station_id`
- `day_of_week`
- `open_time`
- `close_time`

Key points to say:

- This helps users know whether a station is open.
- It supports day-wise availability.
- One station can have many opening-hours records, usually one for each day.

### 3.8 `ChargingPointStatus`

This is a master table for the status of a charging point.

Statuses include:

- Available
- In Use
- Out of Service
- Faulted
- Reserved

Key points to say:

- This allows the system to show real-time charger condition.
- It is used by charging points.

### 3.9 `ChargingPoint`

This is one of the most important tables in the database.

It stores each individual charging outlet or charging point inside a station.

Important columns:

- `charging_point_id`
- `station_id`
- `connector_type_id`
- `charger_type_id`
- `status_id`
- `power_rating`
- `price`

Key points to say:

- A station can have many charging points.
- Each charging point has a connector type, charger type, current status, power rating, and per-unit pricing.
- This table is central because charging sessions happen on a charging point, not directly on the station.

### 3.10 `ChargingSession`

This table stores each charging transaction or charging event.

Important columns:

- `session_id`
- `charging_point_id`
- `user_id`
- `start_time`
- `end_time`
- `energy_consumed`
- `total_cost`

Key points to say:

- This records who charged, where they charged, when they charged, how much energy was consumed, and the total cost.
- It is useful for billing, history, and analytics.
- This is a transaction table.

### 3.11 `Review`

This table stores user feedback about charging stations.

Important columns:

- `review_id`
- `user_id`
- `station_id`
- `rating`
- `review_text`
- `review_date`

Key points to say:

- This supports the customer feedback feature.
- Reviews help users select reliable charging stations.
- It also helps platform owners understand service quality.

### 3.12 `AvailabilityLog`

This table tracks the status history of charging points over time.

Important columns:

- `log_id`
- `charging_point_id`
- `status`
- `logged_at`

Key points to say:

- This stores historical availability data.
- It helps in analytics, such as identifying busy hours, downtime, or frequently faulted chargers.

## 4. Relationship Explanation Script

You can explain the relationships like this:

- One `User` can have many `Vehicle` records.
- One `User` can have many `ChargingSession` records.
- One `User` can have many `Review` records.
- One `ChargingStation` can have many `ChargingPoint` records.
- One `ChargingStation` can have many `OpeningHours` records.
- One `ChargingStation` can have many `Review` records.
- One `ChargingPoint` belongs to one station.
- One `ChargingPoint` has one connector type, one charger type, and one current status.
- One `ChargingPoint` can have many `ChargingSession` records.
- One `ChargingPoint` can have many `AvailabilityLog` records.
- `Vehicle` and `ConnectorType` are connected through `VehicleConnector`, which handles the many-to-many relationship.

## 5. Data Flow Script

If ma'am asks how the data flows in the system, you can say:

1. A user registers in the system.
2. The user adds their EV details in the `Vehicle` table.
3. The system checks supported connectors through `VehicleConnector`.
4. The user searches for a charging station.
5. Each station contains one or more charging points.
6. Each charging point has its own charger type, connector type, power, price, and status.
7. When charging starts, a new record is created in `ChargingSession`.
8. When charging ends, energy consumed and total cost are stored.
9. The user can later submit a review for the station.
10. Availability changes are recorded in `AvailabilityLog`.

## 6. Why This Design Is Good

You can present these as advantages:

- The database is normalized, so repeated data is reduced.
- Master tables like `ConnectorType`, `ChargerType`, and `ChargingPointStatus` improve consistency.
- Foreign keys maintain referential integrity.
- The design supports both current operations and future analytics.
- It can support features like nearest station, live charger status, billing, user history, and station ratings.

## 7. Important Technical Terms to Explain Simply

If asked about database concepts, say:

- `Primary Key`: uniquely identifies each row in a table
- `Foreign Key`: creates a link between two tables
- `Unique Key`: prevents duplicate values like duplicate email or phone
- `Normalization`: splitting data into related tables to avoid duplication
- `Junction Table`: a bridge table used for many-to-many relationships

## 8. Current Practical Issues To Mention Honestly

These are worth knowing before the demo:

### Schema dump vs current application code mismatch

There are some differences between the database dump file and the newer application/seed logic:

- In this dump, `User` has only basic profile fields, but the newer `seed.sql` tries to insert `last_lat`, `last_lng`, and `last_location_updated`.
- In this dump, `ChargingSession.session_id` is not marked `AUTO_INCREMENT`, but the backend inserts sessions without supplying `session_id`.
- In this dump, `Review.review_id` is also not `AUTO_INCREMENT`, but the backend inserts reviews without supplying `review_id`.
- In this dump, `OpeningHours.hours_id` is required, but the newer `seed.sql` inserts records without `hours_id`.
- In this dump, `ChargingStation.name` is present but current inserted rows are `NULL`, so station naming may be incomplete in outputs.

If asked, you can say:

The schema file shows the original database design, and the application has evolved further during development. The next improvement is to align the schema and the backend completely.

## 9. Short 2-Minute Demo Version

If you want a quick presentation:

This database is designed for an EV charging station platform.  
It stores users, their vehicles, charging stations, charging points, charging sessions, reviews, opening hours, and charger availability logs.

The core idea is that a user owns a vehicle, a vehicle supports certain connectors, and a charging station contains multiple charging points with different charger types, power ratings, and prices.

When a user starts charging, we create a charging session. When the charging ends, we store end time, energy consumed, and total cost.  
We also store station reviews and historical availability logs so the system can support user feedback and future analytics.

The database uses primary keys, foreign keys, and normalized design to keep the data structured, connected, and consistent.

## 10. Viva Questions With Answers

### Q1. Why did you create separate tables for connector type and charger type?

Because connector type and charger type are reusable master data.  
Keeping them separate avoids duplication and improves consistency.

### Q2. Why is `VehicleConnector` needed?

Because one vehicle may support multiple connectors, and one connector type may be used by many vehicles.  
So this many-to-many relationship needs a junction table.

### Q3. Why did you create `AvailabilityLog` if `ChargingPoint` already has a status?

`ChargingPoint` stores the current status, while `AvailabilityLog` stores historical status changes over time.

### Q4. Why is `ChargingPoint` different from `ChargingStation`?

A station is the full location, while a charging point is an individual charger inside that station.

### Q5. How is cost calculated?

Cost is calculated using energy consumed multiplied by the price of the charging point.

### Q6. How is charging time estimated?

Charging time is estimated using battery capacity, current battery percentage, target percentage, charger power, and the vehicle's supported AC or DC charging limit.

## 11. Suggested Closing Line

So in summary, our database is the backbone of the EV charging platform.  
It connects users, vehicles, stations, chargers, sessions, and reviews in a structured way, making the system practical for both real-time usage and future analysis.
