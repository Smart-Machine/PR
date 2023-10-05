from tcp_parser import TCPParser

host = "127.0.0.1"
port = 8089
links = [
    "http://127.0.0.1:8089/webserver/",
    "http://127.0.0.1:8089/webserver/about",
    "http://127.0.0.1:8089/webserver/contact",
    "http://127.0.0.1:8089/webserver/products",
]

tcp_parser = TCPParser(host, port, links)
data_queue = tcp_parser.scrape()
for data in data_queue.queue:
    print(data)