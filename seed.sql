-- seed.sql — INSERT only, no CREATE TABLE
-- Run after tables are already created in ev_charging_station database
USE ev_charging_station;

-- ============================================================
-- 1. User (user_id 1-20)
-- ============================================================
INSERT INTO `User` (user_id, first_name, last_name, email, phone, password, role, last_lat, last_lng, last_location_updated) VALUES
(1,  'Aarav',    'Sharma',   'aarav.sharma@gmail.com',    '9876543210', 'pass1234', 'user', 18.5204, 73.8567, '2026-04-15 10:30:00'),
(2,  'Priya',    'Patil',    'priya.patil@gmail.com',     '9876543211', 'pass1234', 'user', 18.5314, 73.8446, '2026-04-15 11:00:00'),
(3,  'Rohan',    'Deshmukh', 'rohan.desh@gmail.com',      '9876543212', 'pass1234', 'user', 18.5074, 73.8077, '2026-04-14 09:15:00'),
(4,  'Sneha',    'Kulkarni', 'sneha.kulk@gmail.com',      '9876543213', 'pass1234', 'user', 18.5590, 73.7868, '2026-04-14 14:20:00'),
(5,  'Vikram',   'Jadhav',   'vikram.j@gmail.com',        '9876543214', 'pass1234', 'user', 18.4630, 73.8680, '2026-04-13 16:45:00'),
(6,  'Anjali',   'More',     'anjali.more@gmail.com',     '9876543215', 'pass1234', 'user', 18.5362, 73.8978, '2026-04-13 08:30:00'),
(7,  'Rahul',    'Gaikwad',  'rahul.gaik@gmail.com',      '9876543216', 'pass1234', 'user', 18.4880, 73.8130, '2026-04-12 12:00:00'),
(8,  'Meera',    'Joshi',    'meera.joshi@gmail.com',     '9876543217', 'pass1234', 'user', 18.5720, 73.9170, '2026-04-12 17:30:00'),
(9,  'Arjun',    'Bhosale',  'arjun.bhos@gmail.com',      '9876543218', 'pass1234', 'user', 18.5100, 73.8300, '2026-04-11 10:00:00'),
(10, 'Kavya',    'Pawar',    'kavya.pawar@gmail.com',     '9876543219', 'pass1234', 'user', 18.5450, 73.8780, '2026-04-11 13:15:00'),
(11, 'Siddharth','Wagh',     'sid.wagh@gmail.com',        '9876543220', 'pass1234', 'user', 18.5280, 73.8500, '2026-04-10 09:45:00'),
(12, 'Diya',     'Chavan',   'diya.chavan@gmail.com',     '9876543221', 'pass1234', 'user', 18.4950, 73.8670, '2026-04-10 15:00:00'),
(13, 'Aditya',   'Shinde',   'aditya.shin@gmail.com',     '9876543222', 'pass1234', 'user', 18.5600, 73.9050, '2026-04-09 11:30:00'),
(14, 'Pooja',    'Mane',     'pooja.mane@gmail.com',      '9876543223', 'pass1234', 'user', 18.4700, 73.8560, '2026-04-09 08:00:00'),
(15, 'Kunal',    'Deshpande','kunal.deshp@gmail.com',     '9876543224', 'pass1234', 'user', 18.5380, 73.8290, '2026-04-08 14:45:00'),
(16, 'Isha',     'Sawant',   'isha.sawant@gmail.com',     '9876543225', 'pass1234', 'user', 18.5050, 73.8780, '2026-04-08 10:20:00'),
(17, 'Om',       'Thakur',   'om.thakur@gmail.com',       '9876543226', 'pass1234', 'user', 18.5510, 73.8350, '2026-04-07 16:00:00'),
(18, 'Tanvi',    'Rajput',   'tanvi.rajp@gmail.com',      '9876543227', 'pass1234', 'user', 18.4830, 73.8900, '2026-04-07 12:30:00'),
(19, 'Yash',     'Nikam',    'yash.nikam@gmail.com',      '9876543228', 'pass1234', 'user', 18.5670, 73.8120, '2026-04-06 09:00:00'),
(20, 'Nisha',    'Kale',     'nisha.kale@gmail.com',      '9876543229', 'pass1234', 'user', 18.5140, 73.8640, '2026-04-06 11:45:00');

