"""Authenticator server"""

class Authenticator:

    def __init__(self, socket):
        self.socket = socket
        self.authenticated = False