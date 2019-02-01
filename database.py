import smtplib
import gspread
import csv
import re
import glob
import time
import urllib
import requests
import numpy as np
from collections import defaultdict
from oauth2client.service_account import ServiceAccountCredentials

from paper import clean_citation
from paper import Paper

def sleep():
	print("\nSLEEP FOR 100 SECONDS SO THE API DOESN'T GET MAD")
	for i in range(10):
		time.sleep(10)
		print(10*(i+1), "seconds done")
	print()

class Database:
	"""
	Database to keep track of all the papers in my reference list and 
	citation network.

	all_papers : Dict with {(title, year): actual Paper object}
	parents : Papers we're going to cite and have .txt reference lists for
		(dict with hash as key and set of reference's hashes as values)
	children : Same as parents but for getting grandchildren
		(dict with hash as key and set of reference's hashes as values)

	client: Thing to get the spreadsheet
	spreadsheet : Opened google drive spreadsheet of the paper database
	main_sheet : All the parents
	verification_sheet : Place to fix stuff by hand in the references

	bibs : list of filenames for all the bibliographies of stuff
	base_url : base URL for the API request to CrossRef
	doi_url : base URL for a DOI number

	int_attrs : Paper properties that should be integers
	auto_attrs : Properties where CrossRef values override, if verified
	hand_attrs : Properties where hand-filled values always take precedence
	"""

	######## 

	def __init__(self):
		
		# Paper storage organization
		self.all_papers = defaultdict()
		self.parents = defaultdict(set)
		self.parent_citations = dict()

		# URLs and filenames
		self.bibs = glob.glob('./bibliographies/*.txt')
		self.base_url = "https://api.crossref.org/works?query.bibliographic="
		self.doi_url = "http://dx.doi.org/"

		# Get the Google drive spreadsheet stuff
		scope = ['https://spreadsheets.google.com/feeds',
				 'https://www.googleapis.com/auth/drive']
		creds = ServiceAccountCredentials.from_json_keyfile_name(
			'client_secret.json', scope)
		self.client = gspread.authorize(creds)
		self.spreadsheet = self.client.open("Paper Database")
		self.main_sheet = self.spreadsheet.get_worksheet(0)

		# Misc "shouldn't re-assign"
		self.int_attrs = ['year', 'reference_count', 'is_referenced_by_count',
			'verified', 'includes_alg', 'auto_verified', 'checked']
		self.auto_attrs = {'citation', 'hash', 'URL', 'DOI', 'year', 'title',
			'reference_count', 'is_referenced_by_count', 'author', 'subject'}
		self.hand_attrs = {'verified', 'type', 'includes_alg', 'prob_attrs',}

	def add_paper(self, p, citation=None, is_parent=False):
		"""
		Add paper p to the database.
		"""

		# Don't add an empty paper to the database
		is_empty = True
		empty_paper = Paper()
		for attr in ["citation", "title", "DOI", "year"]:
			if str(empty_paper.__dict__[attr]) != p.__dict__[attr]:
				is_empty = False
		if is_empty:
			print("DON'T ADD AN EMPTY PAPER, DUMMY")
			return p

		# Look up using CrossRef if given just the citation 
		if citation:
			p.lookup(citation, self.base_url)

		# Unpack/convert attributes that shouldn't be just strings
		else:
			if p.checked == "False":
				p.checked = 0.0
			for attr in self.int_attrs:
				if p.__dict__[attr] != "None":
					setattr(p, attr, float(p.__dict__[attr]))
			p.subject = eval(p.subject)
			p.item = eval(p.item)
			p.container_title = eval(p.container_title)

			"""
			# Leftover from initially adding the journal titles as an attr
			if p.container_title == "None":
				try:
					p.container_title = p.item['container-title']
				except KeyError:
					pass
			"""

		p.hash = (p.title, p.year)
		if is_parent:
			p.is_parent = True

		# Deal with the case where the paper hash is already in the database
		if p.hash in self.all_papers:

			# If it's a duplicate, just return the paper
			if p.is_duplicate(self.all_papers[p.hash]):
				return p

			# If it's not really a duplicate, re-hash one of them
			else:
				old_p = self.all_papers[p.hash]

				# Def'n of dup shouldn't let two non-dup papers both be verified
				if p.verified == 1 and old_p.verified == 1:
					raise ValueError("THEY CAN'T BE BOTH VERIFIED AND NON-DUPLICATE")

				# If the one already there is correct (and p therefore isn't),
				# keep it as is and hash p by citation
				if old_p.verified:
					p.hash = (p.citation, "CITATION ONLY")
					self.all_papers[p.hash] = p

					# I don't think this is doing anything and might need to move
					if is_parent:
						old_p_kids = self.parents[old_p.hash]
						self.parents[old_p.hash] = old_p_kids
						self.parents[p.hash] = set()

				# Otherwise, re-hash the old one and put p in its spot
				else:
					old_p.hash = (old_p.citation, "CITATION ONLY")
					self.all_papers[old_p.hash] = old_p
					self.all_papers[p.hash] = p

					if is_parent:
						old_p_kids = self.parents[p.hash]
						self.parents[old_p.hash] = old_p_kids
						self.parents[p.hash] = set()

		# If we don't already have the paper, simply add as usual
		else:
			self.all_papers[p.hash] = p

		# It's a defaultdict, but it's still nice to just put the hash in now
		if is_parent and p.hash not in self.parents:
			self.parents[p.hash] = set()

		return p

	def write_paper(self, output, p):
		"""
		Write a single paper to file
		"""
		output.write(">>> NEW PAPER <<<")
		for attr in p.__dict__.keys():
			output.write("\n>>> "+attr+" >>> "+str(p.__dict__[attr]))
		output.write("\n")	

	def import_file(self, filename, is_parent=False):

		citations = dict()
		read_all = False

		try:
			with open(filename, errors="backslashreplace") as input:

				p = Paper()
				start = True

				for line in input:
					
					line = line.replace("\n","")

					if line == ">>> NEW PAPER <<<":
						if start: 
							start = False
						else: 
							self.add_paper(p, is_parent=is_parent)
							citations[p.citation] = p
							p = Paper()
					elif line == ">>> ALL DONE <<<":
						read_all = True
					else:
						
						items = line.split(">>>")
						if len(items) < 3:
							print("line, items:", line, items)
						setattr(p, items[1].strip(' '), items[2].strip(' '))
						
				if p.title:
					self.add_paper(p, is_parent=is_parent)
					citations[p.citation] = p

		except FileNotFoundError: pass

		return citations, read_all

	def initialize_parents(self, p_file):
		"""
		Add all the parent papers using their .txt reference files. Read in
		anything that's already been calculated and stored in parents.txt
		"""

		self.parent_citations, read_all = self.import_file(p_file, is_parent=True)
		
		print("Number of parents read from file:", len(self.all_papers))

		if read_all:
			print("All parents added from file; no lookup necessary")

		else:
			with open(p_file, 'a', errors='backslashreplace') as output:

				for i in range(len(self.bibs)):

					with open(self.bibs[i], errors="backslashreplace") as input:

						inputstr = input.readline().strip()
						splits = re.split('\[[0-9]+\]', inputstr)
						citation = splits[1].strip(' ')

						if citation not in self.parent_citations:
							
							print("\nlen(all_papers):", len(self.all_papers))
							print("Add parent", i+1, "of", len(self.bibs), 
								"file", self.bibs[i])
							
							p = self.add_paper(Paper(), citation, is_parent=True)
							self.parent_citations[p.citation] = p
							p.file_loc = self.bibs[i]
							self.write_paper(output, p)

							print("new len(all_papers):", len(self.all_papers)) 

						else:
							self.parent_citations[citation].file_loc = self.bibs[i]

	def initialize_children(self):
		"""
		Add all the references for each paper in the list of bib files.
		"""
		j = 0

		# Go through all the bibliography files
		for bib in self.bibs:

			j += 1

			with open(bib, errors="backslashreplace") as input:
					
				# Fetch or add the parent paper
				splits = re.split('\[[0-9]+\]', input.readline().strip())
				parent_citation = clean_citation(splits[1])
				parent = self.parent_citations[parent_citation]			

				# Get the right filename for the child file
				bib0 = bib.replace('\\','').replace('bibliographies','')
				bib0 = bib0.strip('.').replace('/','')
				childfile = "ref_lists/children_of_" + bib0

				old_size = len(self.all_papers)

				# Get any papers we've already written to the child file
				child_citations, read_all = self.import_file(childfile)
				for citation, p in child_citations.items():
					self.parents[parent.hash].add(p)
					p.file_loc = bib

				if read_all:
					print("("+ str(j) + " of " + str(len(self.bibs)) + ") " +
						"Bib #" + bib[25:-4] + ": All children added from file")

				else:
					# Go through the rest of the file to look up papers
					with open(childfile, 'a', errors='backslashreplace') as output:
						
						inputstr = input.read()
						splits = re.split('\[[0-9]+\]', inputstr.strip(' '))

						print("("+ str(j) + " of " + str(len(self.bibs)) + ")",
							len(splits)-1, "children,", bib[17:])
						#print("\t  ", len(child_citations), "children read from file")

						for i in range(1, len(splits)):

							child_citation = clean_citation(splits[i])
							#print(child_citation)

							if child_citation not in child_citations:
								print("\tAdd child", i, "of", len(splits)-1)
								print('\t\t' + child_citation[:50])

								p = self.add_paper(Paper(), child_citation)
								p.file_loc = bib
								self.write_paper(output, p)
								self.parents[parent.hash].add(p)

						num_children = len(self.parents[parent.hash])
						print("     Added", num_children, "children,", 
							len(self.all_papers) - old_size, "new papers")

	######## SYNC WITH STORAGE FILES AND SPREADSHEET ########

	def rewrite_parents(self, parents_file):
		"""Update the parents file after syncing."""

		with open(parents_file, 'w', errors='backslashreplace') as output:
			for p_hash in self.parents.keys():
				self.write_paper(output, self.all_papers[p_hash])
			output.write(">>> ALL DONE <<<")

	def rewrite_children(self):
		"""Rewrite the children files after updating parents or verifying."""
		
		# Go through all the parents
		for p_hash, ref_list in self.parents.items():
			
			# Fetch the parent paper and child filename
			parent = self.all_papers[p_hash]
			bib0 = parent.file_loc.replace('\\','').replace('bibliographies','')
			childfile = "ref_lists/children_of_" + bib0.strip('.').replace('/','')

			with open(childfile, 'w', errors="backslashreplace") as output:
				for child in ref_list:
					self.write_paper(output, child)
				output.write(">>> ALL DONE <<<")
					
	def sync_parents(self):
		"""
		Add the hand-generated data from the spreadsheet to the database and
		update the spreadsheet with the info we have.
		"""

		# Open up the main sheet and store some metadata stuff
		all_rows = self.main_sheet.get_all_records()

		citation_col = self.main_sheet.find("citation").col
		citations = set(self.main_sheet.col_values(citation_col))

		col_titles = self.main_sheet.row_values(1)
		num_cols = len(col_titles)

		num_requests = 4

		j = 1
		
		parents = set(self.parents.keys()).copy()
		for p_hash in parents:

			p = self.all_papers[p_hash]
			print("\nUpdate", j, "of", len(parents), ":", p_hash)
			j += 1

			# If the row already exists in the spreadsheet
			if p.citation in citations:
				
				row_num = self.main_sheet.find(p.citation).row
				row_dict = all_rows[row_num-2]
				
				num_to_rewrite = 0
				num_requests += 1
				newrow = []
				
				# Go through all the attributes and sync
				for attr in col_titles:

					# If our current p.attr value is the one we want
					if attr in self.auto_attrs and p.auto_verified:

						newrow.append(str(p.__dict__[attr]))
						if str(row_dict[attr]) != str(p.__dict__[attr]):
							num_to_rewrite += 1

					# Otherwise, keep the spreadsheet value and update p
					else:
						
						if attr == "hash":

							item = row_dict["hash"]
							new_hash = (item[2:-8], item[-5:-1])
							old_reflist = self.parents[p.hash]
							
							del self.all_papers[p.hash]
							del self.parents[p.hash]

							self.all_papers[new_hash] = p
							self.parents[new_hash] = old_reflist
							print("REPLACED HASH")
							print("\tnew size of all_papers:", len(self.all_papers))
							print("\tnew size of parents:", len(self.parents))
							
						else:
							p.__dict__[attr] = row_dict[attr]
							newrow.append(str(row_dict[attr]))

				# Update the spreadsheet if necessary
				if num_to_rewrite > 0:		
					cells = self.main_sheet.range(row_num, 1, row_num, num_cols)
					
					for i in range(len(cells)):
						cells[i].value = newrow[i]

					self.main_sheet.update_cells(cells)
					num_requests += 2

			# Otherwise, add a new row
			else:	
				newrow = []
				for attr in col_titles:
					newrow.append(str(p.__dict__[attr]).strip('\n'))

				index = self.main_sheet.row_count
				self.main_sheet.insert_row(newrow, index)
				num_requests += 2
			
			# Make sure we don't overload the API
			if num_requests > 85:
				sleep()
				num_requests = 0

	######## MANUAL VERIFICATION HELPERS ######## 

	def print_stats(self):
		"""Print out verification and size statistics."""
		
		unchecked, regular_checked, to_discard = 0, 0, 0
		just_wrong, close_enough, verified = 0, 0, 0
		unchecked_unverified = 0

		num_children = 0
		for p_hash, ref_list in self.parents.items():
			num_children += len(ref_list)
		print("Total length of all reference lists:", num_children)
		print("Total number of papers:", len(self.all_papers))

		for p_hash, p in self.all_papers.items():

			if p.checked == 0 and p.verified == 0:
				unchecked_unverified += 1

			if p.checked == 0: unchecked += 1
			elif p.checked == 1: regular_checked += 1
			elif p.checked == 2: to_discard += 1
			
			if p.verified == 0: just_wrong += 1
			elif p.verified == 0.5: close_enough += 1
			elif p.verified == 1: verified += 1
			
		print("\n\t", unchecked_unverified, "unchecked and unverified")
		print("\n\t", unchecked, "papers unchecked")
		print("\t", regular_checked, "papers manually checked")
		print("\t", to_discard, "papers to get rid of")
		print("\t", unchecked + regular_checked + to_discard, "total")
		print("\n\t", verified, "papers known to be correct")
		print("\t", close_enough, "not quite right, but close enough")
		print("\t", just_wrong, "entries just wrong")
		print("\t", verified + close_enough + just_wrong, "total")
	
	def write_bads(self, writefile):
		"""
		Write out a tab separated .csv file to manually check and update
		unverified papers.

		SPREADSHEET UPDATING INSTRUCTIONS
		---------------------------------
		1) DO NOT ADD OR CHANGE THE ORDER OF THE COLUMNS. Resizing is fine.
		2) DO NOT TOUCH the "hash" or "citation" columns. It will screw things up.
		3) If you update title and/or year, put the new (title, year) hash in 
			the "new_hash" column.
		4) Write author names separated by "and". 
		5) You can change URL and DOI, but it won't update the database.
		6) Set verified to 1 if the citation is correct and 0.5 if it's a 
			review, purchase listing, or similar of the correct thing.
			- If you set verified to 0.5, do not change author, title, or year.
		7) Set "checked" to 1 for every paper you've manually looked at.
		8) Setting "checked" to 2 marks a reference for deletion. Mark a 
			reference for deletion if it is any of the following:
			- A website or web service 
			- A database or database dump
			- A "personal communication"
			- A software package, software library, or programming language
			- Clearly the clipped second line of a full citation
			- Any citation which does not contain enough information to find
			  the reference even with clever googling.
		"""
		cols = ["hash", "citation", "verified", "checked", "new_hash", "author",
				"title", "year", "URL", "DOI"]
		delim = "\t"
		qchar = "|"

		with open(writefile, "w", errors="backslashreplace") as outputfile:

			writer = csv.writer(outputfile, delimiter=delim, quotechar=qchar,
				lineterminator="\n")
			writer.writerow(cols)

			for p_hash, p in self.all_papers.items():
				if p.verified < 0.5:# and p.checked < 1:
					newrow = []
					for attr in cols:
						if attr in p.__dict__:
							to_add = str(p.__dict__[attr]).strip('\n')
							newrow.append(to_add.replace("\t", " "))
						else:
							newrow.append("")
					writer.writerow(newrow)

	def update_bads(self, readfile):
		"""
		Read in the results from a modified output of write_bads and update
		the database accordingly.
		"""
		cols = ["hash", "citation", "verified", "checked", "new_hash", "author",
				"title", "year", "URL", "DOI"]
		update_hashes = dict()
		to_delete = set()
		updated_year, updated_author, updated_title = 0, 0, 0
		newly_verified, newly_checked, num_rows = 0, 0, 0
		delim = "\t"
		qchar = "|"
		first = True

		print("STATS BEFORE UPDATING:\n")
		self.print_stats()

		with open(readfile, encoding="utf-8", errors="backslashreplace") as input:

			for line in input:

				if first: 
					first = False

				else:

					row = line.split("\t")
					row_dict = {cols[i]:row[i] for i in range(len(cols))}
					p_hash = eval(row_dict["hash"].strip('|'))

					# Hacky Unicode stupid
					if p_hash not in self.all_papers and len(p_hash) > 1:
						p_hash = (p_hash[0].replace('\x9d','\\x9d'),p_hash[1])
					
					# Update any modified values
					if p_hash in self.all_papers:
						num_rows += 1
						new_hash = row_dict["new_hash"]
						p = self.all_papers[p_hash]

						if len(new_hash) > 0:
							update_hashes[p_hash] = new_hash

						if int(row_dict["checked"]) == 2:
							to_delete.add(p_hash)
							
						if p.verified < float(row_dict["verified"]):
							p.verified = float(row_dict["verified"])
							newly_verified += 1
							
						if p.title != row_dict["title"]:
							updated_title += 1
							p.title = row_dict["title"]
							
						if str(p.year) != row_dict["year"]:
							updated_year += 1
							p.year = row_dict["year"]
							
						if p.author != row_dict["author"]:
							updated_author += 1
							p.author = row_dict["author"]
							
						if p.year == "None":
							p.year = None
						if p.year:
							p.year = int(p.year)
					else:
						print("NOT IN DATABASE:")
						print(type(row_dict["hash"]), row_dict["hash"])
						print(type(p_hash),p_hash)
						print(p_hash[0].encode("utf-8", errors="backslashreplace"))

			print("Updated", num_rows, "records")
			print("\t", len(update_hashes), "hashes manually updated")
			print("\t", len(to_delete), "records marked for deletion")
			print("\t", newly_checked, "records newly checked")
			print("\t", newly_verified, "records newly verified")
			print("\t\t", updated_title, "of those with updated title")
			print("\t\t", updated_author, "of those with updated author")
			print("\t\t", updated_year, "of those with updated year")

		print("\nDeleting", len(to_delete), "records")
		for bad in to_delete:
			for p_hash, ref_list in self.parents.items():
				if self.all_papers[bad] in ref_list:
					ref_list.remove(self.all_papers[bad])
			if bad in self.all_papers:
				del self.all_papers[bad]

		print("Updating", len(update_hashes), "hashes")
		for p_hash, new_hash in update_hashes.items():

			# Hacky cleanup for screwy apostrophes and stuff
			new_hash = new_hash.replace('`','')
			if new_hash.count("'") != 2:
				new_hash = new_hash.replace("'","")
				if new_hash[1] != "'":
					new_hash = "('" + new_hash[1:]
				if new_hash[-8] != "'":
					new_hash = new_hash[:-7] + "'" + new_hash[-7:]

			p = self.all_papers[p_hash]
			if p.is_parent == False: # DON'T MESS WITH THE PARENTS
				self.all_papers[new_hash] = p
				del self.all_papers[p.hash]
				p.hash = new_hash

		print("\nSTATS AFTER UPDATING:\n")
		self.print_stats()

	######## CITATION NETWORK AND HELPER FUNCTIONS ######## 
	
	def preprocess(self, thing):
		"""Clean out the stuff Mathematica doesn't like"""
		
		# We can't have any extra quotation marks
		thing = thing.replace('"','').replace("'",'')

		# Mathematica needs the double backslash in the unicode chars
		thing = thing.encode('ascii','backslashreplace')
		return thing.decode('ascii').replace('\\u','\\\\u')

	def add_node(self, p, p_hash, output, nodes):
		
		if p_hash not in nodes:
			
			nodes[p_hash] = len(nodes) + 1

			out = '\n\tnode [ \n'
			out += '\t\tid ' + str(nodes[p_hash]) + '\n'
			#out += '\t\tlabel ' + str(nodes[p_hash]) + '\n'
			out += '\t\ttitle "' + self.preprocess(p.title) + '"\n'
			out += '\t\tyear ' + str(p.year) + '\n'
			out += '\t\treferenceCount ' + str(p.reference_count) + '\n'
			out += '\t\tcitationCount ' + str(p.is_referenced_by_count) + '\n'
			#out += '\t\tURL "' + self.preprocess(p.URL) + '"\n'
			#out += '\t\thash "' + self.preprocess(str(p.hash)) + '"\n'
			#out += '\t\tcitation "' + self.preprocess(p.citation) + '"\n'
			#out += '\t\tverified ' + str(p.verified) + '\n'
			#out += '\t\ttype "' + str(p.type) + '"\n'
			#out += '\t\tincludesAlg ' + str(p.includes_alg) + '\n'
			out += '\t]\n'
			
			output.write(out)
			
	def add_edge(self, source_id, target_id, output, nodes, edges):

		if source_id != target_id and (source_id, target_id) not in edges:
			out = '\n\tedge [ \n'
			out += '\t\tsource ' + str(source_id) + '\n'
			out += '\t\ttarget '+ str(target_id) + '\n'
			out += '\t]\n'
			edges.add((source_id, target_id))
			output.write(out)

	def citation_network(self, filename, max_edges=1e6):
		"""
		Write the citation network to a .gml file.
		"""
		nodes = dict()
		edges = set()
		num_edges = 0

		with open(filename, 'w', errors='backslashreplace') as f:

			f.write("graph [\n\tdirected 1\n")

			for parent_hash, ref_list in self.parents.items():

				if len(ref_list) > 0:

					self.add_node(self.all_papers[parent_hash], parent_hash, f, nodes)
					
					for child in ref_list:

						self.add_node(child, child.hash, f, nodes)

						source_id = nodes[parent_hash]
						target_id = nodes[child.hash]
						self.add_edge(source_id, target_id, f, nodes, edges)
						num_edges += 1

						if num_edges > max_edges:
							print("MAX EDGES REACHED")
							f.write("]")
							return

			print(num_edges, "edges written with max_edges =", max_edges)
			f.write("]")

	######## MISCELLANEOUS USEFUL FILE GENERATION ########
	
	def to_csv(self, filename):
		"""
		Write the whole database to a .csv file so you can look at it. Moving
		column orders is fine after download, it's just read-only.
		"""
		cols = ["citation", "hash", "is_parent", "auto_verified", "verified", 
				"year", "title", "author", "URL", "file_loc", "reference_count", 
				"is_referenced_by_count"]
		delim = "\t"
		qchar = "|"

		with open(filename, "w", errors="backslashreplace") as outputfile:

			writer = csv.writer(outputfile, delimiter=delim, quotechar=qchar,
				lineterminator="\n")
			writer.writerow(cols)

			for p_hash, p in self.all_papers.items():
				newrow = []
				for attr in cols:
					if attr in p.__dict__:
						to_add = str(p.__dict__[attr]).strip('\n')
						newrow.append(to_add.replace("\t", " "))
					else:
						newrow.append("")
				writer.writerow(newrow)

	def file_dumps(self):
		"""
		Convenience function to smush all the reference lists together.
		"""
		headers_list = []

		with open("ALL_CITATIONS.txt", 'w', errors="backslashreplace") as output:

			for i in range(len(self.bibs)):

				with open(self.bibs[i], errors="backslashreplace") as input:
					
					inputstr = input.read()
					splits = re.split('\[[0-9]+\]', inputstr)

					output.write('\nTHIS ONE IS THE HEAD OF THE FILE '+self.bibs[i]+':\n\n')
					output.write(splits[1])
					headers_list.append(self.bibs[i] + ", " + splits[1])
					output.write('\nHERE ARE ALL ITS CITED THINGS:\n\n')

					for j in range(2,len(splits)):
						output.write(splits[j]+'\n')

		with open("ALL_HAVEBIBS.txt", 'w', errors="backslashreplace") as output:
			for i in range(len(headers_list)):
				output.write(headers_list[i])
				output.write('\n')

		with open("all_papers_dump.txt", "w", errors="backslashreplace") as output:
			for p_hash, p in db.all_papers.items():
				self.write_paper(output, p)

	def make_bibtex(self):
		"""
		Write bibtex entries for all the parents.
		"""
		filename = './ThesisClass/thesis_bibliography.txt'

		with open(filename, 'w', errors='backslashreplace') as output:

			for p_hash in self.parents:

				p = self.all_papers[p_hash]
				bib = requests.request('GET', 'http://dx.doi.org/' + p.doi, 
				headers={'Accept':'application/x-bibtex'}, timeout=100)
				output.write('\n' + bib.text)

