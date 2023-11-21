import logging
import threading
import sys
import socket
import time
import json

logging.basicConfig(filename='../communication/client.log', encoding='utf-8', level=logging.DEBUG)

class Game:
    def __init__ (self, username_host):
        self.board = ['******.**... .....**.******', '******.**.*******.**.******', '******.**.*.. ..*.**.******', '..... ....*.....*.......F..', '******.**.*.. ..*.**.******']
        self.players = {}
        self.players[username_host] = {'symbol': 'C', 'x': 0, 'y': 0}
    def start_game (self):
        pass

    def move (self, player, direction):
        
