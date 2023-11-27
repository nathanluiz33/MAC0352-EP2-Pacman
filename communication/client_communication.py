import logging
import threading
import sys
import socket
import time
import json

from communication.protocol import Protocol

logging.basicConfig(filename='../communication/client.log', encoding='utf-8', level=logging.DEBUG)

class ClientCommunication:
    def __init__ (self, server_ip, server_port, protocol):
        if protocol == 'TCP':
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((server_ip, server_port))
        else:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.general_socket = Protocol(protocol, server_socket, (server_ip, server_port))

        logging.info(f"Connected to {server_ip}:{server_port}")

    def connect_to_server (self):
        package = {'type': 'connect', 'status': 'try'}
        message = json.dumps(package)
        logging.debug(f"Sending message to server: {message}")

        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')

        data = json.loads(data)
        logging.info(f"Received data from server: {data}")

        if self.general_socket.protocol == 'UDP':
            self.general_socket.change_address(data['address'])

        return data['type'] == 'connect' and data['status'] == 'ok'

    def create_user (self, username, password):
        package = {'type': 'create_user', 'status': 'try', 'username': username, 'password': password}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        logging.info(f"Received data from server: {data}")

        data = json.loads(data)

        return data['type'] == 'create_user' and data['status'] == 'ok', data['status']
    
    def login (self, username, password):
        package = {'type': 'login', 'status': 'try', 'username': username, 'password': password}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        logging.info(f"Received data from server: {data}")

        data = json.loads(data)

        return data['type'] == 'login' and data['status'] == 'ok', data['status']
    
    def change_password (self, old_password, new_password):
        package = {'type': 'change_password', 'status': 'try', 'old_password': old_password, 'new_password': new_password}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        logging.info(f"Received data from server: {data}")

        data = json.loads(data)

        return data['type'] == 'change_password' and data['status'] == 'ok', data['status']
    
    def logout (self):
        package = {'type': 'logout', 'status': 'try'}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        logging.info(f"Received data from server: {data}")

        data = json.loads(data)

        return data['type'] == 'logout' and data['status'] == 'ok'
    
    def get_leaderboard (self):
        package = {'type': 'get_leaderboard', 'status': 'try'}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        logging.info(f"Received data from server: {data}")

        data = json.loads(data)

        if data['type'] == 'get_leaderboard' and data['status'] == 'ok':
            return data['leaderboard']
        else:
            return None
        
    def get_online_users (self):
        package = {'type': 'get_online_users', 'status': 'try'}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        logging.info(f"Received data from server: {data}")

        data = json.loads(data)

        if data['type'] == 'get_online_users' and data['status'] == 'ok':
            return data['online_users']
        else:
            return None
    
    def tchau (self):
        package = {'type': 'tchau', 'status': 'try'}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        data = json.loads(data)

        return data['type'] == 'tchau' and data['status'] == 'ok'

    def start_game (self, host_ip, host_port):
        package = {'type': 'start_game', 'status': 'try', 'host_ip': host_ip, 'host_port': host_port}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        logging.info(f"Received data from server: {data}")

        data = json.loads(data)

        return data['type'] == 'start_game' and data['status'] == 'ok'
    
    def challenge (self, username):
        package = {'type': 'challenge', 'status': 'try', 'username': username}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        logging.info(f"Received data from server: {data}")

        data = json.loads(data)

        if data['type'] == 'challenge' and data['status'] == 'ok':
            return data['host'], data['status']
        else:
            return None, data['status']
        
    def send_score (self, user, score):
        package = {'type': 'send_score', 'status': 'try', 'user': user, 'score': score}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        logging.info(f"Received data from server: {data}")

        data = json.loads(data)

        return data['type'] == 'send_score' and data['status'] == 'ok'

    def change_status (self, username, status):
        package = {'type': 'change_status', 'status': 'try', 'username': username, 'lstatus': status}
        message = json.dumps(package)

        logging.debug(f"Sending message to server: {message}")
        self.general_socket.send_message(message)

        data = self.general_socket.receive_message()
        data = data.decode('ascii')
        logging.info(f"Received data from server: {data}")

        data = json.loads(data)

        return data['type'] == 'change_status' and data['status'] == 'ok'