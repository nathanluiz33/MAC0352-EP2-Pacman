import logging
import threading
import sys
import socket
import time
import json
import asyncio

logging.basicConfig(filename='../communication/server_database.log', encoding='utf-8', level=logging.DEBUG)

class ServerDataBase:
    def __init__(self):
        self.onlineUsersStatus = {}
        self.usersDatabase = {}
        self.leaderboard = {}
        self.onlineUsersSocket = {}

    def add_online_user (self, username, status, socket):
        self.onlineUsersStatus[username] = status
        self.onlineUsersSocket[username] = socket

    def remove_online_user (self, username):
        self.onlineUsersStatus.pop(username)
        self.onlineUsersSocket.pop(username)

    def create_user(self, username, password):
        if username in self.usersDatabase:
            logging.info(f"Username {username} already exists")
            return False
        else:
            logging.info(f"Created user with username {username} and password {password}")
            self.usersDatabase[username] = password
            return True
        
    def new_password (self, username, password):
        self.usersDatabase[username] = password

    def find_user(self, username):
        return username in self.usersDatabase
    
    def check_password (self, username, password):
        if self.find_user(username):
            return self.usersDatabase[username] == password
        else:
            return False
        
    def is_online (self, username):
        return username in self.onlineUsersStatus

    def logout (self, username):
        self.remove_online_user(username)

    