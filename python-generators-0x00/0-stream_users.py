import mysql.connector
import os

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin')
DB_NAME = "ALX_prodev_database"

def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    Returns the connection object if successful, None otherwise.
    (Duplicated from seed.py for self-containment as per usual exercise setup)
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to {DB_NAME} database: {err}")
        return None

def stream_users():
    """
    Uses a generator to fetch rows one by one from the user_data table.
    Yields each user as a dictionary.
    Constraint: No more than 1 loop.
    """
    connection = None
    try:
        connection = connect_to_prodev()
        if not connection:
            return

        cursor = connection.cursor(dictionary=True, buffered=True) 
        query = "SELECT user_id, name, email, age FROM user_data"
        cursor.execute(query)
        row = cursor.fetchone()
        while row:
            yield row
            row = cursor.fetchone()

    except mysql.connector.Error as err:
        print(f"Error streaming users: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if connection:
            connection.close()