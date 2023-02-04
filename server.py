from enum import Enum
import socket
import sys
import threading
import os

SERVER_DATA_PATH = "server_data/"
EMPTY_DIRECTORY = "Server directory is empty!"

# PROTOCCOL TO USE: MESSAGE LENGTH | FILE

class COMMAND(Enum):
    LIST="LIST"
    PUSH="PUSH"
    DELETE="DELETE"
    OVERWRITE="OVERWRITE"
    EXIT="EXIT"

class ServerThread (threading.Thread):
    threadID: int
    name: str
    client_socket: socket.socket

    def __init__(self, threadID, name, client_socket):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.client_socket = client_socket

    def list_directory(self):
        files = os.listdir(SERVER_DATA_PATH)
        if files == []:
            # empty
            self.client_socket.send((str(len(EMPTY_DIRECTORY)) + "|" + EMPTY_DIRECTORY).encode())
        else:
            # handle files list
            pass
            self.client_socket.send((str(len(EMPTY_DIRECTORY)) + "|" + EMPTY_DIRECTORY).encode())
        return EMPTY_DIRECTORY

    def run(self):
        print ("Connection from : ", self.name)
        msg = ''
        while True:

            data = self.client_socket.recv(16)
            decoded_message = data.decode()
            parsed_decode_message = decoded_message.split("|")
            print("from client, parsed:{}".format(parsed_decode_message))

            if parsed_decode_message[1] == COMMAND.LIST.value:
                self.list_directory()
            else:
                amount_expected = int(parsed_decode_message[0])
                amount_received = len(parsed_decode_message[1])
                full_message = parsed_decode_message[1]

                while amount_received < amount_expected:
                    data = self.client_socket.recv(16)
                    full_message += data.decode()
                    amount_received += len(data)
                
                print("full message ", full_message)
                self.client_socket.send((str(len(full_message)) + "|" + full_message).encode())

                if full_message == COMMAND.EXIT.value:
                    break
        print('we are closing connection to client {}'.format(self.name))
        self.client_socket.close()

class Server:

    server_name: str
    server_port: int
    threadID: int
    server_socket: socket.socket

    def __init__(self, server_name, server_port) -> None:
        self.server_name = server_name
        self.server_port = server_port
        self.threadID = 0

    def run_server(self):
        # Create a TCP/IP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('[STARTING] Server is starting...')
        self.server_socket.bind((self.server_name, self.server_port))

        # Listen for incoming connections
        self.server_socket.listen(10)
        print('[LISTENING] Server is listening...')

        while True:
            connection, client_address = self.server_socket.accept()
            print('[NEW CONNECTION] ({}, {}) connected.\n'.format(client_address, self.server_port))

            self.threadID += 1
            thr = ServerThread(self.threadID, 'thread-{}-{}'.format(self.threadID, client_address), connection)
            thr.start()


server = Server('localhost', 3000)
server.run_server()
