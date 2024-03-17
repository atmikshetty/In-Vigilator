import sqlite3

# Function to create a database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

# Function to create the users table
def create_users_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
        print("Users table created successfully.")
    except sqlite3.Error as e:
        print("Error creating users table:", e)

# Function to insert a user into the database
def insert_user(conn, username, password):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("User inserted successfully.")
    except sqlite3.Error as e:
        print("Error inserting user:", e)

# Main function
def main():
    # Create a connection to the database
    conn = create_connection('database.db')
    if conn:
        # Create the users table if it doesn't exist
        create_users_table(conn)
        # Insert the user 'atmikshetty' with PID '211106'
        insert_user(conn, 'atmikshetty', '211106')
        # Close the connection
        conn.close()
    else:
        print("Connection to the database failed.")

# Run the main function
if __name__ == "__main__":
    main()
