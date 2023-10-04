import re
import json
import socket
import signal
import sys
import threading

HOST = "127.0.0.1"
PORT = 8086


class WebServer:
    parallel_connection_number = 5
    received_bytes = 1024

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.static_path = "static/"
        self.template_path = "templates/"
        self.products_path = "products/"
        self.server_socket = self.init_socket()
        signal.signal(signal.SIGINT, self.signal_handler)

    def init_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return server_socket

    def signal_handler(self, sig, frame):
        print("\nShutting down the server...")
        self.server_socket.close()
        sys.exit(0)

    def request_handler(self, client_socket):
        request_data_bytes = client_socket.recv(self.received_bytes)
        request_data_text = request_data_bytes.decode("utf-8")
        print(f"Received Request Data:\n{request_data_text}")

        method = request_data_text.split("\n")[0].strip().split()[0]
        path = request_data_text.split("\n")[0].strip().split()[1]

        response_content, response_code = self.match_path(path)

        response = f"HTTP/1.1 {response_code} OK\nContent-Type: text/html\n\n{response_content}"
        client_socket.send(response.encode("utf-8"))

        client_socket.close()

    def match_path(self, path):
        if path == "/":
            return self.home_page_handler()
        elif path == "/about":
            return self.aboutus_page_handler()
        elif path == "/contact":
            return self.contact_page_handler()
        elif path == "/products":
            return self.products_page_handler()
        elif re.search(r"\/products\/pages\/page-([0-9]*).html", path):
            return self.redirect_to_page(re.search(r"\/products\/pages\/page-([0-9]*).html", path).group(1))
        elif (re.search(r"\/products\/([0-9]*)", path) and
              path == ("/products/" + re.search(r"\/products\/([0-9]*)", path).group(1))):
            return self.product_by_id_page_handler(re.search(r"\/products\/([0-9]*)", path).group(1))
        else:
            return self.notfound_page_handler()

    def home_page_handler(self):
        with open(self.static_path + "home.html", "r") as file:
            return file.read(), 200

    def aboutus_page_handler(self):
        with open(self.static_path + "about.html", "r") as file:
            return file.read(), 200

    def contact_page_handler(self):
        with open(self.static_path + "contact.html", "r") as file:
            return file.read(), 200

    def products_page_handler(self):
        self.generate_product_pages()
        with open(self.products_path + "pages/page-1.html", "r") as page:
            return page.read(), 200
        return self.notfound_page_handler()

    def redirect_to_page(self, page_number):
        with open(self.products_path + f"pages/page-{page_number}.html", "r") as page:
            return page.read(), 200
        return self.notfound_page_handler()

    def product_by_id_page_handler(self, id: str):
        products = None
        with open(self.products_path + "products.json", "r") as products_file:
            products = json.loads(products_file.read())
        for product in products:
            if product["id"] == int(id):
                with open(self.template_path + "product.tmpl", "r") as product_html:
                    return product_html.read().format(
                        product_name=product["name"],
                        product_author=product["author"],
                        product_price=product["price"],
                    ), 200
        return self.notfound_page_handler()

    def notfound_page_handler(self):
        with open(self.static_path + "notfound.html", "r") as file:
            return file.read(), 200

    def generate_product_pages(self):
        products = None
        with open(self.products_path + "products.json", "r") as products_file:
            products = json.loads(products_file.read())
        for index in range(0, len(products), 2):
            with (open(self.template_path + "products.tmpl", "r") as product_html,
                  open(self.products_path + f"pages/page-{int((index+2)/2)}.html", "w") as page):
                page.write(product_html.read().format(
                    product1_name=products[index]["name"],
                    product1_author=products[index]["author"],
                    product1_price=products[index]["price"],

                    product2_name=products[index+1]["name"],
                    product2_author=products[index+1]["author"],
                    product2_price=products[index+1]["price"],

                    links="".join(
                        f'<a href="http://{HOST}:{PORT}/{self.products_path}pages/page-{i}.html">{i}</a>'
                        for i in range(1, int(len(products)/2)+1)),
                ))

    def start(self):
        self.server_socket.listen(self.parallel_connection_number)
        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(
                f"Accepted connection from {client_address[0]}:{client_address[1]}")

            client_handler = threading.Thread(
                target=self.request_handler, args=(client_socket,))
            client_handler.start()


if __name__ == "__main__":
    webserver = WebServer(HOST, PORT)
    webserver.start()
