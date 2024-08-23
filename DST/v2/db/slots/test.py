from DST.db.slots.funcs import *
import psycopg2
from typing import Optional

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "chitchat-dst-db"

# Connect to the database
conn = psycopg2.connect(
    dbname=DB_NAME,
    host=DB_HOST,
    port=DB_PORT
)
conn.autocommit = True
cursor = conn.cursor()


update_slot('city', 'تهران')
# print(get_slot('city'))  # Output: تهران
# update_slot('food_name', 'پاستا')
# print(get_slot('food_name'))  # Output: پاستا
# print(get_slot('city'))  # Output: تهران
# clear_slots()
# print(get_slot('city'))  # Output: None
# print(get_slot('food_name'))  # Output: None


# Close the cursor and connection
cursor.close()
conn.close()