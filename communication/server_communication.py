import logging
import threading
import sys
import socket
import time
import json
import asyncio

from communication.protocol import Protocol
logging.basicConfig(filename='../communication/server.log', encoding='utf-8', level=logging.DEBUG)

usersDatabase = {}
leaderboard = {}

class ServerCommunication:
    def __init__ (self, protocol, client_socket, otherside_address=None):
        self.general_socket = Protocol(protocol, client_socket, otherside_address)
        self.account_logged = None

    def connect_to_client (self):
        package = {'type': 'connect', 'status': 'ok', 'adress': self.general_socket.this_socket.getsockname()}
        message = json.dumps(package)
        
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)

    def create_user (self, username, password):
        logging.info(f"Creating user with username {username} and password {password}")

        # verificamos se ja tem um user com esse login e senha
        if username in usersDatabase:
            package = {'type': 'create_user', 'status': 'error: username already exists'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
        else:
            usersDatabase[username] = password
            package = {'type': 'create_user', 'status': 'ok'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
    
    def login (self, username, password):
        if not (username in usersDatabase):
            package = {'type': 'login', 'status': 'error: username does not exist'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
        elif usersDatabase[username] != password:
            package = {'type': 'login', 'status': 'error: wrong password'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
        else:
            self.account_logged = username
            package = {'type': 'login', 'status': 'ok'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)

    def change_password (self, old_password, new_password):
        if usersDatabase[self.account_logged] == old_password:
            usersDatabase[self.account_logged] = new_password
            package = {'type': 'change_password', 'status': 'ok'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
        else:
            package = {'type': 'change_password', 'status': 'error: wrong password'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)

    def logout (self):
        self.account_logged = None
        package = {'type': 'logout', 'status': 'ok'}
        message = json.dumps(package)
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)

    def get_leaderboard (self):
        package = {'type': 'get_leaderboard', 'status': 'ok', 'leaderboard': leaderboard}
        message = json.dumps(package)
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)

    def parse_client (self, initial_data = None):
        while True:
            logging.debug (usersDatabase)
            logging.debug (leaderboard)
            logging.info ("Waiting for data from client")

            if initial_data == None:
                recv_data = self.general_socket.receive_message()
            else:
                recv_data = initial_data
                initial_data = None

            if not recv_data:
                break

            recv_data = recv_data.decode('ascii')
            logging.info(f"Received data from client: {recv_data}")

            data = json.loads(recv_data)

            if data['type'] == 'connect' and data['status'] == 'try':
                self.connect_to_client()
            elif data['type'] == 'create_user' and data['status'] == 'try':
                self.create_user(data['username'], data['password'])
            elif data['type'] == 'login' and data['status'] == 'try':
                self.login(data['username'], data['password'])
            elif data['type'] == 'change_password' and data['status'] == 'try':
                self.change_password(data['old_password'], data['new_password'])
            elif data['type'] == 'logout' and data['status'] == 'try':
                self.logout()
            elif data['type'] == 'get_leaderboard' and data['status'] == 'try':
                self.get_leaderboard()
            else:
                package = {'type': 'error', 'status': 'error'}
                message = json.dumps(package)
                logging.debug(f"Sending message to client: {message}")
                self.general_socket.send_message(message)
