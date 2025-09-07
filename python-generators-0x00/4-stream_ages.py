# 4. Memory-Efficient Aggregation with Generators
# Objective: to use a generator to compute a memory-efficient aggregate function i.e average age for a large dataset

#!/usr/bin/python3
seed = __import__('seed')


def stream_user_ages():
   
    # Generator that yields user ages one by one from the user_data table.
   
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data;")

    for row in cursor:  # Only one loop
        yield row['age']

    cursor.close()
    connection.close()


def compute_average_age():
    
   # Computes the average age of users using the stream_user_ages generator.
    
    total = 0
    count = 0

    for age in stream_user_ages():  # Loop 2
        total += age
        count += 1

    if count == 0:
        return 0
    return total / count


if __name__ == "__main__":
    average_age = compute_average_age()
    print(f"Average age of users: {average_age:.2f}")

# Main Points to keep in mind:
# - The function stream_user_ages is a generator that connects to the database, executes a query to fetch all ages from the user_data table, and yields each age one by one using a single loop and yield statement.
# - The function compute_average_age uses the stream_user_ages generator to compute the average age of users by iterating over the ages yielded by the generator.
# - Both functions ensure that the database connection and cursor are properly closed after use.
# - This approach is memory-efficient as it does not load all ages into memory at once, but processes them one by one.
# - The average age is computed by maintaining a running total and count of ages, and the final average is calculated after the iteration is complete.
# - The test code in the __main__ block demonstrates how to call the compute_average_age function and print the result.
# a generator is a function that returns an iterator that produces a sequence of values using the yield statement.
# - The connection and cursor are properly closed after the iteration is complete.