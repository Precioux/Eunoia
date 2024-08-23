import psycopg2

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

# Get the slot labels from the provided list
slot_labels = [
    'city', 'rest_type', 'price_type', 'direction', 'source_calender', 'dest_calender', 'date', 'place_type',
    'prayer_time', 'num1', 'operator', 'num2', 'input', 'source_unit', 'dest_unit', 'alphabet', 'esm_famil_subject',
    'starting_point', 'ending_point', 'source_city', 'dest_city', 'dest_currency', 'movie', 'cinema',
    'gc', 'food_volume', 'food_name', 'nutrition', 'complaint_subject', 'country', 'holiday', 'month', 'prayer_name',
    'movie_genre', 'word', 'length', 'sentence', 'origin_language', 'destination_language', 'currency', 'sore_name', 'num',
    'ingredient', 'book_name', 'telephone', 'poem_subject', 'poet', 'poem_genre', '"song name"', 'singer', 'genre',
    'favorate_subject', 'user_name', 'picture_subject', 'd_subject', 'day', 'nahjcat'
]

# Create table with the specified columns
columns = ', '.join([f"{label} TEXT" for label in slot_labels])
create_table_query = f"CREATE TABLE IF NOT EXISTS slots (id SERIAL PRIMARY KEY, {columns})"
cursor.execute(create_table_query)

# Initialize the table with an empty row if it doesn't exist
cursor.execute("SELECT COUNT(*) FROM slots")
if cursor.fetchone()[0] == 0:
    cursor.execute(f"INSERT INTO slots DEFAULT VALUES")

# Close the cursor and connection
cursor.close()
conn.close()