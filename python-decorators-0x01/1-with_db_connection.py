# creating a decorator that automatically opens and closes a database connection

import sqlite3 
import functools

def with_db_connection(func):
    """ your code goes here""" 
    @functools.wraps(func)  # preserve metadata of the original function
    def wrapper(*args, **kwargs):
        
        # Open the database connection 
        conn = sqlite3.connect('users.db') 
        try: 
            # Pass the connection as the first argument to the function
            result = func(conn, *args, **kwargs) 
        finally: 
            # Ensure the connection is always closed
            conn.close() 
        return result 
    return wrapper

# Function that now receives a database connection automatically
@with_db_connection 
def get_user_by_id(conn, user_id): 
cursor = conn.cursor() 
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
return cursor.fetchone() 
#### Fetch user by ID with automatic connection handling 

user = get_user_by_id(user_id=1)
print(user)