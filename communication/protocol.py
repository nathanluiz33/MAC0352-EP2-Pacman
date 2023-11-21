class Protocol:
    def __init__ (self, protocol, this_socket, otherside_address=None):
        self.protocol = protocol
        self.this_socket = this_socket
        self.otherside_address = otherside_address
    
    def send_message (self, message):
        if self.protocol == 'TCP':
            self.this_socket.sendall(message.encode('ascii'))
        else:
            self.this_socket.sendto(message.encode('ascii'), self.otherside_address)

    def receive_message (self):
        if self.protocol == 'TCP':
            return self.this_socket.recv(1024)
        else:
            return self.this_socket.recvfrom(1024)[0]
        
    def change_address (self, otherside_address):
        self.otherside_address = (otherside_address[0], otherside_address[1])