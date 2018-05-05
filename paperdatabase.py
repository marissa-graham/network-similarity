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
    """
    See if the CrossRef results match what you want manually for a certain
    paper by returning the title of the lookup result.
    """
    base_url = "https://api.crossref.org/works?query.bibliographic="
    url = base_url + urllib.parse.quote(citation)
    response = requests.get(url, timeout=10).json()
    item = response['message']['items'][0]
    return item['title']

class Paper:
    """
    Store metadata for a specific paper.

    doi : DOI number, if it exists
    year : year of publication
    title : title of paper
    author : "author1 and author2 and author3", etc.
    citation : original info used to look up the paper
    bibtex : nice string to put in BibTeX

    crossref_item : result of a CrossRef lookup
    crossref_score : matching score for crossref lookup
    verified : 1 iff CrossRef result is verified correct
    index : index location in the list of all the papers

    in_spreadsheet : have I read through it for strategies and problem attrs?
    field : field of study of primary author
    original_work : is it a survey paper?
    includes_alg : does it include an algorithm?
    prob_attrs : list of problem attributes
    strategies : strategies used in the paper to approach the problem
    notes : any notes I made while reading
    """
    def __init__(self):

        # Actual important metadata
        self.doi = None
        self.year = None
        self.title = ""
        self.author = []
        self.citation = None
        self.bibtex = None

        # CrossRef-specific and housekeeping
        self.crossref_item = None
        self.crossref_score = 0
        self.verified = 0
        self.index = -1
        
        # Spreadsheet-specific
        self.in_spreadsheet = False
        self.field = ""
        self.original_work = True
        self.includes_alg = False
        self.prob_attrs = []
        self.strategies = []
        self.notes = ""

    def get_crossref(self, citation, base_url, get_bib=True):
        """
        Look up the citation in CrossRef and assign values accordingly.

        If the paper has been read in from the spreadsheet, compare the
        CrossRef results to the spreadsheet values to compare accuracy.
        """

        self.citation = citation 

        url = base_url + urllib.parse.quote(citation)
        r = requests.get(url, timeout=100).json()
        self.crossref_item = r['message']['items'][0]


        try:
            self.doi = self.crossref_item['DOI']
        except KeyError:
            pass

        try:
            self.title = self.crossref_item['title'][0].encode(
                'ascii','ignore').decode()
        except KeyError:
            pass

        self.crossref_score = self.crossref_item['score']
        doi_url = 'http://dx.doi.org/' + self.doi

        if get_bib:
            bib = requests.request('GET', doi_url, 
                headers={'Accept':'application/x-bibtex'}, timeout=100)
            self.bibtex = bib.text

            bibdict = {}
            splitbib = bib.text[9:-2].split(',\n')
            for i in range(len(splitbib)):
                keyval = splitbib[i].strip().split(' = ')
                if len(keyval)>1:
                    bibdict[keyval[0]] = keyval[1].strip('{}')

            try:
                self.year = bibdict['year']
            except KeyError:
                pass
            try:
                self.author = bibdict['author']
            except KeyError:
                pass

    def add_from_spreadsheet(self, sheet, row, bool_inds, str_inds):
        """
        """
        self.in_spreadsheet = True
        row_vals = sheet.row_values(row)

        if sheet.cell(row, bool_inds[0]).value == "TRUE":
            self.verified = 1
        if sheet.cell(row, bool_inds[1]).value == "Survey":
            self.original_work = False
        if sheet.cell(row, bool_inds[2]).value == "Yes":
            self.includes_alg = True

        str_vals = [sheet.cell(row, str_inds[i]).value for i in range(len(str_inds))]

        self.doi, self.year, self.author, self.field = str_vals[:4]
        self.title, self.prob_attrs, self.strategies, self.notes = str_vals[4:]

    def __str__(self):
        """
        Print out in a nice format.
        """
        out = "\nTitle: " + self.title
        out += "\n\tAuthor(s): " + str(self.author)
        out += "\n\tDOI number: " + self.doi
        out += "\n\tYear of Publication: " + self.year
        out += "\n\tOriginal work (not survey paper)?: " + str(self.original_work)
        out += "\n\tField of study of primary author: " + self.field
        out += "\n\tIncludes algorithm?: " + str(self.includes_alg)
        out += "\n\tProblem attributes: " + str(self.prob_attrs)
        out += "\n\tStrategies in approach: " + str(self.strategies)
        out += "\n\tNotes: " + self.notes
        return out

    def to_csv(self):
        """
        Return a list of attributes to be joined into a row in a .csv file
        """
        return [self.doi, self.year, self.title, self.author, self.citation, 
            self.bibtex, self.crossref_score, self.verified, self.index, 
            self.in_spreadsheet, self.field, self.original_work, self.includes_alg, 
            self.prob_attrs, self.strategies, self.notes]

