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
        self.players = []
        self.add_player(username_host, 'C', 0, 0)

    def add_player (self, username, symbol, x, y):
        self.players.insert (0, {"username": username, 'symbol': symbol, 'x': x, 'y': y})

    def move (self, username, direction):
        symbol = self.player[username]['symbol']
        dx = 0
        dy = 0
        if direction == 'a':
            dx = -1
        elif direction == 'd':
            dx = 1
        elif direction == 'w':
            dy = 1
        elif direction == 's':
            dy = -1
        else:
            return False

class Pacman ():
    def __init__ (self, host_name):
        self.game = Game(host_name)
        # e um socket que vai ficar escutando por players
        self.players_sockets = {}
        self.turn = []
        self.incoming_players = []

    def add_incoming_player (self, username, host, port):
        self.incoming_players.append((username, host, port))

    def start_game (self):
        while True:
            for player in self.players:
                user = player['username']
                if player['symbol'] == 'C':
                    line = input("Pac-Man> ")
                    line = line.split()

                    if line[0] == 'move':
                        # TODO: move
                        pass
                    elif line[0] == 'encerra':
                        self.end_game()
                    else:
                        print("Comando invalido")
                else:
                    data = {'type': 'request_command', 'status': 'try'}
                    message = json.dumps(data)
                    self.players_sockets[user].sendall(message.encode('ascii'))

                    recv = self.players_sockets[user].recv(1024)
                    recv = recv.decode('ascii')

                    recv = json.loads(recv)
                    if recv['type'] == 'send_command' and recv['status'] == 'ok':
                        command = recv['command']

                        if command == 'move':
                            # TODO: move
                            pass
                        elif command == 'encerra':
                            self.end_game()
                        else:
                            print("Comando invalido")
                    else:
                        print("Algo deu errado")
    
    def flush_incoming_players (self):
        # TODO: add mutex
        for player in self.incoming_players:
            self.connect_to_player(player[0], player[1], player[2])

    def connect_to_player (self, username, host, port):
        # inicializamos um socket que conectar com os ghosts
        ghost_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ghost_socket.connect (host, port)

        self.players_sockets[username] = ghost_socket

        if len(self.players) == 1:
            self.game.add_player(username, 'F', 0, 0)
        else:
            self.game.add_player(username, 'f', 0, 0)

    def end_game (self):
        pass

class Ghost ():
    def __init__ (self, ghost_name, game):
        self.game = game
        if len(game.player) == 1:
            self.game.add_player(ghost_name, 'F', 0, 0)
        else:
            self.game.add_player(ghost_name, 'f', 0, 0)
        

# pac = Pacman("Nathan")
# pac.move()