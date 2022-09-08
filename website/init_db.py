import sqlite3
from venv import create

# Create the users database
def create_user_db():
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    
    # Drop the table if it exists
    cursor.execute('DROP TABLE IF EXISTS users;')

    # Creates the database 
    cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT NOT NULL, 
                email TEXT NOT NULL, 
                pwd TEXT NOT NULL
            );
    ''')

    connection.close()

if __name__ == '__main__':
    create_user_db()
