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
    Get a single CrossRef item manually for a given citation.
    """
    base_url = "https://api.crossref.org/works?query.bibliographic="
    url = base_url + urllib.parse.quote(citation, errors='surrogateescape')
    response = requests.get(url, timeout=100).json()
    item = response['message']['items'][0]
    return item

def set_property(attribute, item, property):
    """Generic safe dictionary lookup setter."""
    try:
        attribute = item[property]
    except KeyError:
        pass

class Paper:
    """
    Store metadata for a specific paper.

    freeform_citation: lookup info we initialize the paper with

    doi : DOI number, if it exists
    url : DOI in URL form if it exists, generic link otherwise
    year : year of publication
    title : title of paper
    author : "author1 and author2 and author3", etc. TODO: crossref format?
    reference_count : number of references
    citation_count : number of times cited
    subjects : list of subjects given by CrossRef
    verified : Are we sure that our metadata is correct?
    
    item : full CrossRef item thing
    bibtex : nice string to put in BibTeX

    type: original, survey, or application?
    includes_alg : does it include an algorithm?
    prob_attrs : list of problem attributes
    strategies : strategies used in the paper to approach the problem
    notes : any notes I made while reading
    """
    def __init__(self):

        # Initialized with 
        self.freeform_citation = None

        # Can be done either manually or automatically
        self.doi = None
        self.url = None
        self.year = None
        self.title = ""
        self.author = []
        self.reference_count = 0
        self.citation_count = 0
        self.subjects = []
        self.verified = False

        # Non-spreadsheet
        self.item = None
        self.bibtex = None
        
        # Must always be done manually
        self.type = None
        self.includes_alg = False
        self.prob_attrs = []
        self.strategies = []
        self.notes = ""   

    def lookup(self, citation, base_url):
        """
        Look up the citation in CrossRef and assign values accordingly.
        """

        # Make the CrossRef API request
        self.freeform_citation = citation 
        url = base_url + urllib.parse.quote(citation, errors='surrogateescape')
        r = requests.get(url, timeout=100).json()
        self.crossref_item = r['message']['items'][0]

        # Get the straightforward properties
        set_property(self.doi, self.crossref_item, 'DOI')
        set_property(self.url, self.crossref_item, 'URL')
        set_property(self.reference_count, self.crossref_item, 'reference_count')
        set_property(self.citation_count, self.crossref_item, 'citation_count')
        set_property(self.subjects, self.crossref_item, 'subject')
            
        # Get the title
        try:
            self.title = self.crossref_item['title'][0]#.encode('ascii','ignore').decode()
        except KeyError: pass

        # Get the year of publication
        try:
            self.year = self.crossref_item['issued']['date_parts'][0][0]
        except KeyError: pass

        # Get the author list
        try:
            authors = self.crossref_item['author']
            n = len(authors)
            alist = [authors[i]['given']+" "+authors[i]['family'] for i in range(n)]
            self.author = " and ".join(alist)
        except KeyError: pass
    
    def __str__(self):
        """
        Print out in a nice format.
        """
        out = "\nTitle: " + self.title
        out += "\n\tAuthor(s): " + str(self.author)
        out += "\n\tReference count: " + str(self.reference_count)
        out += "\n\tCitation count: " + str(self.citation_count)
        out += "\n\tDOI number: " + self.doi
        out += "\n\tYear of Publication: " + self.year
        out += "\n\tSubject(s): " + self.field
        out += "\n\tType: " + str(self.original_work)
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


    def add_from_spreadsheet(self, sheet, row, bool_inds, str_inds):
        """
        Add the possible entries from the spreadsheet
        """
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


    def add_paper(self, citation, base_url, get_bib=True):
        """
        Add paper to the database and return it.
        """

        p = Paper()
        p.lookup(citation, base_url, get_bib=get_bib)

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

    def make_paper_list(self):
        """
        Convenience function to get a list of all the papers we have a properly
        formatted reference list for.
        """
        with open('allpapers.txt','w') as output:
        
            for i in range(num_papers):

                bibfile = "bibliographies\\database" + str(i+1) + ".txt"

                with open(bibfile) as input:

                    splits = re.split('\[[0-9]+\] ', input.read())
                    head = splits[1].replace('\n',' ').strip(' ')
                    p, unique = self.add_paper(head)

                    output.write(p.title+'\n')

                    for j in range(2,len(splits)):

                        ref = splits[j].replace('\n',' ').strip(' ')
                        print('(', j-1, 'of', len(splits)-2, ')', ref[:80])
                        q, unique = self.add_paper(ref, get_bib=False)
                        output.write(q.title + '\n')

    def concat_bibtxt(self):
        """
        Convenience function to smush all the reference lists together.
        """
        headers_list = []

        with open("ALL_CITATIONS.txt", 'w', errors="surrogateescape") as output:

            for i in range(len(self.bibs)):

                with open(self.bibs[i], errors="surrogateescape") as input:
                    
                    inputstr = input.read()
                    splits = re.split('\[[0-9]+\] ', inputstr)

                    output.write('\nTHIS ONE IS THE HEAD OF THE FILE '+self.bibs[i]+':\n\n')
                    output.write(splits[1])
                    headers_list.append(splits[1])
                    output.write('\nHERE ARE ALL ITS CITED THINGS:\n\n')

                    for j in range(2,len(splits)):
                        output.write(splits[j]+'\n')

        with open("ALL_HAVEBIBS.txt", 'w', errors="surrogateescape") as output:
            for i in range(len(headers_list)):
                output.write(headers_list[i])
                output.write('\n')

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

                    inputstr = input.read()
                    splits = re.split('\[[0-9]+\] ', inputstr)
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
    def read_from_spreadsheet(self, sheet):
        """
        Read the spreadsheet into a database.
        """
        n = sheet.row_count
        col_names = sheet.row_values(1)

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

            if len(sheet.row_values(i)) > 0:
                p = Paper()
                p.add_from_spreadsheet(sheet, i, bool_inds, str_inds)
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
                p = self.add_paper(head)
        
    def update_spreadsheet(self, sheet):
        """
        Update the entries in the spreadsheet with CrossRef entries from the
        existing database.
        """
        col_names = sheet.row_values(1)
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
                    row = sheet.find(p.title).row
                    p.in_spreadsheet = True
                    num_requests += 1
                    
                    if sheet.cell(row, col_inds[0]).value != "TRUE":
                        sheet.update_cell(row, col_inds[0], 'True')
                        num_requests += 1

                        if p.doi is not None:
                            sheet.update_cell(row, col_inds[1], 
                                            self.doi_url + p.doi)
                            num_requests += 1

                        if p.year is not None:
                            sheet.update_cell(row, col_inds[2], p.year)
                            num_requests += 1

                        if p.author is not None:
                            sheet.update_cell(row, col_inds[3], p.author)
                            num_requests += 1


                # Not already in the spreadsheet
                except:

                    # Add known values and TODOS
                    newrow = ['', 'TRUE', '', 'TODO', self.doi_url + p.doi, 
                              p.year, p.author, 'TODO', 'TODO', p.title, 'TODO', 
                              'TODO', '']
                    sheet.append_row(newrow)
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

class Library:
    """
    WE HAVE TO GO DEEPER.
    """

    def __init__(self):
        self.bibs = glob.glob('./bibliographies/*.txt')
        self.base_url = "https://api.crossref.org/works?query.bibliographic="
        self.doi_url = "http://dx.doi.org/"  

        # Get the Google drive spreadsheet
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'client_secret.json', scope)
        client = gspread.authorize(creds)

        self.sheet = client.open("Paper Database").sheet1