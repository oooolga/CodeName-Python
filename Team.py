class Team:

	def __init__(self, name):
		self.name = name
		self.current_word_count = 0

	def set_current_word_count(self, word_count):
		self.current_word_count = word_count

	def decrease_current_word_count(self):
		self.current_word_count -= 1