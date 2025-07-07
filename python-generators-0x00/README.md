# seed.py
This script initializes the MySQL ALX_prodev database.
It establishes connections to the server and the specific database.
It creates the user_data table with the required fields (UUID, name, email, age).
Finally, it populates this table by inserting data from a CSV file.

# 0-stream_users.py
This file contains a generator function, stream_users().
It connects to the ALX_prodev database.
It retrieves rows from the user_data table one by one.
Each user is yielded (streamed) as a dictionary for efficient memory management.

# 1-batch_processing.py
This script implements batch data retrieval from the database.
The stream_users_in_batches() function uses yield to return lists of users.
batch_processing() iterates over these batches and filters out users over the age of 25. It ensures efficient processing for large data sets.

# 2-lazy_paginate.py
This file simulates lazy data pagination.
It includes a paginate_users() function that retrieves a specific page.
The generator function lazy_pagination() yields each completed page.
This allows data to be loaded page by page, only when needed.