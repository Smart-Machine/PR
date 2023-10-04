import re
import queue
import socket
import threading


class TCPParser:
    received_bytes = 1024

    def __init__(self, host, port, links):
        self.host = host
        self.port = port
        self.links = links
        self.additional_links = []

    def init_socket(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        return client_socket

    def request(self, link, data_queue):
        client_socket = self.init_socket()
        client_socket.send(f"""
            GET {link.replace("http://127.0.0.1:8089/webserver", "")} HTTP/1.1
            HOST: {self.host}:{self.port}
            User-Agent: tcp-parser
            """.strip().replace(" "*12, "").encode("utf-8")
        )
        data = client_socket.recv(self.received_bytes).decode("utf-8")
        if re.search(r'<a\shref="([^>]*)">', data):
            unscraped_links = []
            for l in re.findall(r'<a\shref="([^>]*)">', data):
                if l not in self.additional_links:
                    self.additional_links.append(l)
                    unscraped_links.append(l)
            for additional_link in unscraped_links:
                print(f"requesting: {additional_link}")
                self.request(additional_link, data_queue)
        data_queue.put(data)
        client_socket.close()

    def parse(self):
        data_queue = queue.Queue()

        thread_pool = [threading.Thread(target=self.request, args=(link, data_queue))
                       for link in self.links]
        for thread in thread_pool:
            thread.start()
            thread.join()
        
        return data_queue
