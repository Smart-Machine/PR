from webserver import WebServer

HOST = "127.0.0.1"
PORT = 8089

webserver = WebServer(HOST, PORT)
webserver.start()
