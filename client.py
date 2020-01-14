from Team import Team
import warnings, random
from VocabList import VocabList
from Game import Game

import random, os, socket, pickle
import pygame
import tkinter
import tkinter.filedialog
import matplotlib.pyplot as plt
import pandas as pd

root = tkinter.Tk()
root.withdraw()
pygame.init()

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.

s.connect((host, port))

game = Game(spymaster=True)

while True:
	board = s.recv(700)
	board = pickle.loads(board)

	if not board:
		exit()

	game.set_simple_board(board)
	game.draw_board()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:  # Usually wise to be able to close your program.
			raise SystemExit
