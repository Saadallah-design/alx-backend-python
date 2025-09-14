# starting with importing sqlite3 module
import sqlite3

# create a class based context manager to handle opening and closing the database connection
class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    def __enter__(self):
        # open the database connection
        self.connection = sqlite3.connect(self.db_name)
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        # close the database connection
        if self.connection:
            self.connection.close()

# Use the context manager with the with statement to be able to perform the query SELECT * FROM users. Print the results from the query.

if __name__ == "__main__": # Ensures that this block of code runs only when the script is executed directly, not when imported as a module.
    with DatabaseConnection('users.db') as conn: # DatabaseConnection('users.db') creates an instance of your class, passing 'users.db' as the database name.
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users;")
        # fetchall() returns a list of tuples, where each tuple represents a row from the table.
        rows = cursor.fetchall()
        for row in rows:
            print(row)