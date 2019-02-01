class Database:
	"""
	Database to keep track of all the papers in my reference list and 
	citation network.

	Pieces we need:

	all_papers : Dictionary with some hashable as the keys and the Paper
				 objects as the values
	parents : Papers we're going to cite and have .txt reference lists for
	children : All the references of the parents (check for accuracy)
	grandchildren : References included in CrossRef for all the children
	"""

	def __init__(self):
		pass

	def write_to_file(self, papers, filename):
		"""
		Write the given iterable collection of Paper objects to filename.
		"""
		pass

	def initialize_parents(self, filename=None):
		"""
		Add all the parent papers using their .txt reference files.

		If a filename is given, read them in from that instead.

		If a filename is given but we have more .txt reference files than
		entries, first read in the filename, then hash the citation strings 
		for the first line of all files to see if we have it. Only look up
		if we don't.
		"""
		pass

	def initialize_children(self, bibs):
		"""
		Add all the references in the list of bib files. This way we don't
		have to do them all at once. Every time you finish with a file, 
		write a new file that has all the information.


		"""
		pass

	def read_parents(self):
		"""
		If we actually
		"""
		pass

	def sync_spreadsheet(self):
		"""
		Add the hand-verification from the spreadsheet to the database.
		"""

		# Open up the main sheet

		# Glob in columns to let us figure out which row each parent is in

		# For each parent

			# If any of the 'I fill out' entries are None (besides 'notes')

				# Get the row values and see if I updated any of them

				# If I did, assign those values

		# Open up the 'verification' sheet
			
		# Glob in columns to look up what our paper is in the database

		# For each nonempty row

			# Figure out which Paper we got 

			# If verification value from spreadsheet is true but ours is false

				# Reset our Paper using values from that row
		
		pass

	def make_bibtex(self):
		"""
		Write bibtex entries for all the parents.
		"""

		# bib = requests.request('GET', 'http://dx.doi.org/' + self.doi, 
        #        headers={'Accept':'application/x-bibtex'}, timeout=100)
        #self.bibtex = bib.text
        pass