import os
import sys
import logging
from dotenv import load_dotenv
from server import Server
from server_media import ServerMedia
from multiprocessing import Process

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    if load_dotenv():
        logging.info("Successfully loaded .env file")
    else:
        logging.info("Failed loading .env file")
        sys.exit(1)
    
    media_server = ServerMedia(os.getenv("MEDIA_SERVER_ADDRESS"), int(os.getenv("MEDIA_SERVER_PORT"))) 
    server = Server(os.getenv("SERVER_ADDRESS"), int(os.getenv("SERVER_PORT")))

    media_server_process = Process(target=media_server.start)
    server_process = Process(target=server.start)

    media_server_process.start()
    server_process.start()
