+---------------------------------------------------------------------------------------------------------------+
| README                                                                                                        |
+---------------------------------------------------------------------------------------------------------------+

I. INSTALLING DBM
   1. Install Python 3.4 from https://www.python.org/download/releases/3.4.3/
   2. Install mysql-connector: https://dev.mysql.com/doc/connector-python/en/connector-python-installation.html
   3. Install the dbm python library by typing (in this directory): python setup.py install
   4. Create an alias by copying dbm.bat to Windows/system32. You might need to change the second line to reflect
   the location of your /util/main.py file.

II. REGISTERING PARAMETERS
   To register parameters in the database, create a json file with the parameters and a field called "type" with
   with the type of the measurement. See test.json in the example folder. Then use the command line tool by
   writing "dbm --register [your json file]". The command line tool can also be used to look up parameters. For
   more information use "dbm --help".

III. USING THE PYTHON API
   Import dbm.db, dbm.config, and mysql.connector into your python code. See example.py to see how to use it.

IV. USING THE LABVIEW API
   Drag dbm.lvclass, and the get and load member VIs into your VI. See example.vi to see how to use it. You may 
   need to change the Python path input to the load VI to match your python path.

V. CLEANING UP/REMOVING DATA
   Only if you know what you are doing, download MySQL command line client, and connect through the admin account in
   dbm/config.py. If you delete something by accident you can't get it back!