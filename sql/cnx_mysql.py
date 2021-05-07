import mysql.connector
from mysql.connector import errorcode
import pymysql


# Obtain connection string information from the portal
db_config = {
    'host': 'psd-wordfinder.mysql.database.azure.com',
    'database': 'psd_project',
    'user': 'adminteam@psd-wordfinder',
    'password': 'jFq&T7bPJXmY',
    #'client_flags': [mysql.connector.ClientFlag.SSL],
    #'ssl_ca': './/src//train//DigiCertGlobalRootG2.crt.pem' #vscode
    'ssl_ca': 'DigiCertGlobalRootG2.crt.pem' #pycharm
}

# Construct connection string
try:
    #conn = mysql.connector.connect(**db_config)
    conn = pymysql.connect(**db_config)
    if conn:
        print("\n Database psd_project was located. \n \n List of tables in psd_project \n")
        with conn.cursor() as cursor:

            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'psd_project'")

            print(cursor.fetchall())


except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with the user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
