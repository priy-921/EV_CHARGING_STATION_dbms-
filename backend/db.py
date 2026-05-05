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

    conn.commit()
    cur.close()
    conn.close()
