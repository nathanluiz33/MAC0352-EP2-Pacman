import logging
import threading
import sys
import socket
import time
import json
import random

logging.basicConfig(filename='../communication/client.log', encoding='utf-8', level=logging.INFO)

class Game:
    def __init__ (self, username_host):
        self.winner = username_host
        self.username_host = username_host
        self.players = []
        self.player = {}
        self.score = 0

        board = ['******.**... .....**.******', '******.**.*******.**.******', '******.**.*.. ..*.**.******', '..... ....*.....*..........', '******.**.*.. ..*.**.******']
        
        self.coded_board = []
        self.board = []
        for i in range (len(board)):
            self.coded_board.append([])
            self.board.append([])

            for j in range (len(board[i])):
                self.board[i].append(board[i][j])

                if board[i][j] == '*':
                    self.coded_board[i].append(['*'])
                elif board[i][j] == '.':
                    self.coded_board[i].append(['.'])
                else:
                    self.coded_board[i].append([])
        self.add_player(username_host, 'C', 2, 13)
        self.add_player("local_ghost", 'F', 3, 24)

    def update_board (self):
        for i in range (len(self.coded_board)):
            for j in range (len(self.coded_board[i])):
                has_dot = '.' in self.coded_board[i][j]
                has_ghost_F = 'F' in self.coded_board[i][j]
                has_ghost_f = 'f' in self.coded_board[i][j]
                has_ghost = has_ghost_F or has_ghost_f

                has_pacman = 'C' in self.coded_board[i][j]

                if has_pacman:
                    if has_dot:
                        self.score += 1
                        self.coded_board[i][j].remove('.')
                    if has_ghost:
                        self.winner = 'local_ghost'
                        for player in self.players:
                            if player != 'local_ghost' and player != self.username_host:
                                self.winner = player
                        return True
                    self.board[i][j] = 'C'
                elif has_ghost_F and has_ghost_f:
                    self.board[i][j] = 'H'
                elif has_ghost_F:
                    self.board[i][j] = 'F'
                elif has_ghost_f:
                    self.board[i][j] = 'f'
                elif has_dot:
                    self.board[i][j] = '.'
                elif self.board[i][j] != '*':
                    self.board[i][j] = ' '

    def add_player (self, username, symbol, y, x):
        logging.debug (f"Adding player: {username}, {symbol}, {x}, {y}")
        self.players.insert (0, username)
        self.player[username] = {"username": username, 'symbol': symbol, 'x': x, 'y': y}
        self.coded_board[y][x].append(symbol)

    def move (self, username, direction):
        dx = 0
        dy = 0
        if direction == 'a':
            dx = -1
        elif direction == 'd':
            dx = 1
        elif direction == 'w':
            dy = -1
        elif direction == 's':
            dy = 1

        x = self.player[username]['x'] + dx
        y = self.player[username]['y'] + dy

        x = (x + len(self.board[0])) % len(self.board[0])
        y = (y + len(self.board)) % len(self.board)

        if self.board[y][x] == '*':
            return False
        else:
            user_symbol = self.player[username]['symbol']
            user_x = self.player[username]['x']
            user_y = self.player[username]['y']
            self.coded_board[user_y][user_x].remove(user_symbol)

            self.player[username]['x'] = x
            self.player[username]['y'] = y
            user_x = x
            user_y = y
            self.coded_board[user_y][user_x].append(user_symbol)
            return True

