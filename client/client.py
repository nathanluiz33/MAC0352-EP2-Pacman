import logging
import threading
import sys
import socket
import time
import json
import os

from os.path import abspath, dirname

# Add the parent directory to the Python path
sys.path.append(abspath(dirname(__file__)) + '/..')

# Import the specific function from the module
from communication.client_communication import ClientCommunication
from communication.game import Game
from communication.protocol import get_open_port
from communication.game import Pacman
from communication.game import Ghost

logging.basicConfig(filename='../communication/client.log', encoding='utf-8', level=logging.DEBUG)

def receive_players (listen_port, pacman):
    # inicializamos um socket que ira ouvir quem entra na sala
    logging.debug (f"TCP Server listening on 127.0.0.1:{listen_port}")
    while True:
        try:
            ghost_socket, ghost_address = receive_players_socket.accept()
            if pacman.game_ended:
                break

            recv_data = ghost_socket.recv(1024)
            recv_data = recv_data.decode('ascii')
            recv_data = json.loads(recv_data)
            logging.debug (f"Received data from {ghost_address}: {recv_data}")

            ghost_socket.close()

            ghost_name = recv_data['username']
            ghost_port = recv_data['port']

            pacman.add_incoming_player(ghost_name, ghost_address[0], ghost_port)
        except:
            break




if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Comando errado. Apresente o ip, o numero da porta e o protocolo como argumentos.")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    protocol = sys.argv[3]

    logging.info(f'Starting client. It is connecting to {server_ip}:{server_port} using {protocol}')

    server_communication = ClientCommunication(server_ip, server_port, protocol)
    if not server_communication.connect_to_server():
        logging.error("Could not connect to server")
        print("Could not connect to server")
        sys.exit(1)
    
    logging.info("Connected to server")

    state = 'NOT_LOGGED_IN'
    cur_username = None
    game = None
    pacman = None
    ghost = None

    while True:
        line = input("Pac-Man> ")
        logging.debug(state)
        commands = line.split(" ")

        if len(commands) > 0:
            if commands[0] == 'tchau':
                server_communication.tchau()
                
                print("Saindo do jogo")
                sys.exit(0)

        if state == 'NOT_LOGGED_IN':
            if commands[0] == 'novo':
                if len(commands) != 3:
                    print("Comando errado. Apresente o usuario e a senha como argumentos.")
                else:
                    username = commands[1]
                    password = commands[2]
                    create_user_ok, create_user_error = server_communication.create_user(username, password)
                    if create_user_ok:
                        print("Usuario criado com sucesso")
                    else:
                        print (create_user_error)
            elif commands[0] == 'entra':
                if len(commands) != 3:
                    print("Comando errado. Apresente o usuario e a senha como argumentos.")
                else:
                    username = commands[1]
                    password = commands[2]

                    login_ok, login_error = server_communication.login(username, password)
                    if login_ok:
                        cur_username = username
                        print("Login realizado com sucesso")
                        state = 'LOGGED_IN'
                    else:
                        print (login_error)
            else:
                print("Comando errado, faca login ou crie uma conta.")
        elif state == 'LOGGED_IN':
            if commands[0] == 'senha':
                if len(commands) != 3:
                    print("Comando errado. Apresente a senha atual e a nova senha como argumentos.")
                else:
                    old_password = commands[1]
                    new_password = commands[2]
                    change_password_ok, change_password_error = server_communication.change_password(old_password, new_password)
                    if change_password_ok:
                        print("Senha alterada com sucesso")
                    else:
                        print (change_password_error)
            elif commands[0] == 'sai':
                if server_communication.logout():
                    print("Logout realizado com sucesso")
                    username = None
                    state = 'NOT_LOGGED_IN'
                else:
                    print("Ocorreu um erro ao realizar o logout")
            elif commands[0] == 'lideres':
                leaderboard = server_communication.get_leaderboard()
                if leaderboard == None:
                    print("Ocorreu um erro ao buscar o leaderboard")
                else:
                    sorted_leaderboard = []
                    for user in leaderboard:
                        sorted_leaderboard.append((int(leaderboard[user]), user))
                    sorted_leaderboard.sort(reverse=True)
                    print("Leaderboard:")
                    for score, user in sorted_leaderboard:
                        print(f"{user}: {score}")
            elif commands[0] == 'inicia':
                server_communication.change_status(cur_username, 'In-game')

                game = Game (cur_username)

                listen_port = get_open_port()
                server_communication.start_game(server_communication.general_socket.this_socket.getsockname ()[0], listen_port)
                pacman = Pacman(cur_username)

                receive_players_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                receive_players_socket.bind(('127.0.0.1', listen_port))
                receive_players_socket.listen()

                threading.Thread(target=receive_players, args=(receive_players_socket, pacman)).start()
                pacman.start_game()

                # precisamos mandar a pontuacao para o servidor
                server_communication.send_score(cur_username, pacman.game.score)
                server_communication.change_status(cur_username, 'Online')
                receive_players_socket.close()

            elif commands[0] == 'desafio':
                if len(commands) != 2:
                    print("Comando errado. Apresente o usuario como argumento.")
                else:
                    user = commands[1]

                    pacman_host, error = server_communication.challenge(user)
                    if pacman_host == None:
                        print(error)
                    else:
                        print("Desafio aceito!")
                        server_communication.change_status(cur_username, 'In-game')
                        ghost = Ghost (cur_username, pacman_host[0], pacman_host[1], get_open_port ())
                        server_communication.change_status(cur_username, 'Online')
            elif commands[0] == 'l':
                online_users = server_communication.get_online_users()
                if online_users == None:
                    print("Ocorreu um erro ao buscar os usuarios online")
                else:
                    print("Usuarios online:")
                    for user in online_users:
                        print(user, online_users[user])
            else:
                print ("Comando errado. Utilize um dos seguintes comandos:")
                print ("senha <senha_atual> <nova_senha>")
                print ("sai")
                print ("lideres")
                print ("inicia")
                print ("desafio <usuario>")
                print ("l")
        else:
            print("Unknown state")

