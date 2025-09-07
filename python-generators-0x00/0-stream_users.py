# 0-stream_users.py

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def stream_users():
    # Generator function that yields rows from user_data table one by one.
    # Uses only one loop and yield.
    
    # Connect to the database
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    # Use dictionary cursor for easier access
    cursor = connection.cursor(dictionary=True)

    # Execute the query
    cursor.execute("SELECT * FROM user_data;")

    # Yield rows one by one
    for row in cursor:  # only one loop
        yield row

    # Clean up resources
    cursor.close()
    connection.close()


# Optional: test the generator
if __name__ == "__main__":
    for user in stream_users():
        print(user)

# Main Point to keep in mind:
# - The function stream_users is a generator that connects to the database,
#   executes a query to fetch all rows from the user_data table, and yields each row
#   one by one using a single loop and yield statement.
# a generator is a function that returns an iterator that produces a sequence of values using the yield statement.
# - The connection and cursor are properly closed after the iteration is complete.
