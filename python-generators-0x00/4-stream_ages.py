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

def stream_user_ages():
    """
    Generator function that yields user ages one by one from the user_data table.
    """
    connection = None
    try:
        connection = connect_to_prodev()
        if not connection:
            return

        cursor = connection.cursor()
        query = "SELECT age FROM user_data"
        cursor.execute(query)

        row = cursor.fetchone()
        while row:
            yield float(row[0])
            row = cursor.fetchone()

    except mysql.connector.Error as err:
        print(f"Error streaming ages: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if connection:
            connection.close()

def calculate_average_age():
    """
    Calculates the average age of users without loading the entire dataset into memory.
    Uses the stream_user_ages generator.
    Constraint: No more than two loops in the script.
    """
    total_age = 0
    count = 0
    
    for age in stream_user_ages():
        total_age += age
        count += 1

    if count == 0:
        return 0
    return total_age / count

if __name__ == "__main__":
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age}")