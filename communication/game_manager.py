import logging
import threading
import sys
import socket
import time
import json

logging.basicConfig(filename='../communication/game_manager.log', encoding='utf-8', level=logging.INFO)

class GameManager:
    def __init__ (self):
        self.port = {}
        self.players = {}

    def create_game (self, username_host, host_ip, host_port):
        self.port[username_host] = (host_ip, host_port)
        self.players[username_host] = [username_host]

    def join_game (self, username_host, username):
        if username_host in self.players:
            self.players[username_host].append(username)
            return True
        else:
            return False
    
    def get_game_port (self, username_host):
        return self.port[username_host]

    def end_game (self, username_host):
        self.port.pop(username_host)
        self.players.pop(username_host)