import datetime
import re
import sys

import mysql.connector

import dbm.config


#opens connection that can only use SELECT
def open_readonly_connection():
    return open_db_connection(dbm.config.read_only_config)

#opens connection with root privileges
def open_admin_connection():
    return open_db_connection(dbm.config.adminconfig)

#creates connection to database, returns database object
def open_db_connection(credentials):
    try:
        cnx = mysql.connector.connect(**credentials)
    except mysql.connector.Error as err:
        sys.exit("Couldn't connect to database.")
    return cnx

#tries to add a new measurement. Will throw an exception if new measurement type/parameter is added. Returns ID.
def insert_into_db(cursor, dict):
    type = dict["type"]
    command = "INSERT INTO " + type + " "
    columns = "("
    values = "VALUES ("
    for i, key in enumerate(dict):
        columns = columns + validate(key) + ", "
        values = values + repr(validate(dict[key])) + ", "
    columns = columns + "date) "
    values = values + "\'" + datetime.datetime.now().isoformat() + "\');"
    query = command + columns + values
    cursor.execute(query)

#gets a row as dictionary or throws exception if id or table does not exist
def get_row(cursor, table, id):
    query = "SELECT * FROM " + validate(table) + " WHERE id=" + validate(id) + ";"
    cursor.execute(query)
    columns = cursor.column_names
    dict = {}
    for row in cursor:
        for i, val in enumerate(row):
            dict[columns[i]] = val
    return dict

#prints mysql styled format (from dotancohen on stackoverflow)
def pretty_print(cursor):
    results = cursor.fetchall()

    widths = []
    columns = []
    tavnit = '|'
    separator = '+'

    for i, cd in enumerate(cursor.description):
        longest_result = 0
        for result in results:
            strlength = len(str(result[i]))
            if strlength > longest_result:
                longest_result = strlength
        widths.append(max(longest_result, len(cd[0])))
        columns.append(cd[0])

    for w in widths:
        tavnit += " %-" + "%ss |" % (w,)
        separator += '-' * w + '--+'

    print(separator)
    print(tavnit % tuple(columns))
    print(separator)
    for row in results:
        print(tavnit % row)
    print(separator)

#adds new table with basic parameters
def create_table(cursor, name):
    query = "CREATE TABLE " + validate(name) + " (id int AUTO_INCREMENT, title varchar(255), " \
                                               "date datetime, type varchar(255), PRIMARY KEY (id))"
    cursor.execute(query)

#removes table from database
def drop_table(cursor, name):
    cursor.execute("DROP TABLE " + validate(name) + ";")

#add new column to a table
def add_column(cursor, table, column, default=None):
    query = "ALTER TABLE " + validate(table) + " ADD " + validate(column) + " varchar(255)"
    if (default):
        query = query + " DEFAULT " + repr(validate(default))
    query = query + ";"
    cursor.execute(query)

#gets the id of the most recently added row
def get_last_id(cursor):
    cursor.execute("SELECT LAST_INSERT_ID();")
    return cursor.lastrowid

#check if an input is valid [0-9a-z_]
def validate(input):
    search = re.search("^[0-9a-z\_]+$", input)
    if search == None:
        sys.exit("String " + input + " is invalid. Must be only lowercase, numbers, and underscore.")
    else:
        return input