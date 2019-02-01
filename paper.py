import smtplib
import gspread
import csv
import re
import glob
import time
import urllib
import requests
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials

def check_crossref(citation):
	"""Get a single CrossRef item manually for a given citation."""
	
	base_url = "https://api.crossref.org/works?query.bibliographic="
	url = base_url + urllib.parse.quote(citation, errors='backslashreplace')
	response = requests.get(url, timeout=100).json()
	item = response['message']['items'][0]
	return item

def clean_citation(citation):
	return citation.strip('\n').strip(' ').replace('\n', ' ')

class Paper:
	"""
	Store metadata for a specific paper.

	citation: lookup info we initialize the paper with (string)

	doi : DOI number, if it exists (string)
	url : DOI in URL form if it exists, generic link otherwise (string)
	year : year of publication (int)
	title : title of paper (string)
	author : "author1 and author2 and author3", etc. (string)
	reference_count : number of references
	is_referenced_by_count : number of times cited
	subjects : list of subjects given by CrossRef (list of strings)
	verified : Are we sure that our metadata is correct? (int, 0 or 1)
	
	item : full CrossRef item thing (string?)

	type: original, survey, or application? (string)
	includes_alg : does it include an algorithm? (int, 0 or 1)
	prob_attrs : list of problem attributes (csv strings)
	strategies : strategies used to approach the problem (csv strings)
	notes : any notes I made while reading (string)
	"""
	def __init__(self):

		self.citation = None
		self.DOI = None
		self.URL = None
		self.year = None
		self.title = None
		self.author = None
		self.reference_count = None
		self.is_referenced_by_count = None
		self.subject = None
		self.container_title = None

		self.auto_verified = 0
		self.is_parent = False
		self.file_loc = ""
		self.verified = 0
		self.checked = 0
		self.item = None
		self.hash = None
		
		self.type = None
		self.includes_alg = 0
		self.prob_attrs = None
		self.strategies = None
		self.notes = None   

		self.easy_attrs = ['DOI', 'URL', 'reference-count', 'container-title'
						   'is-referenced-by-count', 'subject']

	def is_duplicate(self, other):
		"""
		Return true if self is a duplicate of 'other' and false otherwise.

		Definition of duplicate: same citation OR 'same title or DOI and both
		papers are verified'.
		"""
		if self.citation != other.citation:
			#print("\nSame hash but citations don't match:\n\t", self.citation,
			#	"\n\t", other.citation)
			if self.DOI == other.DOI or self.title == other.title:
				#print("\tTitle or DOI does match")
				if self.verified and other.verified:
					#print("\tBoth papers are verified; this is a duplicate")
					return True
				#print("\tPapers aren't both verified; don't count as duplicate")

			return False
			
		else:
			return True

	def lookup(self, citation, base_url):
		"""
		Look up the citation in CrossRef and assign values accordingly.
		"""

		# Make the CrossRef API request
		self.citation = clean_citation(citation)
		url = base_url + urllib.parse.quote(citation, errors='backslashreplace')
		r = requests.get(url, timeout=250).json()
		self.item = r['message']['items'][0]

		# Figure out what to do about non-article things (websites esp.)

		# Get the straightforward properties
		for attr in self.easy_attrs:
			try:
				setattr(self, attr.replace('-','_'), self.item[attr])
			except KeyError:
				pass
			
		# Get the title
		try:
			self.title = self.item['title'][0].replace('\n','')

			def strip(s):
				return s.lower().replace(',','').replace('-','').replace(' ','')
			
			# Try to verify the paper
			if strip(self.citation).find(strip(self.title)) > 0:
				self.verified = 1
				self.auto_verified = 1

		except KeyError: pass

		# Get the year of publication
		try:
			self.year = self.item['issued']['date-parts'][0][0]
		except KeyError: pass

		# Get the author list
		try:
			authors = self.item['author']
			n = len(authors)
			alist = [authors[i]['given']+" "+authors[i]['family'] for i in range(n)]
			self.author = " and ".join(alist)
		except KeyError: pass

	def __str__(self):
		"""
		Print out in a nice format.
		"""
		out = "\nTitle: " + str(self.title)
		out += "\n\tAuthor(s): " + str(self.author)
		out += "\n\tReference count: " + str(self.reference_count)
		out += "\n\tCitation count: " + str(self.is_referenced_by_count)
		out += "\n\tDOI number: " + str(self.DOI)
		out += "\n\tYear of Publication: " + str(self.year)
		out += "\n\tSubject(s): " + str(self.subject)
		out += "\n\tType: " + str(self.type)
		out += "\n\tIncludes algorithm?: " + str(self.includes_alg)
		out += "\n\tProblem attributes: " + str(self.prob_attrs)
		out += "\n\tStrategies in approach: " + str(self.strategies)
		out += "\n\tNotes: " + str(self.notes)
		return out
