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
