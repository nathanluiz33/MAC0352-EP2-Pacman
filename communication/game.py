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
        logging.debug (f"Adding incoming player: {username}, {host}, {port}")
        self.incoming_players.append([username, host, port])

    def start_game (self):
        while True:
            for player in self.game.players:
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
            self.flush_incoming_players()
    
    def flush_incoming_players (self):
        # TODO: add mutex
        print ("OI")
        for player in self.incoming_players:
            print ("flushando")
            self.connect_to_player(player[0], player[1], player[2])
        self.incoming_players = []

    def connect_to_player (self, username, host, port):
        # inicializamos um socket que conectar com os ghosts
        print (host, port)
        ghost_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ghost_socket.connect ((host, port))

        self.players_sockets[username] = ghost_socket
        print (f"Connected to {username} on {host}:{port}")

        message = "teste"
        ghost_socket.sendall(message.encode('ascii'))

        # if len(self.players) == 1:
        #     self.game.add_player(username, 'F', 0, 0)
        # else:
        #     self.game.add_player(username, 'f', 0, 0)

    def end_game (self):
        pass

class Ghost ():
    def __init__ (self, ghost_name, pacman_ip, pacman_port, ghost_port):
        logging.debug (f"Ghost {ghost_name} connecting to {pacman_ip}:{pacman_port} asking to connect on port {ghost_port}")
        self.game = None
        self.ghost_name = ghost_name

        # inicializamos um socket que se conecta com pacman_ip e pacman_port
        pacman_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pacman_socket.connect((pacman_ip, pacman_port))
        pacman_socket.sendall(json.dumps({'username': ghost_name, 'host': '127.0.0.1', 'port': ghost_port}).encode('ascii'))

        self.ghost_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ghost_socket.bind(('127.0.0.1', ghost_port))
        self.ghost_socket.listen()

        self.start_game()


    def start_game (self):
        logging.info (f"Waiting for {self.ghost_name} move on {self.ghost_socket.getsockname()}")

        print ("Waiting for connection")
        back_socket, _ = self.ghost_socket.accept()
        print ("Accepted")
        recv = back_socket.recv(1024)
        recv = recv.decode('ascii')
        print (recv)
        # while True:
        #     recv = self.ghost_socket.recv(1024)
        #     recv = recv.decode('ascii')

        #     recv = json.loads(recv)
        #     if recv['type'] == 'request_command' and recv['status'] == 'try':
        #         line = input("Ghost> ")
        #         line = line.split()

        #         if line[0] == 'move':
        #             pass

    

        

# pac = Pacman("Nathan")
# pac.move()