# starting with importing sqlite3 module
import sqlite3  
# Implement a class based custom context manager ExecuteQuery that takes the query: ”SELECT * FROM users WHERE age > ?” and the parameter 25 and returns the result of the query

class ExecuteQuery:
    def __init__(self, db_name, query, param):
        self.db_name = db_name
        self.query = query
        self.param = param
        self.connection = None
        self.cursor = None

    def __enter__(self):
        # open the database connection
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        # execute the query with the parameter
        self.cursor.execute(self.query, (self.param,))
        return self.cursor.fetchall()  # fetch and return all results

    def __exit__(self, exc_type, exc_value, traceback):
        # close the cursor and database connection
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

# Ensure to use the__enter__() and the __exit__() methods

if __name__ == "__main__":  # Ensures that this block of code runs only when the script is executed directly, not when imported as a module.
    query = "SELECT * FROM users WHERE age > ?;"
    param = 25
    with ExecuteQuery('users.db', query, param) as results:  # ExecuteQuery('users.db', query, param) creates an instance of your class, passing 'users.db' as the database name, the query, and the parameter.
        for row in results:
            print(row)