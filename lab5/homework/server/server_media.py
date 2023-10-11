import sys
import json
import base64
import logging
import signal
import socket 
import threading

class ServerMedia:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.media_path = "server/media/"

        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
        signal.signal(signal.SIGINT, self.signal_handler)

        self.receive_bytes = 4096 
        self.server_socket = self.init_socket() 

    def init_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        logging.info(f"Media Server is listening on {self.host}:{self.port}")
        return server_socket

    def signal_handler(self, sig, frame):
        logging.info("Shutting down the server...")
        self.server_socket.close()
        sys.exit(0)
    
    def handle_files(self, client_socket, client_address):
        while True:
            request_string = client_socket.recv(self.receive_bytes).decode("utf-8")
            if not request_string:
                break
                
            request_json = json.loads(request_string)
            if request_json.get("type") == "upload":
                sender = request_json.get("payload").get("sender")
                filename = request_json.get("payload").get("filename")
                file = request_json.get("payload").get("file")
                file_bytes = base64.b64decode(file)

                try:
                    with open(self.media_path + filename, "wb") as fp:
                        fp.write(file_bytes)
                    logging.info(f"Successfully saved {filename} from {sender}")
                except Exception as e:
                    logging.info(f"Failed at saving {filename} from {sender}")
                    logging.info(f"ERROR: {e}")
                    return

                response_string = json.dumps({
                    "type": "upload",
                    "payload": {
                        "message": "Successfully uploaded the file",
                    }
                }) 
                client_socket.send(response_string.encode("utf-8"))
            
            elif request_json.get("type") == "download":
                filename = request_json.get("payload").get("filename")
                file_bytes = None

                try:
                    with open(self.media_path + filename, "rb") as fp:
                        file_bytes = fp.read()
                    logging.info(f"Successfully read {filename} from media folder")
                except Exception as e:
                    logging.info(f"Failed at reading {filename} from media folder")
                    logging.info(f"ERROR: {e}")
                    return
                
                response_string = json.dumps({
                    "type": "download",
                    "payload": {
                        "file": str(base64.b64encode(file_bytes), "utf-8"),
                    }
                })
                client_socket.send(response_string.encode("utf-8"))

    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_files, args=(client_socket, client_address,))
            client_thread.start()
