import mysql.connector
import dbm.db
import dbm.config

cnx = dbm.db.open_readonly_connection()
cursor = cnx.cursor()
dict = dbm.db.get_row(cursor, "test_measurement", "1")
print(dict)