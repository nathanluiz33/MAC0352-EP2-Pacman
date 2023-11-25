import logging
import threading
import sys
import socket
import time
import json

logging.basicConfig(filename='../communication/game_manager.log', encoding='utf-8', level=logging.DEBUG)

class GameManager:
    def __init__ (self):
        self.hostPort = {}
        self.players = {}

    def create_game (self, username_host, hostPort):
        self.hostPort[username_host] = hostPort

    def join_game (self, username_host, username):
        if username_host not in self.players:
            return False
        else:
            self.players[username_host].append(username)
            return True

    def end_game (self, username_host):
        self.hostPort.pop(username_host)
        self.players.pop(username_host)