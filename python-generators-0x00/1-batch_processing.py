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

def stream_users_in_batches(batch_size):
    """
    Fetches rows from the user_data table in batches using a generator.
    Yields a list of users for each batch.
    """
    connection = None
    try:
        connection = connect_to_prodev()
        if not connection:
            return

        cursor = connection.cursor(dictionary=True)
        query = "SELECT user_id, name, email, age FROM user_data"
        cursor.execute(query)

        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch

    except mysql.connector.Error as err:
        print(f"Error streaming users in batches: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if connection:
            connection.close()

def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25.
    Prints the filtered users.
    Constraint: No more than 3 loops in total (across both functions).
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)