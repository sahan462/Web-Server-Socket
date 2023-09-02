import socket

class HTTPServer:
    def __init__(self, address, directory):
        self.address = address
        self.directory = directory


    def serve_forever(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        url = ("http://localhost", 2728)

        
