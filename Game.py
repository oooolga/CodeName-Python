from Team import Team
import warnings, random
from VocabList import VocabList

import random, os, socket, sys, pickle
import pygame
import tkinter
import tkinter.filedialog
import matplotlib.pyplot as plt
import pandas as pd

root = tkinter.Tk()
root.withdraw()
pygame.init()

## get size of an 
def sizeof(obj):
	size = sys.getsizeof(obj)
	if isinstance(obj, dict): return size + sum(map(sizeof, obj.keys())) + sum(map(sizeof, obj.values()))
	if isinstance(obj, (list, tuple, set, frozenset)): return size + sum(map(sizeof, obj))
	return size

class Game:

	KEYS = ('PROPERTY', 'BOOL_GUESS', 'WORD')
	PROPERTIES = ('BLUE', 'RED', 'BLANK', 'MINE')
	TEAMS = ('BLUE', 'RED')

	PROPERTY_COLOR_DICT = {'BLUE': "#9FE9EE",
						   'RED': "#EE9F9F",
						   'BLANK': 'W',
						   'MINE': '#DADADA'}

	VOCAB_DIR = './VocabList/'

	WHITE = (255, 255, 255)
	BLACK = (0, 0, 0)
	DARK_GREEN = (0, 128, 0)
	DARK_RED = (128, 0, 0)
	DARK_BLUE = (0, 0, 128)
	BEIGE = (255, 243, 202)
	LIGHT_GREY = (220, 220, 220)

	BLOCK_X_SIZE = 250
	BLOCK_Y_SIZE = 120
	SPACE_SIZE = 10
	SCREEN_X_SIZE = 1500
	SCREEN_Y_SIZE = 1000

	KEYS_ORDER = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
				  'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
				  'W', 'X', 'Y']
	KEYS_DICT = {'A': pygame.K_a,
				 'B': pygame.K_b,
				 'C': pygame.K_c,
				 'D': pygame.K_d,
				 'E': pygame.K_e,
				 'F': pygame.K_f,
				 'G': pygame.K_g,
				 'H': pygame.K_h,
				 'I': pygame.K_i,
				 'J': pygame.K_j,
				 'K': pygame.K_k,
				 'L': pygame.K_l,
				 'M': pygame.K_m,
				 'N': pygame.K_n,
				 'O': pygame.K_o,
				 'P': pygame.K_p,
				 'Q': pygame.K_q,
				 'R': pygame.K_r,
				 'S': pygame.K_s,
				 'T': pygame.K_t,
				 'U': pygame.K_u,
				 'V': pygame.K_v,
				 'W': pygame.K_w,
				 'X': pygame.K_x,
				 'Y': pygame.K_y}

	KEY_LABEL_FONT = pygame.font.Font('freesansbold.ttf', 18)
	SCORE_FONT = pygame.font.Font('freesansbold.ttf', 32)
	WORD_FONT = pygame.font.Font('../fonts/NotoSerifSC-Bold.otf', 28)
	HINT_FONT = pygame.font.Font('../fonts/MaShanZheng-Regular.ttf', 30)
	HELP_FONT = pygame.font.Font('freesansbold.ttf', 18)

	def __init__(self, spymaster=False):

		self.team_red = Team('RED')
		self.team_blue = Team('BLUE')
		self.set_empty_board()
		self._vocab = VocabList()
		self.vocab_list = []

		## pygame display
		self.size = [Game.SCREEN_X_SIZE, Game.SCREEN_Y_SIZE]
		self.screen = pygame.display.set_mode(self.size)
		self.set_rect()
		self.screen.fill(Game.WHITE)
		pygame.display.set_caption("Codename")
		self.host_socket = None
		self.client_socket = None

		self.spymaster = spymaster

		self.team_dict = {'RED': self.team_red, 'BLUE': self.team_blue}

		self.round_counter = 0


	def set_socket(self, host_socket, client_socket):
		self.host_socket = host_socket
		self.client_socket = client_socket

	def add_vocab_doc_to_vocab_list(self, doc):
		success_flag = self._vocab.add_vocab_doc(doc)
		self.vocab_list = list(self._vocab.vocab_list)
		random.shuffle(self.vocab_list)
		return success_flag

	def set_empty_board(self):

		self.board = []
		self.simple_board = []

		for i in range(5):

			self.board.append([])
			self.simple_board.append([])

			for j in range(5):

				board_ij = {k:None for k in Game.KEYS}
				self.board[i].append(board_ij)
				self.simple_board[i].append(board_ij.copy())

	def reset_vocab_list(self):

		self.vocab_list = list(self._vocab.vocab_list)
		random.shuffle(self.vocab_list)

	def reset_board(self):

		if len(self.vocab_list) < 25:
			self.load_vocab(msg='Not enough words loaded.')

		#self.reset_vocab_list()

		teams = list(Game.TEAMS)
		random.shuffle(teams)
		team_words = random.sample(list(range(25)), 18)
		self.team_dict[teams[0]].set_current_word_count(9)
		self.team_dict[teams[1]].set_current_word_count(8)

		# clear board
		for i in range(5):
			for j in range(5):
				self.board[i][j]['PROPERTY'] = 'BLANK'

		for i in range(18):
			if i < 9:
				self.board[team_words[i]//5][team_words[i]%5]['PROPERTY'] = teams[0]
			elif i < 17:
				self.board[team_words[i]//5][team_words[i]%5]['PROPERTY'] = teams[1]
			else:
				self.board[team_words[i]//5][team_words[i]%5]['PROPERTY'] = 'MINE'

		for i in range(5):

			for j in range(5):

				self.board[i][j]['BOOL_GUESS'] = False
				self.board[i][j]['WORD'] = self.vocab_list.pop()

				self.simple_board[i][j]['PROPERTY'] = self.board[i][j]['PROPERTY']
				self.simple_board[i][j]['WORD'] = self.board[i][j]['WORD']
				self.simple_board[i][j]['BOOL_GUESS'] = self.board[i][j]['BOOL_GUESS']

		self.print_board_by_key('WORD')
		print('')
		self.print_board_by_key('PROPERTY')

	def plot_current_board(self):

		words_df = self.get_board_words_as_df()
		color_list = self.get_board_colors()

		fig, ax = plt.subplots()

		# hide axes
		fig.patch.set_visible(False)
		ax.axis('off')
		ax.axis('tight')

		ax.table(cellText=words_df.values, loc='center', cellColours=color_list)

		fig.tight_layout()
		plt.show()
		return

	def get_board_colors(self):

		color_list = []

		for i in range(5):

			color_list.append([])
			
			for j in range(5):

				color_list[i].append(Game.PROPERTY_COLOR_DICT[self.board[i][j]['PROPERTY']])

		return color_list

	def get_board_words_as_df(self):

		word_list = []

		for i in range(5):

			word_list.append([])
			
			for j in range(5):

				word_list[i].append(self.board[i][j]['WORD'])

		return pd.DataFrame(word_list)

	def set_simple_board(self, new_board):
		self.simple_board = new_board

		for i in range(5):
			for j in range(5):
				self.board[i][j]['PROPERTY'] = self.simple_board[i][j]['PROPERTY']
				self.board[i][j]['WORD'] = self.simple_board[i][j]['WORD']
				self.board[i][j]['BOOL_GUESS'] = self.simple_board[i][j]['BOOL_GUESS']

	def set_rect(self):

		boarder_x = (Game.SCREEN_X_SIZE - (Game.BLOCK_X_SIZE*5) - (Game.SPACE_SIZE*4))//2
		boarder_y = (Game.SCREEN_Y_SIZE - (Game.BLOCK_Y_SIZE*5) - (Game.SPACE_SIZE*4))//2

		for i in range(5):
			for j in range(5):
				rect = pygame.Rect(boarder_x+i*Game.BLOCK_X_SIZE+i*Game.SPACE_SIZE,
								   boarder_y+j*Game.BLOCK_Y_SIZE+j*Game.SPACE_SIZE,
								   Game.BLOCK_X_SIZE, Game.BLOCK_Y_SIZE)

				label = Game.KEYS_ORDER[i*5+j]
				self.board[i][j]['LABEL'] = label

				label_text = Game.KEY_LABEL_FONT.render(label, True, Game.BLACK)
				label_position = (boarder_x+i*Game.BLOCK_X_SIZE+i*Game.SPACE_SIZE,
								  boarder_y+j*Game.BLOCK_Y_SIZE+j*Game.SPACE_SIZE)

				self.board[i][j]['RECT'] = rect

				self.board[i][j]['LABEL_TEXT'] = label_text
				self.board[i][j]['LABEL_POSITION'] = label_position
				self.board[i][j]['RECT_KEY'] = Game.KEYS_DICT[label]


	def draw_board(self):

		self.screen.fill(Game.WHITE)

		if not self.spymaster:
			red_score_text = Game.SCORE_FONT.render('{}'.format(self.team_red.current_word_count), True,
													Game.DARK_RED)
			blue_score_text = Game.SCORE_FONT.render('{}'.format(self.team_blue.current_word_count), True,
													 Game.DARK_BLUE)
			score_mid_text = Game.SCORE_FONT.render('-', True, Game.BLACK)
			self.screen.blit(red_score_text, (20, 20))
			self.screen.blit(score_mid_text, (20+red_score_text.get_width()+2, 20))
			self.screen.blit(blue_score_text, (20+red_score_text.get_width()+4+score_mid_text.get_width(), 20))


		for i in range(5):
			for j in range(5):

				color = Game.LIGHT_GREY
				font_color = Game.BLACK

				if self.board[i][j]['BOOL_GUESS']:

					if self.board[i][j]['PROPERTY'] == 'BLANK':
						color = Game.BEIGE

					elif self.board[i][j]['PROPERTY'] == 'RED':
						color = Game.DARK_RED
						font_color = Game.WHITE

					elif self.board[i][j]['PROPERTY'] == 'BLUE':
						color = Game.DARK_BLUE
						font_color = Game.WHITE

					elif self.board[i][j]['PROPERTY'] == 'MINE':
						color = Game.BLACK
						font_color = Game.WHITE

				elif self.spymaster:
					if self.board[i][j]['PROPERTY'] == 'RED':
						font_color = Game.DARK_RED

					elif self.board[i][j]['PROPERTY'] == 'BLUE':
						font_color = Game.DARK_BLUE

					elif self.board[i][j]['PROPERTY'] == 'MINE':
						color = (150, 150, 150)

				pygame.draw.rect(self.screen, color, self.board[i][j]['RECT'])
				self.screen.blit(self.board[i][j]['LABEL_TEXT'],
								 self.board[i][j]['LABEL_POSITION'])
				word_text = Game.WORD_FONT.render(self.board[i][j]['WORD'], True, font_color)
				word_position = (self.board[i][j]['LABEL_POSITION'][0]+(Game.BLOCK_X_SIZE-word_text.get_width())//2,
								 self.board[i][j]['LABEL_POSITION'][1]+(Game.BLOCK_Y_SIZE-word_text.get_height())//2)
				self.screen.blit(word_text, word_position)

		## Display
		pygame.display.update()

		return


	def play(self):

		self.reset_board()
		#self.plot_current_board()

		ingame_flag = True
		status_flag = True

		while ingame_flag:

			self.draw_board()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:  # Usually wise to be able to close your program.
					msg = pickle.dumps(False)
					self.client_socket.send(msg)
					raise SystemExit
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						ingame_flag = False

					elif event.key in Game.KEYS_DICT.values():

						found = False

						for i in range(5):
							for j in range(5):

								if self.board[i][j]['RECT_KEY'] == event.key:

									status_flag = True
									self.board[i][j]['BOOL_GUESS'] = True
									self.simple_board[i][j]['BOOL_GUESS'] = True

									if self.board[i][j]['PROPERTY'] == 'MINE':
										ingame_flag = False

									if self.board[i][j]['PROPERTY'] == 'RED':
										self.team_red.decrease_current_word_count()
										if self.team_red.current_word_count == 0:
											ingame_flag = False

									if self.board[i][j]['PROPERTY'] == 'BLUE':
										self.team_blue.decrease_current_word_count()
										if self.team_blue.current_word_count == 0:
											ingame_flag = False

			if status_flag:
				msg = pickle.dumps(self.simple_board)
				self.client_socket.send(msg)

			status_flag = False

		self.round_counter += 1

		end_flag = False
		continue_flag = False
		while not end_flag:

			self.screen.fill(Game.WHITE)

			text = Game.HINT_FONT.render('Next round?', True, Game.BLACK)
			self.screen.blit(text, ((self.size[0]-text.get_width())//2, (self.size[1]-text.get_height())//2))

			output_string = 'Press [N] for next round.            Press [ESC] to end game.'
			help_text = Game.HELP_FONT.render(output_string, True, Game.BLACK)
			self.screen.blit(help_text, ((self.size[0]-help_text.get_width())//2,
										   (self.size[1]+text.get_height())//2+20))

			## Display
			pygame.display.update()

			for event in pygame.event.get():

				if event.type == pygame.QUIT:  # Usually wise to be able to close your program.
					msg = pickle.dumps(False)
					self.client_socket.send(msg)
					raise SystemExit
				elif event.type == pygame.KEYDOWN:

					if event.key == pygame.K_ESCAPE:
						msg = pickle.dumps(False)
						self.client_socket.send(msg)
						end_flag = True
					elif event.key == pygame.K_n:
						continue_flag = True
						end_flag = True

		
		if continue_flag and self.round_counter <= 25:
			self.play()

		return

	def load_vocab_list_dialog(self):

		try:
			root.filename = tkinter.filedialog.askopenfilename(initialdir = Game.VOCAB_DIR,
													   title = "Select vocabulary lists",
													   filetypes = [("Text file",'*.txt')])
			return self.add_vocab_doc_to_vocab_list(root.filename)
		except Exception:
			return False

	def load_vocab(self, msg=''):

		end_flag = False
		success_flag = False

		help_font = pygame.font.Font('freesansbold.ttf', 18)
		vocab_font = pygame.font.Font('../fonts/MaShanZheng-Regular.ttf', 48)

		msg = msg+' ' if msg else msg

		while not end_flag:

			self.screen.fill(Game.WHITE)
			text = Game.HINT_FONT.render('{}Let\'s Load!'.format(msg), True, Game.BLACK)
			self.screen.blit(text, ((self.size[0]-text.get_width())//2, (self.size[1]-text.get_height())//2))

			help_text = Game.HELP_FONT.render('Press [L] to load vocabulary list.          Press [P] to play.', True, Game.BLACK)
			self.screen.blit(help_text, ((self.size[0]-help_text.get_width())//2,
										 (self.size[1]+text.get_height())//2+20))
			help_text2 = Game.HELP_FONT.render('Number of successfully loaded vocabulary lists: {}'.format(self._vocab.get_number_of_lists()), True, Game.DARK_RED)
			self.screen.blit(help_text2, ((self.size[0]-help_text2.get_width())//2,
										 (self.size[1]+text.get_height())//2+40+help_text.get_height()))

			## Display
			pygame.display.update()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:  # Usually wise to be able to close your program.
					raise SystemExit
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_l:
						success_flag = self.load_vocab_list_dialog()
					elif event.key == pygame.K_p and self._vocab.get_number_of_lists() > 0:
						end_flag = True

	def print_board_by_key(self, key):

		for i in range(5):

			print_str = ''

			for j in range(5):

				print_str += self.board[i][j][key] + '\t\t'

			print(print_str)


if __name__ == '__main__':

	game = Game()

	s = socket.socket()          # Create a socket object
	host = socket.gethostname()  # Get local machine name
	port = 12345                 # Reserve a port for your service.
	s.bind((host, port))         # Bind to the port

	s.listen(1)                  # Now wait for client connection.

	c, addr = s.accept()     # Establish connection with client.
	print('Got connection from', addr)

	game.set_socket(s, c)

	#game.reset_board()
	game.play()

