import mysql.connector
import csv
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = "ALX_prodev"


def connect_db():

    # Connect to the MySQL server (not a specific database)
    # Returns the connection object
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def create_database(connection):
    # To link with the ALX_prodev database later.
    #  Linking it using the connection object passed as an argument
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
    cursor.close()


def connect_to_prodev():
    
    # Connect to the ALX_prodev database
    # Returns the connection object
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to {DB_NAME}: {e}")
        return None


def create_table(connection):
    """
    Create the user_data table if it does not exist
    Fields:
        user_id: PRIMARY KEY, UUID, Indexed
        name: VARCHAR NOT NULL
        email: VARCHAR NOT NULL
        age: DECIMAL NOT NULL
    """
    cursor = connection.cursor()
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL(5,2) NOT NULL,
        INDEX idx_user_id (user_id)
    );
    """
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()
    print("Table user_data created successfully")


def insert_data(connection, csv_file):
    """
    Insert data from CSV file into user_data table if it does not exist
    CSV format: user_id,name,email,age
    """
    cursor = connection.cursor()

    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if user_id already exists
            cursor.execute("SELECT user_id FROM user_data WHERE user_id=%s", (row['user_id'],))
            if cursor.fetchone():
                continue  # Skip if already exists

            # Insert new row
            cursor.execute(
                "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                (row['user_id'], row['name'], row['email'], row['age'])
            )

    connection.commit()
    cursor.close()
    print("Data inserted successfully")


# Optional: Test run
if __name__ == "__main__":
    conn = connect_db()
    if conn:
        create_database(conn)
        conn.close()

    conn = connect_to_prodev()
    if conn:
        create_table(conn)
        insert_data(conn, "user_data.csv")
        conn.close()
