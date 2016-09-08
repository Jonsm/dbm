import sys

import dbm.db


def main():
    table = sys.argv[1]
    id = sys.argv[2]
    cnx = dbm.db.open_readonly_connection()
    cursor = cnx.cursor()
    dict = dbm.db.get_row(cursor, table, id)
    output = ""
    for i, key in enumerate(dict):
        output = output + key + ", " + str(dict[key]) + "\n"
    print(output)
    cursor.close()
    cnx.close()

main()
