# Second task-batch_users.py

import mysql.connector
import os
from dotenv import load_dotenv
from itertools import islice

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def stream_users_in_batches(batch_size):
    
    # Generator function to fetch rows from user_data table in batches.
    # Yields a list of dictionaries, each batch containing at most batch_size rows.
    
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data;")

    while True:
        batch = list(islice(cursor, batch_size))  # Fetch up to batch_size rows
        if not batch:
            break
        yield batch  # Yield the batch as a list

    cursor.close()
    connection.close()


def batch_processing(batch_size):
    
    # Processes each batch from the generator to filter users over the age of 25.
    # Yields each user one by one (lazy evaluation).
    
    for batch in stream_users_in_batches(batch_size):  # Loop 1
        for user in batch:  # Loop 2
            if user['age'] > 25:  # Loop 3 is implicit in filtering
                yield user  # Yield one user at a time


# Optional test
if __name__ == "__main__":
    for user in batch_processing(3):
        print(user)
