import logging
import threading
import sys
import socket
import time
import asyncio
import random
import os

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind(('127.0.0.1', 1235))
tcp_socket.listen()

lista = []

class teste:
    def __init__(self, l):
        self.l = l
        self.l.append(1)
        print (self.l)

teste  (lista)
print (lista)