-- ============================================================
-- 2. Vehicle (vehicle_id 1-10)
-- ============================================================
INSERT INTO `Vehicle` (vehicle_id, user_id, model, brand, battery_capacity, max_ac_kw, max_dc_kw, segment) VALUES
(1,  1,  'Nexon EV',    'Tata',     40.5,  7.2,  50,   '4W'),
(2,  2,  'ZS EV',       'MG',       50.3,  7.4,  76,   '4W'),
(3,  3,  'Kona Electric','Hyundai', 39.2,  7.2,  50,   '4W'),
(4,  4,  'S1 Pro',      'Ola',      3.97,  0.9,  NULL, '2W'),
(5,  5,  '450X',        'Ather',    2.9,   0.85, NULL, '2W'),
(6,  6,  'iQube',       'TVS',      4.56,  0.9,  NULL, '2W'),
(7,  7,  'Tigor EV',    'Tata',     26.0,  3.3,  NULL, '4W'),
(8,  8,  'XUV400',      'Mahindra', 39.4,  7.2,  50,   '4W'),
(9,  9,  'EV6',         'Kia',      77.4,  11.0, 233,  '4W'),
(10, 10, 'Atto 3',      'BYD',      60.48, 11.0, 80,   '4W');

-- ============================================================
-- 3. VehicleConnector — map vehicles to connector types
-- connector_type_id: 1=J1772, 2=Mennekes, 3=Bharat AC-001, 4=CCS2, 5=CHAdeMO
-- ============================================================
INSERT INTO `VehicleConnector` (vehicle_id, connector_type_id) VALUES
(1, 2), (1, 4),
(2, 2), (2, 4),
(3, 2), (3, 4),
(4, 3),
(5, 3),
(6, 3),
(7, 2), (7, 3),
(8, 2), (8, 4),
(9, 2), (9, 4),
(10, 2), (10, 4);

-- ============================================================
-- 4. OpeningHours — all 10 stations, 7 days each
-- ============================================================
INSERT INTO `OpeningHours` (station_id, day_of_week, open_time, close_time) VALUES
(1,'Monday','08:00:00','22:00:00'),(1,'Tuesday','08:00:00','22:00:00'),(1,'Wednesday','08:00:00','22:00:00'),(1,'Thursday','08:00:00','22:00:00'),(1,'Friday','08:00:00','22:00:00'),(1,'Saturday','08:00:00','22:00:00'),(1,'Sunday','08:00:00','22:00:00'),
(2,'Monday','08:00:00','22:00:00'),(2,'Tuesday','08:00:00','22:00:00'),(2,'Wednesday','08:00:00','22:00:00'),(2,'Thursday','08:00:00','22:00:00'),(2,'Friday','08:00:00','22:00:00'),(2,'Saturday','08:00:00','22:00:00'),(2,'Sunday','08:00:00','22:00:00'),
(3,'Monday','08:00:00','22:00:00'),(3,'Tuesday','08:00:00','22:00:00'),(3,'Wednesday','08:00:00','22:00:00'),(3,'Thursday','08:00:00','22:00:00'),(3,'Friday','08:00:00','22:00:00'),(3,'Saturday','08:00:00','22:00:00'),(3,'Sunday','08:00:00','22:00:00'),
(4,'Monday','08:00:00','22:00:00'),(4,'Tuesday','08:00:00','22:00:00'),(4,'Wednesday','08:00:00','22:00:00'),(4,'Thursday','08:00:00','22:00:00'),(4,'Friday','08:00:00','22:00:00'),(4,'Saturday','08:00:00','22:00:00'),(4,'Sunday','08:00:00','22:00:00'),
(5,'Monday','08:00:00','22:00:00'),(5,'Tuesday','08:00:00','22:00:00'),(5,'Wednesday','08:00:00','22:00:00'),(5,'Thursday','08:00:00','22:00:00'),(5,'Friday','08:00:00','22:00:00'),(5,'Saturday','08:00:00','22:00:00'),(5,'Sunday','08:00:00','22:00:00'),
(6,'Monday','08:00:00','22:00:00'),(6,'Tuesday','08:00:00','22:00:00'),(6,'Wednesday','08:00:00','22:00:00'),(6,'Thursday','08:00:00','22:00:00'),(6,'Friday','08:00:00','22:00:00'),(6,'Saturday','08:00:00','22:00:00'),(6,'Sunday','08:00:00','22:00:00'),
(7,'Monday','08:00:00','22:00:00'),(7,'Tuesday','08:00:00','22:00:00'),(7,'Wednesday','08:00:00','22:00:00'),(7,'Thursday','08:00:00','22:00:00'),(7,'Friday','08:00:00','22:00:00'),(7,'Saturday','08:00:00','22:00:00'),(7,'Sunday','08:00:00','22:00:00'),
(8,'Monday','08:00:00','22:00:00'),(8,'Tuesday','08:00:00','22:00:00'),(8,'Wednesday','08:00:00','22:00:00'),(8,'Thursday','08:00:00','22:00:00'),(8,'Friday','08:00:00','22:00:00'),(8,'Saturday','08:00:00','22:00:00'),(8,'Sunday','08:00:00','22:00:00'),
(9,'Monday','08:00:00','22:00:00'),(9,'Tuesday','08:00:00','22:00:00'),(9,'Wednesday','08:00:00','22:00:00'),(9,'Thursday','08:00:00','22:00:00'),(9,'Friday','08:00:00','22:00:00'),(9,'Saturday','08:00:00','22:00:00'),(9,'Sunday','08:00:00','22:00:00'),
(10,'Monday','08:00:00','22:00:00'),(10,'Tuesday','08:00:00','22:00:00'),(10,'Wednesday','08:00:00','22:00:00'),(10,'Thursday','08:00:00','22:00:00'),(10,'Friday','08:00:00','22:00:00'),(10,'Saturday','08:00:00','22:00:00'),(10,'Sunday','08:00:00','22:00:00');

