import logging
import threading
import sys
import socket
import time
import json

from os.path import abspath, dirname

# Add the parent directory to the Python path
sys.path.append(abspath(dirname(__file__)) + '/..')

# Import the specific function from the module
from communication.client_communication import ClientCommunication

logging.basicConfig(filename='../communication/client.log', encoding='utf-8', level=logging.DEBUG)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Comando errado. Apresente o ip, o numero da porta e o protocolo como argumentos.")
        sys.exit(1)

    client_port = int(sys.argv[1])
    server_ip = sys.argv[2]
    server_port = int(sys.argv[3])
    protocol = sys.argv[4]

    logging.info(f'Starting client on port {client_port}. It is connecting to {server_ip}:{server_port} using {protocol}')

    server_communication = ClientCommunication(server_ip, server_port, protocol)
    if not server_communication.connect_to_server():
        logging.error("Could not connect to server")
        print("Could not connect to server")
        sys.exit(1)
    
    logging.info("Connected to server")

    state = 'NOT_LOGGED_IN'

    while True:
        line = input("Pac-Man> ")
        logging.debug(state)
        commands = line.split(" ")

        if len(commands) > 0:
            if commands[0] == 'tchau':
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
                state = 'IN_GAME'
                pass
            elif commands[0] == 'desafio':
                if len(commands) != 2:
                    print("Comando errado. Apresente o usuario como argumento.")
                else:
                    user = commands[1]
                    # TODO: implementar challenge
                    # challenge_ok, challenge_error = server_communication.challenge(user)
                    # if challenge_ok:
                    #     print("Desafio enviado com sucesso")
                    # else:
                    #     print(challenge_error)
        elif state == 'IN_GAME':
            pass
        else:
            print("Unknown state")

