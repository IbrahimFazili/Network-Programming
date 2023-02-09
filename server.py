from enum import Enum
import socket
import sys
import threading
import os

SERVER_DATA_PATH = "server_data/"
EMPTY_DIRECTORY = "Server directory is empty!"
FILE_NOT_FOUND = "File not found!"
FILE_DELETED = "The file {} deleted!"
DISCONNECT_FROM_SERVER = "Disconnected from the server!"
NOT_SUPPORTED = "This is not a supported command"
PUSH_CONFIRMATION = "Received the file {}!"
OVERWRITTEN_CONFIRMATION = "The file {} overwritten!"
OVERWRITTEN_TEXT = "Hi! You're text file has been overwritten with this sentence!"

BUFFER_SIZE = 1024
# GENERAL HEADER PROTOCCOL TO USE: LENGTH | COMMAND | FILE_LENGTH | FILE_NAME
# CONTENT PAYLOAD: FILE BYTES

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
        """
        Checks the server directory to see if there are any files when the user inputs LIST
        If there are files, it sends them as total bytes|file1|file2|file3...fileN
        Otherwise Empty directory message is sent
        """
        files = os.listdir(SERVER_DATA_PATH)
        if files == []:
            # empty
            self.client_socket.send((str(len(EMPTY_DIRECTORY)) + "|" + EMPTY_DIRECTORY).encode())
        else:
            # handle files list
            full_message = "/".join(files)
            self.client_socket.sendall((str(len(full_message)) + "|" + full_message).encode())

    def delete_file(self, file_to_delete):
        """
        Given the filename, attempts to delete that file in the server_data folder.

        Parameters
        ----------
        file_to_delete: str
        """
        files = os.listdir(SERVER_DATA_PATH)
        if files == []:
            # empty
            self.client_socket.send((str(len(EMPTY_DIRECTORY)) + "|" + EMPTY_DIRECTORY).encode())
            return
        if os.path.isfile(SERVER_DATA_PATH + file_to_delete):
            # delete file
            os.remove(SERVER_DATA_PATH + file_to_delete)
            formatted_string = FILE_DELETED.format(file_to_delete)
            self.client_socket.sendall((str(len(formatted_string)) + "|" + formatted_string).encode())
        else:
            # file doesn't exist
            self.client_socket.sendall((str(len(FILE_NOT_FOUND)) + "|" + FILE_NOT_FOUND).encode())
        
    def create_file(self, file_name:str, filecontents: bytes):
        """
        Creates the given filename in the server_data and write its content

        Parameters
        ----------
        file_name: str
        filecontents: bytes
        """
        file_writer = open(SERVER_DATA_PATH + file_name, "wb")
        file_writer.write(filecontents)
        formatted_string = PUSH_CONFIRMATION.format(file_name)
        self.client_socket.sendall((str(len(formatted_string)) + "|" + formatted_string).encode())

    def overwrite_file(self, file_to_delete):
        """
        Overwrites the given txt file with a hardcoded text value if it exists

        Parameters
        ----------
        file_to_delete:str
        """
        if os.path.isfile(SERVER_DATA_PATH + file_to_delete):
            file_writer = open(SERVER_DATA_PATH + file_to_delete, "wb")
            file_writer.write(OVERWRITTEN_TEXT.encode())
            formatted_string = OVERWRITTEN_CONFIRMATION.format(file_to_delete)
            self.client_socket.sendall((str(len(formatted_string)) + "|" + formatted_string).encode())
        else:
            self.client_socket.sendall((str(len(FILE_NOT_FOUND)) + "|" + FILE_NOT_FOUND).encode())

    def run(self):

        while True:
            # parse and receive the header protoccol to find which command has been issued
            # by the user 
            data = self.client_socket.recv(BUFFER_SIZE)
            decoded_message = data.decode()
            parsed_decode_message = decoded_message.split("|")
            split_parsed_decode_message = parsed_decode_message[1].split(" ")
            amount_expected = int(parsed_decode_message[0])
            amount_received = len(parsed_decode_message[1])
            full_message = parsed_decode_message[1]

            while amount_received < amount_expected:
                data = self.client_socket.recv(BUFFER_SIZE)
                full_message += data.decode()
                amount_received += len(data)

            if split_parsed_decode_message[0] == COMMAND.LIST.value:
                self.list_directory()
            elif split_parsed_decode_message[0] == COMMAND.DELETE.value:
                # receive the file
                file_data = self.client_socket.recv(BUFFER_SIZE).decode()
                parsed_file_data = file_data.split("|")
                amount_expected = int(parsed_file_data[0])
                amount_received = len(parsed_file_data[1])
                full_message_data = parsed_file_data[1]
                while amount_received < amount_expected:
                    data = self.client_socket.recv(BUFFER_SIZE)
                    full_message_data += data.decode()
                    amount_received += len(data)
                self.delete_file(full_message_data)
            elif split_parsed_decode_message[0] == COMMAND.PUSH.value:
                # receive the file
                file_data = self.client_socket.recv(BUFFER_SIZE)
                amount_expected = int(parsed_decode_message[-2])
                amount_received = len(file_data)
                full_message_data = file_data
                while amount_received < amount_expected:
                    data = self.client_socket.recv(BUFFER_SIZE)
                    full_message_data += data
                    amount_received += len(data)
                self.create_file(parsed_decode_message[-1], full_message_data)
            elif split_parsed_decode_message[0] == COMMAND.OVERWRITE.value:
                self.overwrite_file(parsed_decode_message[-1])
            elif split_parsed_decode_message[0] == COMMAND.EXIT.value:
                self.client_socket.send((str(len(DISCONNECT_FROM_SERVER)) + "|" + DISCONNECT_FROM_SERVER).encode())
                break
            else:
                self.client_socket.send((str(len(NOT_SUPPORTED)) + "|" + NOT_SUPPORTED).encode())

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
            print('[NEW CONNECTION] ({}, {}) connected.\n'.format(client_address[0], client_address[1]))

            self.threadID += 1
            thr = ServerThread(self.threadID, 'thread-{}-{}'.format(self.threadID, client_address), connection)
            thr.start()


server = Server('localhost', 3000)
server.run_server()
