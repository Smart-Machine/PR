import os
import sys
import json
import base64
import socket
import signal
import logging
import threading 

class Client():

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.received_bytes = 4096  
        self.client_socket = self.init_socket()
        self.uuid = None
        self.name = None
        self.room = None
        self.media_path = "client/media/"

        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def init_socket(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return client_socket

    def signal_handler(self, sig, frame):
        logging.info("Closing connection...")
        self.client_socket.close()
        sys.exit(0)

    def get_name(self):
        self.name = input("Enter name: ")
        while not self.name:
            self.name = input("Enter name: ")
    
    def get_room(self):
        self.room = input("Enter room: ")
        while not self.room:
            self.room = input("Enter room: ")

    def connect_to_server(self):
        self.client_socket.connect((self.host, self.port))

        request_string = json.dumps({
            "type": "connect",
            "payload": {
                "name": self.name,
                "room": self.room,
            }
        })
        self.client_socket.send(request_string.encode("utf-8"))

        response_string = self.client_socket.recv(self.received_bytes).decode("utf-8")
        if not response_string:
            logging.info("Failed while connecting to the server")
            sys.exit(1)

        response_json = json.loads(response_string)
        if response_json.get("type") == "connect_ack":
            uuid = response_json.get("payload").get("uuid")
            message = response_json.get("payload").get("message") 

            if message == "Connected to the room":
                logging.info(f"Connected to {self.host}:{self.port}")
                return uuid 

    def receive_message(self):
        while True:
            response_string = self.client_socket.recv(self.received_bytes).decode("utf-8")
            if not response_string:
                return

            response_json = json.loads(response_string)
            if response_json.get("type") == "message":
                sender = response_json.get('payload').get('sender')
                text = response_json.get('payload').get('text')
                logging.info(f"{sender}: {text}")
            elif response_json.get("type") == "notification":
                message = response_json.get("payload").get("message")
                logging.info(message)

    def handle_command(self, command):
        parsed_command = command.split(" ")

        cmd = None
        arg = None
        if len(parsed_command) == 1:
            cmd = parsed_command[0]
        elif len(parsed_command) == 2:
            cmd, arg = parsed_command
        else:
            logging.info("Invalid command")
        
        if cmd == "/exit":
            self.signal_handler(None, None) 

        if cmd == "/?" or cmd == "/help":
            logging.info("""\n
                * /upload <path to file>
                * /download <filename>
            """.replace(" "*16, "\t"))
            return

        if cmd == "/upload" and arg:
            try: 
                with open(arg, "rb") as fp:
                    self.upload_file(os.path.basename(fp.name), fp.read())
                logging.info(f"Successfully uploaded {arg} file")
            except FileNotFoundError:
                logging.info(f"File {arg} doesn't exist")
            return

        if cmd == "/download" and arg:
            file_bytes = self.download_file(arg)
            if not file_bytes:
                logging.info(f"File {arg} doesn't exist")
            else:
                try:
                    with open(self.media_path + arg, "wb") as fp:
                        fp.write(file_bytes)
                    logging.info(f"Successfully downloaded {arg} file")
                except Exception as e:
                    logging.info(f"Error while downloading file {arg}")
                    logging.info(e)
            return
        
        if not arg and cmd:
            logging.info(f"Provide arguments for the {cmd} command")
            return
    
    def upload_file(self, filename, file_bytes):
        request_string = json.dumps({
            "type": "upload",
            "payload": {
                "uuid": self.uuid,
                "sender": self.name,
                "room": self.room,
                "filename": filename, 
                "file": str(base64.b64encode(file_bytes), "utf-8"),
            }
        })
        self.client_socket.send(request_string.encode("utf-8"))

    def download_file(self, filename):
        request_string = json.dumps({
            "type": "download",
            "payload": {
                "uuid": self.uuid,
                "filename": filename,
            }
        })
        self.client_socket.send(request_string.encode("utf-8"))
        print("sending")

        response_string = self.client_socket.recv(self.received_bytes).decode("utf-8")
        logging.info(f"Response: {response_string}")
        if not response_string:
            return

        response_json = json.loads(response_string)
        if response_json.get("type") == "download":
            return base64.b64decode(response_json.get("payload").get("file"))

    def send_message(self, message):
        request_string = json.dumps({
            "type": "message",
            "payload": {
                "uuid": self.uuid,
                "sender": self.name,
                "room": self.room,
                "text": message,
            }
        })
        self.client_socket.send(request_string.encode("utf-8"))
    
    def start(self):
        self.get_name()
        self.get_room()

        self.uuid = self.connect_to_server()

        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.daemon = True
        receive_thread.start()

        print("Enter a message ('/exit' to quit or '/help' | '/?' for help):")
        while True:
            message = input()
            if message and message[0] == "/":
                self.handle_command(message) 
            else:
                self.send_message(message)
 

