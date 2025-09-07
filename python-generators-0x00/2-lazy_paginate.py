# Lazy loading Paginated Data
# Objective: Simulte fetching paginated data from the users database using a generator to lazily load each page

#!/usr/bin/python3
seed = __import__('seed')


def paginate_users(page_size, offset):

    # Fetch a single page of users from the database.

    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def lazy_pagination(page_size):
    
    # Generator function that yields pages of users lazily.
    # Only fetches the next page when needed.

    offset = 0
    while True:  # Only one loop
        page = paginate_users(page_size, offset)
        if not page:  # No more rows
            break
        yield page  # Yield the current page
        offset += page_size  # Move to the next page


# Optional test
if __name__ == "__main__":
    for page in lazy_pagination(5):
        for user in page:
            print(user)
# Main Points to keep in mind:
# - The function lazy_pagination is a generator that fetches pages of users from the user_data table lazily.
# - It uses a while loop to continuously fetch pages until no more rows are returned.
# - Each page is fetched using the paginate_users function, which takes page_size and offset as arguments.
# - The generator yields each page of users, allowing the caller to process one page at a time.
# - The offset is incremented by page_size after each yield to fetch the next page in the subsequent iteration.
# - The connection and cursor are properly closed after fetching each