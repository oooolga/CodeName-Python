import warnings
import os

class VocabList:

	def __init__(self):
		self._doc_list = []
		self._doc_vocab_dict = {}
		self.vocab_list = set()

	def __len__(self):
		return len(self.vocab_list)

	def get_number_of_lists(self):
		return len(self._doc_list)

	def add_vocab_doc(self, doc):

		doc = os.path.abspath(doc)

		if doc in self._doc_list:
			warnings.warn(
				'{} was already added to the vocabulary list.'.format(doc))
			return False

		if len(self._doc_list) >= 10:
			raise MemoryError('You can load at most 10 vocabulary lists.')

		try:
			self.add_vocab_to_list(doc)
		except FileNotFoundError as err:
			warnings.warn('{} cannot be found.'.format(doc))
			return False
		except Exception as e:
			import sys
			warnings.warn("Unexpected error:", sys.exc_info()[0])
			return False

		self._doc_list.append(doc)
		return True

	def add_vocab_to_list(self, doc):

		doc = os.path.abspath(doc)
		self._doc_vocab_dict[doc] = []

		with open(doc, 'r') as vocab_f:
			
			for v in vocab_f:
				v = v.strip()
				if len(v) > 24:
					continue
				self._doc_vocab_dict[doc].append(v.upper())

			self.vocab_list |= set(self._doc_vocab_dict[doc])

		return

	def remove_vocab_doc(self, doc):

		doc = os.path.abspath(doc)

		if not doc in self._doc_list:
			warnings.warn(
				'{} was not in the vocabulary list.'.format(doc))
		else:
			self._doc_list.remove(doc)

		if not doc in self._doc_vocab_dict:
			warnings.warn(
				'{} was not in the vocabulary list.'.format(doc))
		else:
			self._doc_vocab_dict.pop(doc)

		self.vocab_list = set()
		for doc in self._doc_list:
			self.vocab_list |= set(self._doc_vocab_dict[doc])

		return

	def add_vocab_to_doc(self, doc, new_vocab_list):

		try:
			with open(doc, 'w+') as vocab_f:

				for vocab in new_vocab_list:
					vocab_f.write(vocab)

				doc = os.path.abspath(doc)
				if doc in self._doc_list:
					self._doc_vocab_dict[doc] += new_vocab_list
					self.vocab_list |= set(self._doc_vocab_dict[doc])
		except Exception:
			import sys
			warnings.warn("Unexpected error:", sys.exc_info()[0])
			return False

		return True