class Pacman ():
    def __init__ (self, host_name):
        self.game = Game(host_name)
        # e um socket que vai ficar escutando por players
        self.players_sockets = {}
        self.turn = []
        self.incoming_players = []
        self.game_ended = False

    def add_incoming_player (self, username, host, port):
        logging.debug (f"Adding incoming player: {username}, {host}, {port}")
        self.incoming_players.append([username, host, port])

    def measure_latency (self):
        for player in self.game.players:
            if player != 'local_ghost' and player != self.game.username_host:
                ans = []
                for i in range (3):
                    data = {'type': 'ping'}
                    message = json.dumps(data)
                    time_in = time.time ()
                    self.players_sockets[player].sendall(message.encode('ascii'))
                    self.players_sockets[player].recv(1024)
                    time_out = time.time ()
                    ans.append (time_out - time_in)
                return ans
        return None

    def start_game (self):
        continue_game = True
        while continue_game:
            for user in self.game.players:
                # updating boards
                if not continue_game:
                    break
                
                if self.game.update_board():
                    continue_game = False
                    print ("Game over")
                    break
                for user_ in self.game.players:
                    if user_ != self.game.username_host:
                        if user_ == 'local_ghost':
                            continue
                        data = {'type': 'update_board', 'status': 'ok', 'board': self.game.board}
                        message = json.dumps(data)
                        logging.debug(f"Sending message to {user_}: {message}")
                        self.players_sockets[user_].sendall(message.encode('ascii'))

                        recv = self.players_sockets[user_].recv(1024)
                        recv = recv.decode('ascii')
                        logging.debug(f"Received data from {user_}: {recv}")
                    else:
                        print ("---------------------------")
                        for line in self.game.board:
                            for char in line:
                                print (char, end='')
                            print ()
                time.sleep(0.1)
                        
                player = self.game.player[user]
                if player['symbol'] == 'C':
                    while True:
                        line = input("Pac-Man> ")
                        line = line.split()

                        if line[0] == 'move':
                            if len(line) != 2:
                                print("Comando invalido")
                                continue
                            dir = line[1]
                            self.game.move(user, dir)
                            break
                        elif line[0] == 'encerra':
                            continue_game = False
                            break
                        elif line[0] == 'atraso':
                            print (self.measure_latency())
                        else:
                            print("Comando invalido")
                elif player['symbol'] == 'F':
                    rand = random.randint(0, 7)
                    if rand <= 2:
                        self.game.move(user, 'a')
                    elif rand == 3:
                        self.game.move(user, 'd')
                    elif rand == 4:
                        self.game.move(user, 'w')
                    else:
                        self.game.move(user, 's')
                else:
                    while True:
                        data = {'type': 'request_command', 'status': 'try'}
                        message = json.dumps(data)
                        logging.debug(f"Sending message to ghost: {message}")
                        self.players_sockets[user].sendall(message.encode('ascii'))

                        recv = self.players_sockets[user].recv(1024)
                        recv = recv.decode('ascii')
                        logging.debug(f"Received data from ghost: {recv}")

                        recv = json.loads(recv)
                        if recv['type'] == 'send_command' and recv['status'] == 'ok':
                            command = recv['command']

                            if command == 'move':
                                dir = recv['direction']
                                self.game.move(user, dir)
                                break
                            elif command == 'encerra':
                                continue_game = False
                                print ("Game ended")
                                break
                            elif command == 'atraso':
                                data = {'type': 'atraso', 'status': 'ok', 'atraso': self.measure_latency()}
                                message = json.dumps(data)
                                logging.debug(f"Sending message to ghost: {message}")
                                self.players_sockets[user].sendall(message.encode('ascii'))

                                recv = self.players_sockets[user].recv(1024)
                                recv = recv.decode('ascii')
                                logging.debug(f"Received data from ghost: {recv}")
                            else:
                                print("Comando invalido")
                        else:
                            print("Algo deu errado")

            time.sleep(1)
            self.flush_incoming_players()

        self.flush_incoming_players()
        self.end_game()
        self.game_ended = True
        print ("Game ended")
        self.game.players.remove('local_ghost')
        return self.game.winner, self.game.score, self.game.players
    
    def flush_incoming_players (self):
        for player in self.incoming_players:
            self.connect_to_player(player[0], player[1], player[2])
            self.game.add_player(player[0], 'f', 0, 12)
        self.incoming_players = []

    def connect_to_player (self, username, host, port):
        # inicializamos um socket que conectar com os ghosts
        ghost_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ghost_socket.connect ((host, port))

        self.players_sockets[username] = ghost_socket

    def end_game (self):
        for player in self.players_sockets:
            data = {'type': 'end_game', 'status': 'ok'}
            message = json.dumps(data)
            self.players_sockets[player].sendall(message.encode('ascii'))

class Ghost ():
    def __init__ (self, ghost_name, pacman_ip, pacman_port, ghost_port):
        logging.debug (f"Ghost {ghost_name} connecting to {pacman_ip}:{pacman_port} asking to connect on port {ghost_port}")
        self.board = []
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

        back_socket, _ = self.ghost_socket.accept()

        while True:
            recv = back_socket.recv(1024)
            recv = recv.decode('ascii')
            logging.debug(f"Received data from {self.ghost_name}: {recv}")
            recv = json.loads(recv)

            if recv['type'] == 'request_command' and recv['status'] == 'try':
                line = input("Ghost> ")
                line = line.split()

                if line[0] == 'move':
                    if len(line) != 2:
                        print("Comando invalido")
                        back_socket.sendall(json.dumps({'type': 'send_command', 'status': 'error: invalid command'}).encode('ascii'))
                    else:
                        back_socket.sendall(json.dumps({'type': 'send_command', 'status': 'ok', 'command': 'move', 'direction': line[1]}).encode('ascii'))
                elif line[0] == 'encerra':
                    back_socket.sendall(json.dumps({'type': 'send_command', 'status': 'ok', 'command': 'encerra'}).encode('ascii'))
                elif line[0] == 'atraso':
                    back_socket.sendall(json.dumps({'type': 'send_command', 'status': 'ok', 'command': 'atraso'}).encode('ascii'))
                else:
                    back_socket.sendall(json.dumps({'type': 'send_command', 'status': 'error: invalid command'}).encode('ascii'))
            elif recv['type'] == 'end_game' and recv['status'] == 'ok':
                print ("Game ended")
                break
            elif recv['type'] == 'ping':
                back_socket.sendall(json.dumps({'type': 'ping'}).encode('ascii'))
            elif recv['type'] == 'atraso' and recv['status'] == 'ok':
                print (recv['atraso'])
                back_socket.sendall(json.dumps({'type': 'atraso', 'status': 'ok'}).encode('ascii'))
            elif recv['type'] == 'update_board' and recv['status'] == 'ok':
                self.board = recv['board']
                print ("---------------------------")
                for line in self.board:
                    for char in line:
                        print (char, end='')
                    print ()
                back_socket.sendall(json.dumps({'type': 'update_board', 'status': 'ok'}).encode('ascii'))