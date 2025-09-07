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
    
    # Generator that fetches rows from user_data in batches.
    # Yields lists of users, each list has at most batch_size rows.

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data;")

    while True:
        batch = list(islice(cursor, batch_size))
        if not batch:
            break
        yield batch

    cursor.close()
    connection.close()
    return "All batches processed"  # final return value after generator is exhausted


def batch_processing(batch_size):
    
    # Processes batches and yields users over the age of 25 one by one.
    
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                yield user
    return "Batch processing complete"  # final return after all batches


# Optional test
if __name__ == "__main__":
    # Capture the generator's return value
    gen = batch_processing(3)
    try:
        while True:
            user = next(gen)
            print(user)
    except StopIteration as e:
        print(e.value)  # prints "Batch processing complete"
# Main Points to keep in mind:
# - The function stream_users_in_batches is a generator that fetches rows from the user_data table in batches of a specified size using islice.
# - The function batch_processing processes these batches and yields users over the age of 25 one by one.
# - Both generators have a final return statement that provides a message when the generator is exhausted.
# - The test code demonstrates how to capture the return value of the generator using StopIteration exception handling.
# - The connection and cursor are properly closed after the iteration is complete.