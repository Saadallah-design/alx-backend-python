import sqlite3
import functools
from datetime import datetime


# first what is a decorator? A decorator is a function that takes another function as an argument, extends its behavior, and returns a new function. 
# Decorators are often used for logging, access control, instrumentation, and caching.
# Decorator to log SQL queries before execution
def log_queries(func):
    @functools.wraps(func)  # preserves the original function's metadata
    def wrapper(*args, **kwargs):
        # Try to get the SQL query from keyword arguments or first positional argument
        query = kwargs.get("query") or (args[0] if args else None)
        
        # If a query is found, print a log message
        if query:
            print(f"[LOG] Executing SQL query: {query}")
        
        # Call the original function with all arguments and return its result
        return func(*args, **kwargs)
    return wrapper  # return the wrapped function

# Apply the decorator to this function
@log_queries
def fetch_all_users(query: str) -> list:
    """
    Fetch all users from the database.
    
    Args:
        query (str): The SQL query to execute
    
    Returns:
        list: List of rows fetched from the database
    """
    # Open a connection to the SQLite database
    conn = sqlite3.connect('users.db')
    
    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    
    # Execute the SQL query passed to the function
    cursor.execute(query)
    
    # Fetch all results from the query
    results = cursor.fetchall()
    
    # Close the connection to free resources
    conn.close()
    
    return results  # return the fetched rows

# Example usage: fetch users while automatically logging the query
users = fetch_all_users(query="SELECT * FROM users;")
print(users)
