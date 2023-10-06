import uuid
import json
import sys
import logging
import signal
import socket 
import threading

class Server:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port

        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
        signal.signal(signal.SIGINT, self.signal_handler)

        self.receive_bytes = 4096
        self.clients = []
        self.server_socket = self.init_socket() 

    def init_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        logging.info(f"Server is listening on {self.host}:{self.port}")
        return server_socket

    def signal_handler(self, sig, frame):
        logging.info("Shutting down the server...")
        self.server_socket.close()
        sys.exit(0)

    def is_client_connected(self, client_id):
        for client in self.clients:
            if client.get("uuid") == client_id:
                return True
        return False

    def notify_message(self, message, client_socket, room):
        for client in self.clients:
            if client.get("client_socket") != client_socket and client.get("room") == room: 
                client.get("client_socket").send(message.encode("utf-8"))

    def handle_client(self, client_socket, client_address):
        client_id = None

        while True:
            request_string = client_socket.recv(self.receive_bytes).decode("utf-8")
            if not request_string:
                break

            request_json = json.loads(request_string)
            if request_json.get("type") == "connect":
                client_id = str(uuid.uuid4())
                name = request_json.get("payload").get("name")
                room = request_json.get("payload").get("room")

                self.clients.append({
                    "uuid": client_id, 
                    "client_socket": client_socket, 
                    "client_address": client_address,
                    "name": name,
                    "room": room,
                })
                logging.info(f"Accepted connection from {name}({client_address})")

                response_string = json.dumps({
                    "type": "connect_ack",
                    "payload": {
                        "uuid": client_id,
                        "message": "Connected to the room",
                    }
                })
                client_socket.send(response_string.encode("utf-8"))

                message = json.dumps({
                    "type": "notification",
                    "payload": {
                        "message": f"{name} connected to the chat room"
                    }
                }) 
                self.notify_message(message, client_socket, room)

            elif request_json.get("type") == "message":
                client_id = request_json.get("payload").get("uuid")
                sender = request_json.get('payload').get('sender')
                room = request_json.get("payload").get("room")
                text = request_json.get("payload").get("text")

                logging.info(f"Received message from {sender}")
                if self.is_client_connected(client_id):
                    for client in self.clients:
                        if client.get("client_socket") != client_socket and client.get("room") == room:
                            response_string = json.dumps({
                                "type": "message",
                                "payload": {
                                    "sender": sender, 
                                    "text": text,
                                }
                            })
                            client.get("client_socket").send(response_string.encode("utf-8"))

        for client in self.clients:
            if client.get("client_id") == client_id:
                client.get("client_socket").close()
                self.clients.remove(client)
                return
    
    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address,))
            client_thread.start()

if __name__=="__main__":
    server = Server("127.0.0.1", 8089)
    server.start()