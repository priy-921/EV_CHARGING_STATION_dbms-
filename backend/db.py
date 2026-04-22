import MySQLdb

def get_db():
    conn = MySQLdb.connect(
        host='localhost',
        user='root',
        password='priyanka123',
        database='ev_charging_station'
    )
    conn.cursorclass = MySQLdb.cursors.DictCursor
    return conn