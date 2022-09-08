import sqlite3

# This file will contain database related functions - processing, parsing etc.

# DB_Manager is a parent class that manages a database - only one database per db_manager object
class DB_Manager():

    def __init__(self, db_path):
        self.connection = None 
        self.cursor = None
        self.db_path = db_path

    # Set database path manually
    def set_db_path(self, db_path):
        self.db_path = db_path

    # For connecting to the database - sets the connection as self.db and the cursor as self.cursor
    def connect_db(self):
        self.connection = sqlite3.connect(self.db_path) 
        self.cursor = self.connection.cursor()
    
    # Executes and returns the result of the sql command
    def exec(self, sql_command, args=None):

        # Take care of case when there are no additional arguments being passed
        if args != None:
            self.cursor.execute(sql_command, args)
            return self.cursor.fetchall()

        self.cursor.execute(sql_command)

        return self.cursor.fetchall() # Optional return to return SQL output 
    
    # Commit the updates to the database
    def commit(self):
        self.connection.commit()

    # Closes the cursor and connection:
    def close(self):
        self.cursor.close()
        self.connection.close()

# Inherits from DB_Manager - contains arena.db specific methods
class Arena_DB_Manager(DB_Manager):

    def __init__(self, db_path):
        super().__init__(db_path)

    # Create the users database - contains users and user_watchlist table
    def init_arena_db(self, reset=False):
        self.connect_db() 
        
        # Drop the tabless - to renew the entire database (dangerous in production!)
        if reset == True:
            self.exec('DROP TABLE IF EXISTS users;')
            self.exec('DROP TABLE IF EXISTS user_watchlist;')

        # Creates the 'users' table in the database
        self.exec('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT NOT NULL, 
                    email TEXT NOT NULL, 
                    pwd TEXT NOT NULL
                );
            ''')

        # Creates the 'user_watchlist' table in the database
        self.exec('''
                CREATE TABLE IF NOT EXISTS user_watchlist ( 
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    coin_id TEXT NOT NULL,
                    FOREIGN KEY (user_id)
                        REFERENCES users (id)
                        ON UPDATE SET NULL 
                        ON DELETE SET NULL
                );
            ''')

        # Close the cursor and connection
        self.close()

    # Adds user credentials to arena.db
    def add_user_credentials(self, user_data):
        self.connect_db()
        sql_string = 'INSERT INTO users (username, email, pwd) VALUES (?, ?, ?)'
        self.exec(sql_string, user_data)
        
        self.commit()
        self.close()

if __name__ == '__main__':
    # create_user_db()
    db_man = DB_Manager()
    db_man.init_arena_db()
