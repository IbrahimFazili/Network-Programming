from enum import Enum
import socket
import sys

CLIENT_DATA_PATH = "client_data/"

BUFFER_SIZE = 1024
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

    def handle_list_response(self):
        # Look for the response
        data = self.client_socket.recv(BUFFER_SIZE)
        msg = data
        decoded_message = data.decode()
        parsed_decode_message = decoded_message.split("|")
        print("from server, parsed:{}".format(parsed_decode_message))

        amount_expected = int(parsed_decode_message[0])
        amount_received = len(parsed_decode_message[1])
        full_message = parsed_decode_message[1]

        while amount_received < amount_expected:
            data = self.client_socket.recv(BUFFER_SIZE)
            full_message += data.decode()
            amount_received += len(data)
            print("full message ", full_message)

        files = full_message.split("/")
        for file in files:
            print(file)

    def handle_delete_response(self):
        data = self.client_socket.recv(BUFFER_SIZE)
        msg = data
        decoded_message = data.decode()
        parsed_decode_message = decoded_message.split("|")
        print("from server, parsed:{}".format(parsed_decode_message))

        amount_expected = int(parsed_decode_message[0])
        amount_received = len(parsed_decode_message[1])
        full_message = parsed_decode_message[1]

        while amount_received < amount_expected:
            data = self.client_socket.recv(BUFFER_SIZE)
            full_message += data.decode()
            amount_received += len(data)
        print(full_message)

    def get_file_bytes(self, filename):
        file_reader = open(CLIENT_DATA_PATH + filename, "rb")
        content = file_reader.read()
        return content

    def start_client(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_name, self.server_port))
        print('Welcome to the File Server!\n')

        try:
            while True:
                request_message = input("Enter something: ")
                length_request_message = len(request_message)
                # Send data
                print('sending {}{!r}'.format(length_request_message, request_message))

                split_request_message = request_message.split(" ")
                if split_request_message[0] == COMMAND.LIST.value:
                    self.client_socket.sendall((str(length_request_message) + "|" + request_message).encode())
                    self.handle_list_response()
                elif split_request_message[0] == COMMAND.DELETE.value:
                    self.client_socket.sendall((str(length_request_message) + "|" + request_message).encode())
                    self.handle_delete_response()
                elif split_request_message[0] == COMMAND.PUSH.value:
                    bytes_to_send = self.get_file_bytes(split_request_message[1])
                    # total bytes|PUSH filename/content
                    formatted_request = ("PUSH " + split_request_message[1] + "/").encode() + bytes_to_send
                    self.client_socket.sendall(((str(len(formatted_request)) + "|").encode() + formatted_request)) 
                else:
                    self.client_socket.sendall((str(length_request_message) + "|" + request_message).encode())
                    # Look for the response
                    data = self.client_socket.recv(BUFFER_SIZE)
                    msg = data
                    decoded_message = data.decode()
                    parsed_decode_message = decoded_message.split("|")
                    print("initial packet from server, parsed:{}".format(parsed_decode_message))

                    amount_expected = int(parsed_decode_message[0])
                    amount_received = len(parsed_decode_message[1])
                    full_message = parsed_decode_message[1]

                    while amount_received < amount_expected:
                        data = self.client_socket.recv(BUFFER_SIZE)
                        full_message += data.decode()
                        amount_received += len(data)
                
                    print("full message ", full_message)

                if request_message == COMMAND.EXIT.value:
                    break

        finally:
            self.client_socket.close()

client = Client('localhost', 3000)
client.start_client()