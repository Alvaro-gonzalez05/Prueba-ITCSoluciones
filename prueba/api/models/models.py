import pymysql
import os

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_database = os.getenv('DB_NAME')

def conexion():
    try:
        connection = pymysql.connect(
            host=db_host,  
            user=db_user,
            password=db_password, 
            database=db_database,
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        return None
