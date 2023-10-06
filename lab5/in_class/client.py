import json
import sys
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
            if response_json.get("type") == "notification":
                message = response_json.get("payload").get("message")
                logging.info(message)

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

        print("Enter a message (or 'exit' to quit):")
        while True:
            message = input()
            if message.lower() == "exit":
                break
            self.send_message(message)
 

if __name__=="__main__":
    client = Client("127.0.0.1", 8089)
    client.start()
