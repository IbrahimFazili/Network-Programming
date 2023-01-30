import socket
import sys

class Client:

    client_socket: socket.socket
    server_name: str
    server_port: int

    def __init__(self, server_name, server_port) -> None:
        self.server_name = server_name
        self.server_port = server_port

        # Create a TCP/IP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_client(self):
        self.client_socket.connect((self.server_name, self.server_port))
        print('Welcome to the File Server!\n')

        try:
            # Send data
            message = b'This is the message.  It will be repeated.'
            print('sending {!r}'.format(message))
            self.client_socket.sendall(message)

            # Look for the response
            amount_received = 0
            amount_expected = len(message)

            while amount_received < amount_expected:
                data = self.client_socket.recv(16)
                amount_received += len(data)
                print('received {!r}'.format(data))

        finally:
            self.client_socket.close()

client = Client('localhost', 3000)
client.start_client()