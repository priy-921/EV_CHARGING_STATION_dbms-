import os
import MySQLdb
DB_NAME = os.getenv('EVFINDER_DB_NAME', 'ev_charging_station')
DB_USER = os.getenv('EVFINDER_DB_USER', 'root')
DB_PASSWORD = os.getenv('EVFINDER_DB_PASSWORD', 'Madhura@27')


def get_db():
    attempts = [
        {'host': 'localhost', 'unix_socket': '/private/tmp/mysql.sock'},
        {'host': 'localhost', 'unix_socket': '/tmp/mysql.sock'},
        {'host': '127.0.0.1', 'port': 3306},
        {'host': 'localhost', 'port': 3306},
    ]

    last_error = None
    for attempt in attempts:
        try:
            conn = MySQLdb.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                **attempt,
            )
            conn.cursorclass = MySQLdb.cursors.DictCursor
            return conn
        except MySQLdb.Error as err:
            last_error = err

    raise RuntimeError(
        'Could not connect to MySQL. Tried /private/tmp/mysql.sock, /tmp/mysql.sock, '
        '127.0.0.1:3306, and localhost:3306. '
        f'Last error: {last_error}'
    )


def ensure_user_station_columns():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SHOW COLUMNS FROM `User`")
    columns = {row['Field'] for row in cur.fetchall()}

    if 'admin_station_id' not in columns:
        cur.execute("ALTER TABLE `User` ADD COLUMN admin_station_id INT NULL")

    if 'selected_station_id' not in columns:
        cur.execute("ALTER TABLE `User` ADD COLUMN selected_station_id INT NULL")

    cur.execute("SHOW INDEX FROM `User` WHERE Key_name = 'ux_user_admin_station'")
    if not cur.fetchall():
        cur.execute("CREATE UNIQUE INDEX ux_user_admin_station ON `User` (admin_station_id)")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS UserData (
            user_id INT NOT NULL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            password VARCHAR(255) NOT NULL,
            last_lat DECIMAL(10,7) NULL,
            last_lng DECIMAL(10,7) NULL,
            last_location_updated DATETIME NULL,
            selected_station_id INT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY ux_user_data_email (email),
            UNIQUE KEY ux_user_data_phone (phone),
            FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE CASCADE,
            FOREIGN KEY (selected_station_id) REFERENCES ChargingStation(station_id) ON DELETE SET NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS AdminData (
            admin_user_id INT NOT NULL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            password VARCHAR(255) NOT NULL,
            admin_station_id INT NULL,
            last_lat DECIMAL(10,7) NULL,
            last_lng DECIMAL(10,7) NULL,
            last_location_updated DATETIME NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY ux_admin_data_email (email),
            UNIQUE KEY ux_admin_data_phone (phone),
            UNIQUE KEY ux_admin_data_station (admin_station_id),
            FOREIGN KEY (admin_user_id) REFERENCES `User`(user_id) ON DELETE CASCADE,
            FOREIGN KEY (admin_station_id) REFERENCES ChargingStation(station_id) ON DELETE SET NULL
        )
    """)

    cur.execute("""
        INSERT INTO UserData (
            user_id, first_name, last_name, email, phone, password,
            last_lat, last_lng, last_location_updated, selected_station_id
        )
        SELECT user_id, first_name, last_name, email, phone, password,
               last_lat, last_lng, last_location_updated, selected_station_id
        FROM `User`
        WHERE LOWER(COALESCE(role, 'user')) <> 'admin'
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
    """)

    cur.execute("""
        INSERT INTO AdminData (
            admin_user_id, first_name, last_name, email, phone, password,
            admin_station_id, last_lat, last_lng, last_location_updated
        )
        SELECT user_id, first_name, last_name, email, phone, password,
               admin_station_id, last_lat, last_lng, last_location_updated
        FROM `User`
        WHERE LOWER(COALESCE(role, '')) = 'admin'
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
    """)

    cur.execute("SHOW TABLES LIKE 'AdminStation'")
    if cur.fetchone():
        cur.execute("""
            UPDATE AdminData ad
            JOIN (
                SELECT admin_user_id, MIN(station_id) AS station_id
                FROM AdminStation
                GROUP BY admin_user_id
            ) ast ON ad.admin_user_id = ast.admin_user_id
            SET ad.admin_station_id = COALESCE(ad.admin_station_id, ast.station_id)
        """)
        cur.execute("""
            UPDATE `User` u
            JOIN AdminData ad ON u.user_id = ad.admin_user_id
            SET u.admin_station_id = COALESCE(u.admin_station_id, ad.admin_station_id)
            WHERE LOWER(COALESCE(u.role, '')) = 'admin'
        """)
        cur.execute("DROP TABLE AdminStation")

    cur.execute("SHOW INDEX FROM AdminData WHERE Key_name = 'ux_admin_data_station'")
    if not cur.fetchall():
        cur.execute("CREATE UNIQUE INDEX ux_admin_data_station ON AdminData (admin_station_id)")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS UserNotification (
            notification_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            session_id INT NULL,
            notification_type VARCHAR(50) NOT NULL,
            message VARCHAR(500) NOT NULL,
            billing_amount DECIMAL(10,2) NULL,
            is_read TINYINT(1) NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES ChargingSession(session_id) ON DELETE SET NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
