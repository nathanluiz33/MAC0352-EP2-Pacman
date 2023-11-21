import logging
import threading
import sys
import socket
import time
import asyncio
import random

from os.path import abspath, dirname

# Add the parent directory to the Python path
sys.path.append(abspath(dirname(__file__)) + '/..')

# Import the specific function from the module
from communication.server_communication import ServerCommunication

host = '127.0.0.1'
logging.basicConfig(filename='../communication/server.log', encoding='utf-8', level=logging.DEBUG)

def handle_connection_tcp (client_socket, client_address):
    logging.info (f"New connection from {client_address}")
    client_communication = ServerCommunication('TCP', client_socket)
    client_communication.parse_client()

def tcp_server(port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((host, port))
    tcp_socket.listen()

    logging.info (f"TCP Server listening on {host}:{port}")
    while True:
        client_socket, client_address = tcp_socket.accept()

        threading.Thread(target=handle_connection_tcp, args=(client_socket, client_address), daemon=True).start()

def try_bind (client_socket, host, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.bind((host, port))
        return True
    except:
        return False

def handle_connection_udp (client_address, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    new_port = random.uniform(2000, 50000)
    while not try_bind(client_socket, host, new_port):
        new_port = int(random.uniform(2000, 50000))
    client_socket.bind((host, new_port))

    client_communication = ServerCommunication('UDP', client_socket, client_address)
    client_communication.parse_client(data)

def udp_server(port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))

    logging.info (f"UDP Server listening on {host}:{port}")
    while True:
        data, client_address = udp_socket.recvfrom(1024)
        logging.info (f"Received data from {client_address}: {data}")
        threading.Thread(target=handle_connection_udp, args=(client_address, data), daemon=True).start()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Comando errado. Apresente o numero da porta como argumento.")
        sys.exit(1)

    port = int(sys.argv[1])
    logging.info(f'Starting server on port {port}')

    tcp_thread = threading.Thread(target=tcp_server, daemon=True, args=(port,))
    udp_thread = threading.Thread(target=udp_server, daemon=True, args=(port,))

    tcp_thread.start()
    udp_thread.start()

    while True:
        pass
