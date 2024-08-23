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

# Get the slot labels from the provided list
slot_labels = [
    'city', 'rest_type', 'price_type', 'direction', 'source_calender', 'dest_calender', 'date', 'place_type',
    'prayer_time', 'num1', 'operator', 'num2', 'input', 'source_unit', 'dest_unit', 'alphabet', 'esm_famil_subject',
    'starting_point', 'ending_point', 'source_city', 'dest_city', 'dest_currency', 'movie', 'cinema',
    'gc', 'food_volume', 'food_name', 'nutrition', 'complaint_subject', 'country', 'holiday', 'month', 'prayer_name',
    'movie_genre', 'word', 'length', 'sentence', 'origin_language', 'destination_language', 'currency', 'sore_name', 'num',
    'ingredient', 'book_name', 'telephone', 'poem_subject', 'poet', 'poem_genre', 'song_name', 'singer', 'genre',
    'favorate_subject', 'user_name', 'picture_subject', 'd_subject', 'day', 'nahjcat'
]

# Function to create the slots table
def create_slots_table():
    cursor = conn.cursor()
    # Create table with the specified columns
    columns = ', '.join([f"{label} TEXT" for label in slot_labels])
    create_table_query = f"CREATE TABLE IF NOT EXISTS slots (id SERIAL PRIMARY KEY, {columns})"
    cursor.execute(create_table_query)
    # Initialize the table with an empty row if it doesn't exist
    cursor.execute("SELECT COUNT(*) FROM slots")
    if cursor.fetchone()[0] == 0:
        cursor.execute(f"INSERT INTO slots DEFAULT VALUES")
    cursor.close()
    print('DB:       slots table created with initial values set to NULL')

# Function to update slot values
def update_slot(slot: str, value: str):
    cursor = conn.cursor()
    print(f'updating slot {slot} to {value}')
    update_query = f"UPDATE slots SET {slot} = %s WHERE id = 1"
    cursor.execute(update_query, (value,))
    cursor.close()
    print('done')


# Function to get a specific slot value
def get_slot(slot: str) -> Optional[str]:
    cursor = conn.cursor()
    select_query = f"SELECT {slot} FROM slots WHERE id = 1"
    cursor.execute(select_query)
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


# Function to clear all slot values
def clear_slots():
    cursor = conn.cursor()
    clear_query = f"UPDATE slots SET {', '.join([f'{label} = NULL' for label in slot_labels])} WHERE id = 1"
    cursor.execute(clear_query)
    cursor.close()
    print('slot values cleared')


# Function to check if a slot is in the slots table columns
def is_slot_in_columns(slot: str) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='slots'")
    columns = cursor.fetchall()
    cursor.close()
    column_names = [column[0] for column in columns]
    return slot in column_names

# Close the connection when done
def close_connection():
    conn.close()
