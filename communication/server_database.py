import sqlite3
import logging
from sqlite3 import Error
from queue import Queue
from threading import Lock

class ConnectionPool:
    def __init__(self, db_path, pool_size=5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self._lock = Lock()

    def get_connection(self):
        with self._lock:
            if self.pool.empty():
                return sqlite3.connect(self.db_path)
            else:
                return self.pool.get()

    def release_connection(self, connection):
        with self._lock:
            if self.pool.qsize() < self.pool_size:
                self.pool.put(connection)
            else:
                connection.close()

class ServerDataBase:
    def __init__(self, db_path='server_database.db', pool_size=5):
        self.db_path = db_path
        self.connection_pool = ConnectionPool(db_path, pool_size)

        self.onlineUsersStatus = {}
        self.onlineUsersSocket = {}

        # Create tables if they don't exist
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard (
                    username TEXT PRIMARY KEY,
                    score INTEGER
                )
            ''')

            conn.commit()

    def execute_query(self, query, parameters=None):
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def create_user(self, username, password):
        try:
            self.execute_query('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            logging.info(f"Created user with username {username} and password {password}")
            return True
        except Error as e:
            logging.error(f"Error creating user: {e}")
            return False

    def new_password(self, username, password):
        self.execute_query('UPDATE users SET password=? WHERE username=?', (password, username))

    def find_user(self, username):
        result = self.execute_query('SELECT * FROM users WHERE username=?', (username,))
        return len(result) > 0

    def check_password(self, username, password):
        result = self.execute_query('SELECT password FROM users WHERE username=?', (username,))
        return len(result) > 0 and result[0][0] == password

    def update_leaderboard(self, username, score):
        try:
            self.execute_query('INSERT INTO leaderboard (username, score) VALUES (?, ?) ON CONFLICT(username) DO UPDATE SET score=score+?', (username, score, score))
        except Error as e:
            logging.error(f"Error updating leaderboard: {e}")

    def get_leaderboard(self):
        return self.execute_query('SELECT * FROM leaderboard')

    def add_online_user (self, username, status, socket):
        self.onlineUsersStatus[username] = status
        self.onlineUsersSocket[username] = socket

    def remove_online_user (self, username):
        if username in self.onlineUsersStatus:
            self.onlineUsersStatus.pop(username)
            self.onlineUsersSocket.pop(username)

    def is_online (self, username):
        return username in self.onlineUsersStatus

    def logout (self, username):
        self.remove_online_user(username)

    def change_status (self, username, status):
        self.onlineUsersStatus[username] = status