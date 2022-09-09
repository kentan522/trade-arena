import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

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
        user_data[2] = generate_password_hash(user_data[2], method='sha256') # Hash the password

        insert_user_str = 'INSERT INTO users (username, email, pwd) VALUES (?, ?, ?);'
        self.exec(insert_user_str, user_data)
        
        self.commit()
        self.close()

    def check_login_credentials(self, login_data):
        self.connect_db()
        username = login_data[0]
        password = login_data[1]
        obtain_user_str = "SELECT username FROM users WHERE username = (?);"

        # Return false if username does not exist in the db
        if len(self.exec(obtain_user_str, (username, ))) == 0:
            return False

        else:
            
            # Obtain the hashed password using the login's username
            obtain_pwd_str = "SELECT pwd FROM users WHERE username = (?);"
            hashed_pwd = self.exec(obtain_pwd_str, (username,))[0][0] # Since queries are returned as [(hashedpwd, )]

            # Return false if password doesn't match
            if not check_password_hash(hashed_pwd, password):
                return False
            
            # Otherwise return True
            return True
    
    def check_exists_credentials(self, username, email):
        self.connect_db()

        # Should support caching in the future instead of querying the whole user table 
        # Probably save check_register_dict as an attribute of the dbmanager?
        # Probably can just check through each values within the nested loop below and return to exit the loop when the same username is encountered? 
            # That was I don't have to store everything in a dict
        obtain_user_str = 'SELECT username, email FROM users'
        user_data = self.exec(obtain_user_str)
        columns = [description[0] for description in self.cursor.description] # Obtain columns from output of last SQL command

        # Create a dictionary containing all usernames and emails from the database
        check_register_dict = {}
        for i in range(len(columns)):
            check_register_dict[columns[i]] = []
            for data in user_data:
                check_register_dict[columns[i]].append(data[i])
        
        username_exists = username in check_register_dict[columns[0]]
        email_exists = email in check_register_dict[columns[1]]

        if username_exists or email_exists:
            return True

        return False




        


        

if __name__ == '__main__':
    # create_user_db()
    db_man = DB_Manager()
    db_man.init_arena_db()
