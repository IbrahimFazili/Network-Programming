import socket
import sys
import threading

class ServerThread (threading.Thread):
    threadID: int
    name: str
    client_socket: socket.socket

    def __init__(self, threadID, name, client_socket):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.client_socket = client_socket

    def handle_connection(self):
        # Receive the data in small chunks and retransmit it
        while True:
            data = self.client_socket.recv(16)
            print('received {!r}'.format(data))
            if data:
                print('sending data back to the client')
                self.client_socket.sendall(data)
            else:
                print('no data from', self.client_socket)
                break

    def run(self):
        print('threadId: {} -- name: {}'.format(self.threadID, self.name))
        self.handle_connection()

class Server:

    server_name: str
    server_port: int
    threadID: int
    server_socket: socket.socket

    def __init__(self, server_name, server_port) -> None:
        self.server_name = server_name
        self.server_port = server_port
        self.threadID = 0
        # Create a TCP/IP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run_server(self):
        print('STARTING] Server is starting...')
        self.server_socket.bind((self.server_name, self.server_port))

        # Listen for incoming connections
        self.server_socket.listen(1)
        print('[LISTENTING] Server is listening...')

        while True:
            connection, client_address = self.server_socket.accept()
            try:
                print('[NEW CONNECTION] ({}, {}) connected.\n'.format(client_address, self.server_port))

                ServerThread(self.threadID, client_address, connection).run()
                self.threadID += 1

            finally:
                # Clean up the connection
                connection.close()

server = Server('localhost', 3000)
server.run_server()
