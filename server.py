from Game import Game

import socket

game = Game()

s = socket.socket()          # Create a socket object
host = socket.gethostname()  # Get local machine name
port = 12345                 # Reserve a port for your service.
s.bind((host, port))         # Bind to the port

s.listen(1)                  # Now wait for client connection.

c, addr = s.accept()     # Establish connection with client.
print('Got connection from', addr)

game.set_socket(s, c)

game.play()