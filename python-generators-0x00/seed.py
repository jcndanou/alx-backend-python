import mysql.connector
import csv
import uuid
import os

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin')
DB_NAME = "ALX_prodev_database"

def connect_db():
    """
    Connects to the MySQL database server.
    Returns the connection object if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Connected to MySQL server.")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
        return None

def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database {DB_NAME} created successfully or already exists.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
    finally:
        cursor.close()

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
        print(f"Connected to database {DB_NAME}.")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to {DB_NAME} database: {err}")
        return None

def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields.
    user_id (Primary Key, UUID, Indexed)
    name (VARCHAR, NOT NULL)
    email (VARCHAR, NOT NULL)
    age (DECIMAL, NOT NULL)
    """
    cursor = connection.cursor()
    table_name = "user_data"
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        user_id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL(5, 2) NOT NULL,
        INDEX(email) -- Email index for quick lookups
    );
    """
    try:
        cursor.execute(create_table_query)
        print(f"Table {table_name} created successfully or already exists.")
    except mysql.connector.Error as err:
        print(f"Failed creating table {table_name}: {err}")
    finally:
        cursor.close()

def insert_data(connection, csv_file_path):
    """     
    Inserts data from a CSV file into the user_data table.
    It checks if data exists before inserting to avoid duplicates based on user_id.
    """
    cursor = connection.cursor()
    insert_query = """
    INSERT INTO user_data (user_id, name, email, age)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        email = VALUES(email),
        age = VALUES(age);
    """
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for i, row in enumerate(csv_reader):
                user_id = row['user_id'] if 'user_id' in row and row['user_id'] else str(uuid.uuid4())
                name = row['name']
                email = row['email']
                age = float(row['age'])

                data_tuple = (user_id, name, email, age)
                try:
                    cursor.execute(insert_query, data_tuple)
                    if (i + 1) % 100 == 0:
                        print(f"Inserted/Updated {i + 1} rows...")
                except mysql.connector.Error as err_insert:
                    print(f"Error inserting row {row}: {err_insert}")
                    connection.rollback()
                    break
        connection.commit()
        print("Data insertion complete.")
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
    except mysql.connector.Error as err:
        print(f"Failed inserting data: {err}")
    finally:
        cursor.close()
