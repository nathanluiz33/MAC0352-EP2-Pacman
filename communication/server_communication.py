import logging
import threading
import sys
import socket
import time
import json
import asyncio

from communication.protocol import Protocol
logging.basicConfig(filename='../communication/server.log', encoding='utf-8', level=logging.INFO)

from communication.server_database import ServerDataBase
from communication.game_manager import GameManager

server_database = ServerDataBase()
game_manager = GameManager()

class ServerCommunication:
    def __init__ (self, protocol, client_socket, otherside_address=None):
        self.general_socket = Protocol(protocol, client_socket, otherside_address)
        self.account_logged = None

    def connect_to_client (self):
        package = {'type': 'connect', 'status': 'ok', 'address': self.general_socket.this_socket.getsockname()}
        message = json.dumps(package)
        
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)

    def create_user (self, username, password):
        logging.info(f"Creating user with username {username} and password {password}")

        # verificamos se ja tem um user com esse login e senha
        if server_database.create_user(username, password) == False:
            package = {'type': 'create_user', 'status': 'error: username already exists'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
        else:
            package = {'type': 'create_user', 'status': 'ok'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
    
    def login (self, username, password):
        if not server_database.find_user(username):
            logging.info(f"User from {self.general_socket.otherside_address} could not login on {username}")
            package = {'type': 'login', 'status': 'error: username does not exist'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
        elif not server_database.check_password(username, password):
            logging.info(f"User from {self.general_socket.otherside_address} could not login on {username}")
            package = {'type': 'login', 'status': 'error: wrong password'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
        elif server_database.is_online(username):
            logging.info(f"User from {self.general_socket.otherside_address} could not login on {username}")
            package = {'type': 'login', 'status': 'error: user already logged in'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
        else:
            logging.info(f"User from {self.general_socket.otherside_address} logged in on {username}")
            self.account_logged = username
            package = {'type': 'login', 'status': 'ok'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)

            server_database.add_online_user(username, 'Online', self.general_socket)


    def change_password (self, old_password, new_password):
        if server_database.check_password (self.account_logged, old_password):
            server_database.new_password(self.account_logged, new_password)

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
        server_database.logout(self.account_logged)

        self.account_logged = None
        package = {'type': 'logout', 'status': 'ok'}
        message = json.dumps(package)
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)

    def get_leaderboard (self):
        package = {'type': 'get_leaderboard', 'status': 'ok', 'leaderboard': server_database.get_leaderboard()}
        message = json.dumps(package)
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)

    def get_online_users (self):
        package = {'type': 'get_online_users', 'status': 'ok', 'online_users': server_database.onlineUsersStatus}
        message = json.dumps(package)
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)

    def tchau (self):
        logging.info(f"User {self.general_socket.otherside_address} disconnected")
        server_database.logout(self.account_logged)

        package = {'type': 'tchau', 'status': 'ok'}
        message = json.dumps(package)
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)
    
    def start_game (self, host_ip, host_port):
        logging.info(f"User form {self.general_socket.otherside_address} started a game on account {self.account_logged}")
        game_manager.create_game(self.account_logged, host_ip, host_port)

        package = {'type': 'start_game', 'status': 'ok'}
        message = json.dumps(package)
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)

    def challenge (self, username):
        # precisamos desafiar o username
        if game_manager.join_game (username, self.account_logged):
            # se existe um jogo com esse username, entao o desafio foi aceito
            package = {'type': 'challenge', 'status': 'ok', 'host': game_manager.get_game_port(username)}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)
        else:
            package = {'type': 'challenge', 'status': 'error: user is not in-game or something else happened'}
            message = json.dumps(package)
            logging.debug(f"Sending message to client: {message}")
            self.general_socket.send_message(message)

    def send_score (self, user, score):
        server_database.update_leaderboard(user, score)

        package = {'type': 'send_score', 'status': 'ok'}
        message = json.dumps(package)
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)

    def change_status (self, username, lstatus):
        server_database.change_status(username, lstatus)

        package = {'type': 'change_status', 'status': 'ok'}
        message = json.dumps(package)
        logging.debug(f"Sending message to client: {message}")
        self.general_socket.send_message(message)
        

    def parse_client (self, initial_data = None):
        while True:
            logging.debug ("Waiting for data from client")

            if initial_data == None:
                recv_data = self.general_socket.receive_message()
            else:
                recv_data = initial_data
                initial_data = None

            if not recv_data:
                break

            recv_data = recv_data.decode('ascii')
            logging.debug(f"Received data from client: {recv_data}")

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
            elif data['type'] == 'get_online_users' and data['status'] == 'try':
                self.get_online_users()
            elif data['type'] == 'start_game' and data['status'] == 'try':
                self.start_game(data['host_ip'], data['host_port'])
            elif data['type'] == 'challenge' and data['status'] == 'try':
                self.challenge(data['username'])
            elif data['type'] == 'send_score' and data['status'] == 'try':
                self.send_score(data['user'], data['score'])
            elif data['type'] == 'change_status' and data['status'] == 'try':
                self.change_status(data['username'], data['lstatus'])
            elif data['type'] == 'tchau' and data['status'] == 'try':
                self.tchau()
                break
            else:
                package = {'type': 'error', 'status': 'error'}
                message = json.dumps(package)
                logging.debug(f"Sending message to client: {message}")
                self.general_socket.send_message(message)

