from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import socket
import json

from threading import Thread



BASE_DIR = pathlib.Path()


class MainServer(BaseHTTPRequestHandler):

    def do_GET(self):
        return self.router()
    

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        self.save_data_to_json(data)
        self.client(data.decode())
        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()


    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())
    

    def send_static(self, file):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header('Content-type', mt[0])
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(file, 'rb') as fd:  # ./assets/js/app.js
            self.wfile.write(fd.read())

    
    def router(self):
        pr_url = urllib.parse.urlparse(self.path)

        match pr_url.path:
            case '/':
                self.send_html_file('front-init\index.html')
            case '/message.html':
                self.send_html_file('front-init\message.html')
            case _:
                file = BASE_DIR.joinpath(pr_url.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html_file('front-init\error.html', 404)
      

    def client(self, message):
        host = socket.gethostname()
        port = 5000

        client_socket = socket.socket()
        client_socket.connect((host, port))

        while message.lower():
            client_socket.send(message.encode())
            data = client_socket.recv(1024).decode()
            print(f'received message: {data}')

        client_socket.close()

    
    def save_data_to_json(self, data):
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_parse = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        with open(BASE_DIR.joinpath('front-init\storage\data.json'), 'a', encoding='utf-8') as fd:
            json.dump(data_parse, fd, ensure_ascii=False)



def server_socket():
    print("start server")
    host = socket.gethostname()
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(2)
    conn, address = server_socket.accept()
    print(f'Connection from {address}')
    while True:
        data = conn.recv(100).decode()

        if not data:
            break
            
    conn.close()


def run(server_class=HTTPServer, handler_class=MainServer):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        server = Thread(target=server_socket)
        server.start()
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
