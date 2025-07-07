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
    (Duplicated from seed.py for self-containment)
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

def paginate_users(page_size, offset):
    """
    Fetches a single page of users from the user_data table.
    This function is provided by the exercise.
    """
    connection = connect_to_prodev()
    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT user_id, name, email, age FROM user_data LIMIT {page_size} OFFSET {offset}")
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error fetching page: {err}")
        return []
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if connection:
            connection.close()

def lazy_pagination(page_size):
    """
    Implements a generator function that fetches data page by page from user_data table
    using paginate_users, only fetching the next page when needed.
    Starts at offset 0.
    Constraint: Only one loop.
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size