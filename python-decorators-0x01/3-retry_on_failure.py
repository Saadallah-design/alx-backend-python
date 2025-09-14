# create a decorator that retries database operations if they fail due to transient errors
import sqlite3
import functools
import time

# Decorator to retry database operations
def retry_db_operation(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)  # preserves the original function's metadata
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)  # Try to execute the decorated function
                except sqlite3.OperationalError as e:
                    last_exception = e
                    print(f"[RETRY] Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)  # Wait before retrying
            print(f"[FAILURE] All {retries} attempts failed.")
            raise last_exception  # Raise the last exception if all retries fail
        return wrapper  # return the wrapped function
    return decorator  # return the decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)