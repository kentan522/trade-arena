import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import json

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

    # Check for allowing user login
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


            self.close()

            # Return false if password doesn't match
            if not check_password_hash(hashed_pwd, password):
                return False
            
            # Otherwise return True
            return True
    
    # Check for preventing registration of existing username or email
    def check_exists_credentials(self, username, email):
        self.connect_db()

        # Should support caching in the future instead of querying the whole user table 
        # Probably save check_register_dict as an attribute of the dbmanager?
        # Probably can just check through each values within the nested loop below and return to exit the loop when the same username is encountered? 
            # That was I don't have to store everything in a dict
        obtain_user_str = 'SELECT username, email FROM users'
        user_data = self.exec(obtain_user_str)

        self.close()
        columns = [description[0] for description in self.cursor.description] # Obtain columns from output of last SQL command

        # Create a dictionary containing all usernames and emails from the database
        # Maybe change this to an internal function?
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

    # Calls API to get coin data, for adding coin to user's watchlist
    def add_coin_data(self, username, coin_name):

        data = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_name}&vs_currencies=usd").json()

        if data:
            # Obtain coin name - this is still called instead of using the passed in 'coin_name' because the passed in 'coin_name' may have weird casing combinations
            coin_name = list(data.keys())[0]

            self.connect_db()

            # Obtain user id based on username of current logged in user
            obtain_id_str = 'SELECT id FROM users WHERE username=(?)'
            user_id = self.exec(obtain_id_str, (username,))[0][0]

            # Obtain coin_ids in the user's watchlist
            obtain_coin_str = 'SELECT coin_id FROM user_watchlist WHERE user_id=(?)'
            coin_ids = self.exec(obtain_coin_str, (user_id, ))
            
            # If there are coins in the user's watchlist
            if len(coin_ids) != 0:

                # Only limit 10 coins in the watchlist (FOR NOW)
                if len(coin_ids) > 10:
                    return False

                # Obtain the list of tuples coin_ids = [(coin_name,)...]
                coin_ids = self.exec(obtain_coin_str, (user_id, ))

                # Convert the list of tuples to a list of coin names
                coin_names = []
                for i in range(len(coin_ids)):
                    coin_names.append(coin_ids[i][0])

                # Check if coin is already in the watchlist
                if coin_name in coin_names:
                    # Coin is already in the watchlist!
                    # Use a json file to handle this maybe? And use json files to handle all message flashes [FUTURE REFACTORING]
                    return False

            # Otherwise, add coin to watchlist of user id 
            add_watchlist_str = 'INSERT INTO user_watchlist (user_id, coin_id) VALUES (?, ?);'
            self.exec(add_watchlist_str, (user_id, coin_name))

            print('Coin added to watchlist!')
            
            self.commit()
            self.close()

            return True

        else:
            # No coin was found
            return False

    def get_coin_watchlist_data(self, username):
        self.connect_db()

        # Obtain user id based on username of current logged in user
        obtain_id_str = 'SELECT id FROM users WHERE username=(?)'
        user_id = self.exec(obtain_id_str, (username,))[0][0]

        # Obtain the list of tuples coin_ids = [(coin_name,)...]
        obtain_coin_str = 'SELECT coin_id FROM user_watchlist WHERE user_id=(?)'
        coin_ids = self.exec(obtain_coin_str, (user_id, ))

        # If there are coins in the user's watchlist - this is for loading the watch list initially but when the watchlist is empty
        if len(coin_ids) == 0:
            return [], []

        # Convert the list of tuples to a list of coin names
        coin_names = []
        for i in range(len(coin_ids)):
            coin_names.append(coin_ids[i][0])

        # THIS IS VERY SLOW SINCE IT MAKES MULTIPLE API CALLS, INSTEAD CALL ONCE TO GET ALL PRICES
        # Update coin price data for each coin
        coin_prices = []
        for coin in coin_names:
            data = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd").json()
            
            coin_prices.append(list(data[coin].values())[0])
        
        print('Coin price data updated!')
        self.close()
        return coin_names, coin_prices



if __name__ == '__main__':
    # Testing
    pass
