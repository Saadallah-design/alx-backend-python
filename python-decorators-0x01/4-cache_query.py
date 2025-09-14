# create a decorator that caches the results of a database queries inorder to avoid redundant calls
import sqlite3
import functools
from datetime import datetime

# Decorator to cache SQL query results
def cache_query(func):
    cache = {}  # dictionary to store cached results

    @functools.wraps(func)  # preserves the original function's metadata
    def wrapper(*args, **kwargs):
        query = kwargs.get("query") or (args[0] if args else None)
        
        # Check if the result is already in the cache
        if query in cache:
            print(f"[CACHE] Returning cached result for query: {query}")
            return cache[query]
        
        # If not in cache, execute the function and store the result
        result = func(*args, **kwargs)
        cache[query] = result  # store the result in the cache
        print(f"[CACHE] Caching result for query: {query}")
        return result

    return wrapper  # return the wrapped function

# Apply the decorator to this function
@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")