-- ============================================================
-- 5. ChargingSession (300 rows)
-- Spread across Jan-Apr 2026, peak hours 8-10am and 6-9pm
-- ============================================================
DELIMITER //
DROP PROCEDURE IF EXISTS seed_sessions//
CREATE PROCEDURE seed_sessions()
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE v_cp_id INT;
    DECLARE v_user_id INT;
    DECLARE v_energy DECIMAL(10,2);
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_start DATETIME;
    DECLARE v_end DATETIME;
    DECLARE v_hour INT;
    DECLARE v_day_offset INT;
    DECLARE v_duration INT;

    WHILE i < 300 DO
        SET v_cp_id = FLOOR(1 + RAND() * 28);
        SET v_user_id = FLOOR(1 + RAND() * 20);
        SET v_day_offset = FLOOR(RAND() * 90);

        -- Bias towards peak hours: 60% peak, 40% off-peak
        IF RAND() < 0.6 THEN
            IF RAND() < 0.5 THEN
                SET v_hour = FLOOR(8 + RAND() * 2);   -- 8-9 AM
            ELSE
                SET v_hour = FLOOR(18 + RAND() * 3);  -- 6-8 PM
            END IF;
        ELSE
            SET v_hour = FLOOR(8 + RAND() * 14);       -- 8 AM - 9 PM
        END IF;

        SET v_start = DATE_SUB(NOW(), INTERVAL v_day_offset DAY)
                      + INTERVAL v_hour HOUR
                      + INTERVAL FLOOR(RAND() * 60) MINUTE;
        SET v_energy = ROUND(5 + RAND() * 55, 2);
        SET v_duration = FLOOR(15 + RAND() * 120);
        SET v_end = v_start + INTERVAL v_duration MINUTE;

        SELECT price INTO v_price FROM ChargingPoint WHERE charging_point_id = v_cp_id LIMIT 1;
        IF v_price IS NULL THEN SET v_price = 12.00; END IF;

        INSERT INTO `ChargingSession` (charging_point_id, user_id, start_time, end_time, energy_consumed, total_cost)
        VALUES (v_cp_id, v_user_id, v_start, v_end, v_energy, ROUND(v_energy * v_price, 2));

        SET i = i + 1;
    END WHILE;
