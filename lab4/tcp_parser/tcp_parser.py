import bs4
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
        self.data_queue = queue.Queue()
        self.pages_path = "tcp_parser/pages"

    def init_socket(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        return client_socket

    def request(self, link):
        client_socket = self.init_socket()
        client_socket.send(f"""
            GET {link.replace(f"http://{self.host}:{self.port}/webserver", "")} HTTP/1.1
            HOST: {self.host}:{self.port}
            User-Agent: tcp-parser
            """.strip().replace(" "*12, "").encode("utf-8")
        )
        html = client_socket.recv(self.received_bytes).decode("utf-8")
        data, links = self.parse(html)
        if data:
            self.data_queue.put(data)
        for l in links:
            self.request(l)
        client_socket.close()

    def parse(self, html):
        soup = bs4.BeautifulSoup(html, "html.parser")

        data = [{
            "name": name,
            "author": author,
            "price": price,
        } for name, author, price in zip(soup.select("h2.name"), soup.select("h4.author"), soup.select("h4.price"))]

        unscraped_links = []
        for l in soup.find_all("a"):
            if l.get("href") not in self.additional_links:
                self.additional_links.append(l.get("href"))
                unscraped_links.append(l.get("href"))
        if not soup.find_all("a"):
            with open(f"{self.pages_path}/{soup.title.string}.html", "w") as page:
                page.write(html.replace("HTTP/1.1 200 OK\nContent-Type: text/html\n\n", ""))

        return data, unscraped_links

    def scrape(self):
        thread_pool = [threading.Thread(target=self.request, args=(link,))
                       for link in self.links]
        for thread in thread_pool:
            thread.start()
            thread.join()

        return self.data_queue
