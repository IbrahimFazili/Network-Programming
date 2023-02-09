from enum import Enum
import socket
import sys
import time

CLIENT_DATA_PATH = "client_data/"

BUFFER_SIZE = 1024

class COMMAND(Enum):
    """
    Enum used to check the command passed in the input
    """
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

    def handle_list_response(self):
        """
        receives response from the server in the form of total bytes|file1|file2|file3...|fileN 
        waits until it receives all the data files, splits and prints it for the user
        """
        # Look for the response
        data = self.client_socket.recv(BUFFER_SIZE)
        decoded_message = data.decode()
        parsed_decode_message = decoded_message.split("|")

        amount_expected = int(parsed_decode_message[0])
        amount_received = len(parsed_decode_message[1])
        full_message = parsed_decode_message[1]

        while amount_received < amount_expected:
            data = self.client_socket.recv(BUFFER_SIZE)
            full_message += data.decode()
            amount_received += len(data)

        files = full_message.split("/")
        for file in files:
            print(file)
        print()

    def print_server_response(self):
        """
        receives response from the server in the form of total bytes|message 
        and prints for the user
        """
        data = self.client_socket.recv(BUFFER_SIZE)
        decoded_message = data.decode()
        parsed_decode_message = decoded_message.split("|")

        amount_expected = int(parsed_decode_message[0])
        amount_received = len(parsed_decode_message[1])
        full_message = parsed_decode_message[1]

        while amount_received < amount_expected:
            data = self.client_socket.recv(BUFFER_SIZE)
            full_message += data.decode()
            amount_received += len(data)
        print(full_message)
        print()

    def get_file_bytes(self, filename):
        """
        Given the filename, returns the number of bytes in the file
        Parameters
        ----------
        filename: str
        """
        file_reader = open(CLIENT_DATA_PATH + filename, "rb")
        content = file_reader.read()
        return content

    def start_client(self):
        """
        The main function that will be executed each time a client is run to connect to a server.
        First establishes a TCP connection to the server socket before handling user input
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_name, self.server_port))
        print('Welcome to the File Server!\n')

        try:
            while True:
                request_message = input("Enter something: ")
                # Send data

                split_request_message = request_message.split(" ")
                command = split_request_message[0]
                if command == COMMAND.LIST.value:
                    self.client_socket.sendall((str(len(command)) + "|" + command).encode())
                    self.handle_list_response()
                elif command == COMMAND.DELETE.value:
                    self.client_socket.sendall((str(len(command)) + "|" + command).encode())
                    time.sleep(0.5)
                    file_to_delete = split_request_message[1]
                    length_file_to_delete = len(file_to_delete)
                    self.client_socket.sendall((str(length_file_to_delete) + "|" + file_to_delete).encode())
                    self.print_server_response()
                elif command == COMMAND.PUSH.value:
                    bytes_to_send = self.get_file_bytes(split_request_message[1])
                    # total bytes|PUSH|file bytes|file_name
                    self.client_socket.sendall((str(len(command)) + "|" + command + "|" + str(len(bytes_to_send)) + "|" + split_request_message[1]).encode())
                    time.sleep(0.5)
                    self.client_socket.sendall(bytes_to_send) 
                    self.print_server_response()
                elif command == COMMAND.OVERWRITE.value:
                    file_to_overwrite = split_request_message[1]
                    length_file_to_overwrite = len(file_to_overwrite)
                    self.client_socket.sendall((str(len(command)) + "|" + command + "|" + str(length_file_to_overwrite) + "|" + file_to_overwrite).encode())
                    self.print_server_response()
                elif command == COMMAND.EXIT.value:
                    self.client_socket.sendall((str(len(command)) + "|" + command).encode())
                    break

        finally:
            self.client_socket.close()

client = Client('localhost', 3000)
client.start_client()