END//
DELIMITER ;
CALL seed_sessions();
DROP PROCEDURE IF EXISTS seed_sessions;

-- ============================================================
-- 6. Review (100 rows)
-- ============================================================
INSERT INTO `Review` (user_id, station_id, rating, review_text, review_date) VALUES
(1,1,5,'Excellent charging station! Very clean and well-maintained. The staff was very helpful.','2026-02-01 10:30:00'),
(2,1,4,'Good experience overall. Fast charging speed but parking space is a bit tight.','2026-02-03 14:20:00'),
(3,2,5,'Best charger in Pune! Super fast CCS2 charger, my Kona was full in 45 mins.','2026-02-05 09:15:00'),
(4,2,3,'Average experience. Had to wait 20 mins for a slot. They should add more chargers.','2026-02-07 16:45:00'),
(5,3,4,'Reliable station near Hinjewadi. Convenient for IT park employees.','2026-02-09 11:00:00'),
(6,3,5,'Love this station! Always available when I need it. Great location.','2026-02-11 08:30:00'),
(7,4,2,'Charger was not working when I visited. Waste of time driving there.','2026-02-13 13:00:00'),
(8,4,4,'Good station with multiple charger types. Waited only 5 minutes.','2026-02-15 17:30:00'),
(9,5,5,'Fastest charger I have used in Pune. My EV6 charged to 80% in 30 mins!','2026-02-17 10:00:00'),
(10,5,4,'Nice and clean. Good coffee shop nearby to wait. Highly recommend.','2026-02-19 15:15:00'),
(11,6,3,'Decent station but the app showed wrong availability. Please fix.','2026-02-21 09:45:00'),
(12,6,4,'Smooth experience. Price is reasonable compared to other stations.','2026-02-23 14:00:00'),
(13,7,5,'Superb! No waiting time at all. Charged my Nexon EV fully.','2026-02-25 11:30:00'),
(14,7,3,'Station is good but road leading to it has too many potholes.','2026-02-27 08:00:00'),
(15,8,4,'Great location in Kothrud. Easy to find. Clean facilities.','2026-03-01 16:30:00'),
(16,8,5,'My go-to charging station! Never had a bad experience here.','2026-03-03 10:20:00'),
(17,9,2,'Very slow charging speed. Took 3 hours for my Tigor EV.','2026-03-05 12:00:00'),
(18,9,4,'Good station. The guard helped me connect the charger. Nice people.','2026-03-07 14:45:00'),
(19,10,5,'Top notch station! Modern setup with real-time status display.','2026-03-09 09:00:00'),
(20,10,4,'Reliable and fast. Wish they had a waiting lounge though.','2026-03-11 11:45:00'),
(1,2,4,'Second visit here. Consistent quality and fast charging.','2026-03-13 10:30:00'),
(2,3,3,'Had some trouble with the connector. Staff helped eventually.','2026-03-15 13:20:00'),
(3,4,5,'Much improved since my last visit! New chargers installed.','2026-03-17 09:00:00'),
(4,5,4,'Good station. Slightly expensive but worth it for the speed.','2026-03-19 15:30:00'),
(5,6,5,'Fantastic experience! Charged my Ather in just 30 minutes.','2026-03-21 08:45:00'),
(6,7,3,'Average. The payment terminal was not working, had to pay UPI.','2026-03-23 14:15:00'),
(7,8,4,'Reliable as always. My ZS EV charges well on their CCS2.','2026-03-25 11:00:00'),
(8,9,5,'Great station near market. Very convenient for quick top-ups.','2026-03-27 16:00:00'),
(9,10,4,'Clean and well-lit station. Feels safe to charge at night.','2026-03-29 20:30:00'),
(10,1,3,'Long queue today. Usually its better. Still decent though.','2026-03-31 10:00:00'),
(11,2,5,'Absolutely love this station! Fast, clean, and affordable.','2026-04-01 09:30:00'),
(12,3,4,'Good charger but the location is a bit hard to find.','2026-04-02 13:45:00'),
(13,4,4,'Nice ambiance. They have added a small cafe now!','2026-04-03 11:20:00'),
(14,5,5,'Premium quality station. Worth every rupee!','2026-04-04 08:15:00'),
(15,6,3,'Okay experience. One charger out of service.','2026-04-05 15:00:00'),
(16,7,4,'Good station for daily commuters. Affordable pricing.','2026-04-06 10:30:00'),
(17,8,5,'Best station in Kothrud area! Highly recommend.','2026-04-07 12:45:00'),
(18,9,3,'Mediocre. Slow charging and no shade for the car.','2026-04-08 14:00:00'),
(19,10,4,'Very good station. Modern infrastructure and helpful staff.','2026-04-09 09:45:00'),
(20,1,5,'Perfect station! Quick charge and friendly attendant.','2026-04-10 11:15:00'),
(1,3,4,'Consistent quality. My Nexon EV always charges well here.','2026-04-11 10:00:00'),
(2,5,3,'Bit crowded during evening peak hours. Come early!','2026-04-11 18:30:00'),
(3,7,5,'Excellent! The new DC fast charger is amazing.','2026-04-12 09:00:00'),
(4,9,4,'Good station. Easy to navigate from the main road.','2026-04-12 14:30:00'),
(5,1,4,'Reliable station. Have been coming here for 6 months.','2026-04-13 11:00:00'),
(6,2,5,'Love the new LED display showing charger status!','2026-04-13 16:00:00'),
(7,4,3,'Had to wait today. Weekend rush. Plan accordingly.','2026-04-14 10:45:00'),
(8,6,4,'Clean restrooms available. Good for long waits.','2026-04-14 13:30:00'),
(9,8,5,'My favorite station in Pune! Never disappoints.','2026-04-15 08:30:00'),
(10,10,4,'Great station. Just needs more parking space.','2026-04-15 15:15:00'),
(11,1,4,'Smooth charging session. Done in under an hour.','2026-02-02 10:00:00'),
(12,2,5,'Very modern setup. Multiple connector options available.','2026-02-04 14:30:00'),
(13,3,3,'Station was working but the display was broken.','2026-02-06 09:00:00'),
(14,4,4,'Nice maintenance. Chargers are always clean.','2026-02-08 16:00:00'),
(15,5,5,'Record speed! 10 to 80 percent in just 25 minutes.','2026-02-10 11:30:00'),
(16,6,4,'Good value for money. Reasonable per kWh pricing.','2026-02-12 08:00:00'),
(17,7,3,'Nothing special but gets the job done.','2026-02-14 13:45:00'),
(18,8,5,'Top quality station. They keep upgrading their equipment.','2026-02-16 10:20:00'),
(19,9,4,'Decent station. Not the fastest but reliable.','2026-02-18 15:00:00'),
(20,10,4,'Good experience. Quick and hassle-free.','2026-02-20 12:00:00'),
(1,4,5,'Great improvement! CCS2 now works perfectly.','2026-02-22 09:30:00'),
(2,6,3,'Average station. Could use better signage.','2026-02-24 14:15:00'),
(3,8,4,'Convenient location and fast service.','2026-02-26 11:00:00'),
(4,10,5,'Excellent! Their customer support is very responsive.','2026-02-28 16:45:00'),
(5,2,4,'Good charger speed. My Ather was full quickly.','2026-03-02 08:30:00'),
(6,4,4,'Nice and shaded parking area. Very comfortable wait.','2026-03-04 13:00:00'),
(7,6,5,'Best Bharat AC charger I have used! Perfect for 2-wheelers.','2026-03-06 10:30:00'),
(8,8,3,'A bit expensive. Other stations charge less per kWh.','2026-03-08 15:30:00'),
(9,1,4,'Reliable charging. No issues whatsoever.','2026-03-10 09:00:00'),
(10,3,5,'Simply superb! Clean, fast, and great location.','2026-03-12 14:00:00'),
(11,5,4,'My weekly charging spot. Happy customer!','2026-03-14 11:30:00'),
(12,7,3,'The app needs better station details. Otherwise fine.','2026-03-16 16:00:00'),
(13,9,4,'Good station. Could use a weatherproof canopy.','2026-03-18 08:45:00'),
(14,1,5,'Perfect station! Keep up the great work.','2026-03-20 13:30:00'),
(15,3,4,'Smooth experience as always. Good staff.','2026-03-22 10:00:00'),
(16,5,3,'Wait time was more than expected. But charger was fast once available.','2026-03-24 15:00:00'),
(17,7,5,'Charged my Tigor EV in record time! Very impressed.','2026-03-26 09:30:00'),
(18,10,4,'Clean and tidy. Great for a night charge.','2026-03-28 21:00:00'),
(19,2,5,'Wonderful station! They even have free WiFi now.','2026-03-30 11:00:00'),
(20,4,4,'Good infrastructure. Well maintained by the team.','2026-04-01 14:00:00'),
(1,6,3,'One charger was faulted but the other worked fine.','2026-04-02 10:30:00'),
(2,8,4,'Nice station. Reasonable price and good speed.','2026-04-03 13:00:00'),
(3,10,5,'Five stars! Nothing to complain about.','2026-04-04 09:00:00'),
(4,1,4,'Good station. Regular visitor. Very consistent.','2026-04-05 16:30:00'),
(5,3,4,'Convenient for shopping. Charge while you shop!','2026-04-06 11:15:00'),
(6,5,5,'Fastest charger in town! Absolutely love it.','2026-04-07 08:00:00'),
(7,7,3,'Okay experience. Not the best but acceptable.','2026-04-08 14:30:00'),
(8,2,4,'Second time here. Satisfied with the service.','2026-04-09 10:00:00'),
(9,4,5,'Top notch! Modern chargers and very fast.','2026-04-10 15:45:00'),
(10,6,4,'Good station. Clean surroundings and helpful guard.','2026-04-11 12:00:00'),
(11,8,3,'Average. Needs more charger slots during peak hours.','2026-04-12 09:30:00'),
(12,10,5,'Love coming here! Best station in East Pune.','2026-04-13 14:00:00'),
(13,1,4,'Smooth and quick. My Nexon EV loves this station!','2026-04-14 11:30:00'),
(14,3,4,'Reliable station. Good for routine charging.','2026-04-15 08:45:00'),
(15,5,5,'Amazing speed and reasonable cost. Top station!','2026-04-16 13:00:00'),
(16,9,3,'Took a while to get a free slot. Decent otherwise.','2026-04-16 17:00:00'),
(17,2,4,'Good Mennekes charger. Perfect for my ZS EV.','2026-04-17 10:00:00'),
(18,4,5,'Fantastic new upgrades! Much better than before.','2026-04-17 15:30:00'),
(19,6,4,'Clean and well-maintained. Would recommend.','2026-04-18 09:15:00'),
(20,8,4,'Great station in a convenient location. No complaints!','2026-04-18 14:00:00');

-- ============================================================
-- 7. AvailabilityLog (500 rows)
-- ============================================================
DELIMITER //
DROP PROCEDURE IF EXISTS seed_availability//
CREATE PROCEDURE seed_availability()
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE v_cp_id INT;
    DECLARE v_status VARCHAR(20);
    DECLARE v_logged DATETIME;
    DECLARE v_rand DOUBLE;

    WHILE i < 500 DO
        SET v_cp_id = FLOOR(1 + RAND() * 28);
        SET v_rand = RAND();

        IF v_rand < 0.5 THEN
            SET v_status = 'Available';
        ELSEIF v_rand < 0.85 THEN
            SET v_status = 'In Use';
        ELSE
            SET v_status = 'Out of Service';
        END IF;

        SET v_logged = DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 90) DAY)
                       + INTERVAL FLOOR(RAND() * 14 + 8) HOUR
                       + INTERVAL FLOOR(RAND() * 60) MINUTE;

        INSERT INTO `AvailabilityLog` (charging_point_id, status, logged_at)
        VALUES (v_cp_id, v_status, v_logged);

        SET i = i + 1;
    END WHILE;
END//
DELIMITER ;
CALL seed_availability();
DROP PROCEDURE IF EXISTS seed_availability;
