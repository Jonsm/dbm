import json
import re
import sys

import dbm.config
import dbm.db
import mysql.connector

# Parser
def main ():
    if len(sys.argv) == 1:
        sys.exit("Arguments needed. Use --help.")
    else:
        if (sys.argv[1] == "--help"):
            help()
        elif (sys.argv[1] == "--register"):
            if len(sys.argv) != 3:
                sys.exit("Usage: dbm --register [json file]")
            register(sys.argv[2])
        elif (sys.argv[1] == "--get"):
            if len(sys.argv) != 4:
                sys.exit("Usage: dbm --get [measurement type] [id]")
            get(sys.argv[2], sys.argv[3])
        elif (sys.argv[1] == "--eval"):
            if len(sys.argv) == 2:
                sys.exit("Usage: dbm --eval [SQL Query]")
            query = ""
            for arg in sys.argv[2:len(sys.argv)]:
                query = query + arg + " "
            eval(query)
        else:
            print("Unknown command. Use --help")


#Puts a json file into the database, creates a unique ID and prints it out
def register (filename):
    jsonfile = open(filename)
    dict = json.loads(jsonfile.read())
    jsonfile.close()
    if not dict['type']:
        sys.exit("Must provide 'type' field specifying type of measurement.")

    cnx = dbm.db.open_admin_connection()
    cursor = cnx.cursor(buffered=True)
    id = None
    new_table_added = False

    while True:
        try:
            dbm.db.insert_into_db(cursor, dict)
            id = dbm.db.get_last_id(cursor)
            break
        except mysql.connector.errors.ProgrammingError as err:
            if err.errno == 1146: #couldn't find table
                matches = re.match("Table \'" + dbm.config.dbname + "\.([^\']*)\' doesn\'t exist", err.msg)
                tablename = matches.group(1)
                if (yes_no("Measurement \'" + tablename + "\' does not exist. Create new measurement?")):
                    dbm.db.create_table(cursor, tablename)
                    new_table_added = True
                else:
                    sys.exit("Changes not committed.")
            elif err.errno == 1054: #couldn't find parameter
                matches = re.match("Unknown column \'([^\']*)\' in \'field list\'", err.msg)
                colname = matches.group(1)
                if (yes_no("Parameter \'" + colname + "\' does not exist. Create new parameter?")):
                    print("Default value for " + colname + "? (Usually value in previous measurements.) Leave blank for NULL.")
                    default = input()
                    if default == "":
                        default = None
                    dbm.db.add_column(cursor, dict["type"], colname, default=default)
                else:
                    if new_table_added:
                        dbm.db.drop_table(cursor, dict["type"])
                    sys.exit("Changes not committed.")
            else:
                sys.exit("Bad database query: " + err.msg)

    cnx.commit()
    cursor.close()
    cnx.close()
    print("Parameters registered with id: " + str(id))

#gets a row with that ID and prints as json
def get(table, id):
    cnx = dbm.db.open_admin_connection()
    cursor = cnx.cursor(buffered=True)
    try:
        dict = dbm.db.get_row(cursor, table, id)
        if not dict:
            sys.exit("Invalid id: " + id)
        dict['id'] = repr(dict['id'])
        dict['date'] = dict['date'].isoformat()
        print(json.dumps(dict, sort_keys=True, indent=4, separators={': ', ','}))
        cursor.close()
        cnx.close()
    except mysql.connector.errors.ProgrammingError as err:
        sys.exit(err.msg)

#evaluates read only SQL query
def eval(query):
    cnx = dbm.db.open_readonly_connection()
    cursor = cnx.cursor(buffered=True)
    try:
        cursor.execute(query)
        dbm.db.pretty_print(cursor)
        cursor.close()
        cnx.close()
    except mysql.connector.errors.ProgrammingError as err:
        sys.exit(err.msg)

#help duhh
def help():
    helpfile = open("help.txt")
    print(helpfile.read())
    helpfile.close()

#asks yes or no question
def yes_no (question):
    print(question)
    print("(y/n)")
    response = ""
    while response != "y" and response != "n":
        response = input()
    return response == "y"

main()