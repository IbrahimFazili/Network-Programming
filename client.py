from enum import Enum
import socket
import sys

class COMMAND(Enum):
    LIST="LIST"
    PUSH="PUSH"
    DELETE="DELETE"
    OVERWRITE="OVERWRITE"
    EXIT="EXIT"

class Client:

    client_socket: socket.socket
    server_name: str
    server_port: int

    def __init__(self, server_name, server_port) -> None:
        self.server_name = server_name
        self.server_port = server_port

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_name, self.server_port))
        print('Welcome to the File Server!\n')

        try:
            while True:
                inpu = input("Enter something")
                # Send data
                print('sending {!r}'.format(inpu))
                self.client_socket.sendall(inpu.encode())

                # Look for the response
                amount_received = 0
                amount_expected = len(inpu)

                while amount_received < amount_expected:
                    data = self.client_socket.recv(16)
                    amount_received += len(data)
                    print('received {!r}'.format(data))

                if inpu == "bye":
                    break

        finally:
            print('closing socket to server')
            self.client_socket.close()

client = Client('localhost', 3000)
client.connect_to_server()