class Database:
    """
    Database for all the papers.

    sheet : Google sheets spreadsheet with data in it
    papers : list of Paper objects in the database
    titles : set with all the titles of the papers in the database
    bibs : list of filenames for all the bibliographies of stuff

    base_url : base URL for the API request to CrossRef
    doi_url : base URL for a DOI number
    """

    def __init__(self):
    
        self.papers = []
        self.titles = dict()
        self.bibs = glob.glob('./bibliographies/*.txt')

        self.base_url = "https://api.crossref.org/works?query.bibliographic="
        self.doi_url = "http://dx.doi.org/"

        # Get the Google drive spreadsheet
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'client_secret.json', scope)
        client = gspread.authorize(creds)
        self.sheet = client.open("Database Entry Form (Responses)").sheet1

    def add_paper(self, citation, get_bib=True, update_spreadsheet=False):
        """
        Add paper to the database and return it.
        """

        p = Paper()
        p.get_crossref(citation, self.base_url, get_bib=get_bib)

        # Check if the title matches what we expect from the citation
        strip_citation = citation.lower().replace('-','')
        strip_ptitle = p.title.replace(',','').replace('-','').lower()

        if strip_citation.find(strip_ptitle) > 0:
            p.verified = 1
        else:
            print("Could not verify", strip_ptitle, "from", strip_citation)

        # Check if it's a duplicate and add/return accordingly
        if p.title in self.titles:

            matches_p = self.papers[titles[p.title]]
            
            if p.doi != matches_p.doi:
                raise ValueError("WE HAVE RUN INTO A DUPLICATE TITLE:", p.title,
                 "matches DOI numbers", p.doi, "and", matches_p.doi)

            return self.papers[titles[p.title]]

        else:
            p.index = len(self.papers)
            self.titles[p.title] = p.index
            self.papers.append(p)
            return p

    # Main thing from 643 project, haven't touched since
    def import_bibliographies(self, num_papers):
        """
        Go through the .txt file bibliographies we made, add all the papers
        to the database, and make an adjacency list for all the citations
        """

        with open('bib_edges.txt','w') as output:
        
            for i in range(num_papers):

                bibfile = "bibliographies\\database" + str(i+1) + ".txt"

                with open(bibfile) as input:

                    splits = re.split('\[[0-9]+\] ', input.read())
                    head = splits[1].replace('\n',' ').strip(' ')
                    
                    print("\nRead bibliography for paper", i+1, "of", num_papers,
                        ": ", len(splits)-2, " references")
                    print('*'*100,'\n')

                    p, unique = self.add_paper(head)

                    for j in range(2,len(splits)):

                        ref = splits[j].replace('\n',' ').strip(' ')
                        print('(', j-1, 'of', len(splits)-2, ')', ref[:80])
                        q, unique = self.add_paper(ref, get_bib=False)
                        output.write(p.title + ' <-> ' + q.title + '\n')

    # Kinda useless, it's slower than just using CrossRef
    def read_from_spreadsheet(self):
        """
        Read the spreadsheet into a database.
        """
        n = self.sheet.row_count
        col_names = self.sheet.row_values(1)

        lookup_cols = ['CrossRef Verified', 'Original?', 'DOI number', 'Year', 
                'Authors', 'Field of Study of Primary Author', 'Algorithm?', 
                'Title', 'Problem Attributes', 'Strategies', 'Notes'] 

        bool_cols = ['CrossRef Verified', 'Original?', 'Algorithm?']

        str_cols =  ['DOI number', 'Year', 'Authors', 'Field of Study of Primary Author',
                'Title', 'Problem Attributes', 'Strategies', 'Notes']

        bool_inds = [col_names.index(col) + 1 for col in bool_cols]
        str_inds = [col_names.index(col) + 1 for col in str_cols]

        num_requests = 2

        for i in range(2, n+1):

            if num_requests > 80:
                print("\nSLEEP FOR 100 SECONDS SO THE API DOESN'T GET MAD")
                for i in range(10):
                    time.sleep(10)
                    print(10*i, "seconds done")
                print()
                num_requests = 0

            if len(self.sheet.row_values(i)) > 0:
                p = Paper()
                p.add_from_spreadsheet(self.sheet, i, bool_inds, str_inds)
                print(p)
                num_requests += 12

                p.index = len(self.papers)
                self.titles[p.title] = p.index
                self.papers.append(p)

            else:
                num_requests += 1

    def read_from_bibheaders(self):
        """
        Go through the bibliography .txt files we have and add their
        corresponding papers.
        """
        for i in range(len(self.bibs)):
            with open(self.bibs[i]) as input:
                print("Add", i, "of", len(self.bibs), "from", self.bibs[i])
                splits = re.split('\[[0-9]+\] ', input.read())
                head = splits[1].replace('\n',' ').strip(' ')
                p = db.add_paper(head)
        
    def update_spreadsheet(self):
        """
        Update the entries in the spreadsheet with CrossRef entries from the
        existing database.
        """
        col_names = self.sheet.row_values(1)
        update_cols = ['CrossRef Verified', 'DOI number', 'Year', 'Authors']
        col_inds = [col_names.index(col) + 1 for col in update_cols]

        num_requests = 1

        for i in range(len(self.papers)):
            
            p = self.papers[i]
            
            if num_requests > 90:
                print("\nSLEEP FOR 100 SECONDS SO THE API DOESN'T GET MAD")
                for i in range(10):
                    time.sleep(10)
                    print(10*i, "seconds done")
                print()
                num_requests = 0
            
            if p.verified:
                
                # Already in the spreadsheet
                try:
                    row = self.sheet.find(p.title).row
                    p.in_spreadsheet = True
                    num_requests += 1
                    
                    if self.sheet.cell(row, col_inds[0]).value != "TRUE":
                        self.sheet.update_cell(row, col_inds[0], 'True')
                        num_requests += 1

                        if p.doi is not None:
                            self.sheet.update_cell(row, col_inds[1], 
                                            self.doi_url + p.doi)
                            num_requests += 1

                        if p.year is not None:
                            self.sheet.update_cell(row, col_inds[2], p.year)
                            num_requests += 1

                        if p.author is not None:
                            self.sheet.update_cell(row, col_inds[3], p.author)
                            num_requests += 1


                # Not already in the spreadsheet
                except:

                    # Add known values and TODOS
                    newrow = ['', 'TRUE', '', 'TODO', self.doi_url + p.doi, 
                              p.year, p.author, 'TODO', 'TODO', p.title, 'TODO', 
                              'TODO', '']
                    self.sheet.append_row(newrow)
                    p.in_spreadsheet = True
                    num_requests += 1
                
            # Otherwise, put the citation as the 'title' and TODO everything else
            else:
                print("NOT VERIFIED: do not add '"+p.title+"' from citation\
                notes", p.citation)

    # TODO
    def make_pandas(self):
        """
        Make a nice pandas database.
        """
        pass

    # TODO
    def read_from_file(self, filename):
        """
        Read in an existing paper database from file.
        """
        pass

    # TODO
    def append_to_file(self, filename):
        """
        Write new database entries to an existing file.
        """
        pass

    # TODO
    def to_file(self, filename):
        """
        Write the database to a file.
        """

        field_delim = "<<"
        element_delim = "@@@"
        firstline_items = ['doi','year','title','author','citation','bibtex',
            'crossref_score','in_spreadsheet','field','original_work',
            'includes_alg','prob_attrs','strategies','notes']

        """
        TODO: Include a thing to check if the filename already has stuff in it,
        and if so, go through and check. For now, the 'w' argument guarantees
        a fresh, blank file.
        """

        with open(filename,'w'):

            file.write(field_delim.join(firstline_items) + element_delim)

            for i in range(len(papers)):
                file.write(field_delim.join(paper[i].to_csv) + element_delim)