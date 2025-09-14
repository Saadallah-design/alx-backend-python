# create a decorator that manages database transactions by automatically committing or rolling back changes
import sqlite3
import functools

def transactional(func):
    @functools.wraps(func)  # preserve metadata of the original function
    def wrapper(*args, **kwargs):
        # Open the database connection
        conn = sqlite3.connect('users.db')
        try:
            # Start a transaction
            conn.execute('BEGIN;')
            # Pass the connection as the first argument to the function
            result = func(conn, *args, **kwargs)
            # Commit the transaction if no exceptions occurred
            conn.commit()
        except Exception as e:
            # Rollback the transaction in case of an error
            conn.rollback()
            print(f"Transaction failed: {e}")
            raise  # Re-raise the exception after rollback
        finally:
            # Ensure the connection is always closed
            conn.close()
        return result
    return wrapper

# Function that now receives a database connection automatically
@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
cursor = conn.cursor() 
cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
#### Update user's email with automatic transaction handling 

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')