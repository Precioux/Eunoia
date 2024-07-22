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
# cursor = conn.cursor()


# Create table with the specified columns
# create_table_query = """
# CREATE TABLE IF NOT EXISTS states (
#     id SERIAL PRIMARY KEY,
#     conversation_id TEXT,
#     turn INTEGER,
#     state TEXT,
#     intent TEXT
# )
# """
# cursor.execute(create_table_query)

# Function to add entries to the states table
def add_entry(conversation_id: str, turn: int, state: str, intent: str):
    print(
        f'adding to states table with conversation_id: {conversation_id}, turn: {turn}, state: {state}, intent: {intent}')
    cursor = conn.cursor()
    insert_query = "INSERT INTO states (conversation_id, turn, state, intent) VALUES (%s, %s, %s, %s)"
    cursor.execute(insert_query, (conversation_id, turn, state, intent))
    cursor.close()
    print('done')


# Function to get intent based on conversation_id and turn
def get_intent(conversation_id: str, turn: int) -> Optional[str]:
    cursor = conn.cursor()
    print(f'getting intent of conversation_id: {conversation_id}, turn: {turn}')
    select_query = "SELECT intent FROM states WHERE conversation_id = %s"
    cursor.execute(select_query, (conversation_id))
    result = cursor.fetchone()
    print(f'result: {result}')
    cursor.close()
    return result[0] if result else None

# Function to check if the table is empty
def is_table_empty(table_name: str) -> bool:
    cursor = conn.cursor()
    print(f'checking if table {table_name} is empty')
    select_query = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(select_query)
    result = cursor.fetchone()
    is_empty = result[0] == 0
    print(f'table {table_name} is empty: {is_empty}')
    cursor.close()
    return is_empty

# Function to get the conversation_id of the latest added row
def get_latest_conversation_id() -> Optional[str]:
    print('getting conversation_id of the latest added row')
    cursor = conn.cursor()
    select_query = "SELECT conversation_id FROM states ORDER BY id DESC LIMIT 1"
    cursor.execute(select_query)
    result = cursor.fetchone()
    print(f'latest conversation_id: {result[0]}' if result else 'No rows found')
    cursor.close()
    return result[0] if result else None

# Function to get the latest status of a given conversation_id
def get_latest_status(conversation_id: str) -> Optional[str]:
    print(f'getting latest status for conversation_id: {conversation_id}')
    cursor = conn.cursor()
    select_query = "SELECT state FROM states WHERE conversation_id = %s ORDER BY id DESC LIMIT 1"
    cursor.execute(select_query, (conversation_id,))
    result = cursor.fetchone()
    print(f'latest status: {result[0]}' if result else 'No rows found')
    cursor.close()
    return result[0] if result else None


# Function to check if a conversation_id is available in the states table
def is_conversation_id_available(conversation_id: str) -> bool:
    print(f'checking if conversation_id: {conversation_id} is available in states table')
    cursor = conn.cursor()
    select_query = "SELECT 1 FROM states WHERE conversation_id = %s LIMIT 1"
    cursor.execute(select_query, (conversation_id,))
    result = cursor.fetchone()
    is_available = result is not None
    print(f'conversation_id: {conversation_id} is available: {is_available}')
    cursor.close()
    return is_available


# Example usage
# add_entry('conv1', 1, 'state1', 'intent1')
# # add_entry('conv1', 2, 'state2', 'intent2')
# print(get_intent('conv1', 1))  # Output: intent1
# # print(get_intent('conv1', 2))  # Output: intent2

# Close the connection when done
def close_connection():
    conn.close()