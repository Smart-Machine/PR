import os
import sys
import logging
from dotenv import load_dotenv
from client import Client

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    if load_dotenv():
        logging.info("Successfully loaded .env file")
    else:
        logging.info("Failed loading .env file")
        sys.exit(1)

    client = Client(os.getenv("CLIENT_ADDRESS"), int(os.getenv("CLIENT_PORT")))
    client.start()
