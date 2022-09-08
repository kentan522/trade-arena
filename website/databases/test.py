import sqlite3
from flask import g

connection = sqlite3.connect('users.db')
cursor = connection.cursor()
cursor.execute('''
INSERT INTO users VALUES (1, ken, ken, 123);
''')
# cursor.execute('SELECT * FROM users;')
# data = cursor.fetchall()
# print(data)