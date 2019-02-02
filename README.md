# network-similarity

Code and miscellaneous files that I generated in the process of writing my master's thesis. A subset of them can be used as a general package for creating a citation network from a collection of .txt files containing the references of your parent papers in a standard format. There are a lot of extra files, so here's a guide to what's important:

* "Marissa Graham Thesis" PDF in the ThesisClass folder is the final draft.
* "Thesis Presentation" PDF in the main folder is the beamer slides for my defense.
* The "bibliographies" folder contains the reference lists I formatted by hand. The "ref_lists" folder stores the (manually corrected) references for each parent paper in their Paper class format. None of the other .csv or .txt files are necessary to store and load the dataset itself.
* All of the .png files are necessary to compile my thesis and slides. A few of them are only for the slides, but I didn't keep track of which ones they are.
* Getting things to play nice with Google Sheets will involve some JSON files and probably a rabbit hole of googling things if you're not used to API keys. Maybe even if you are. 

Most relevant Mathematica notebooks: 

* "Miscellaneous Figures" (didn't put much effort into documentation since the figures have context in the thesis itself).
* "Subject Tagged Stuff" (good documentation).
* "Full Citation Network Statistics and Visualization" (ok documentation). 

.py files:

* paper.py is a smallish file containing the Paper class for storing the metadata I cared about for each paper, looking up citations in CrossRef, and duplicate testing.
* database.py is the workhorse file with the Database class for creating a database from a collection of reference lists for individual papers by parsing and looking up individual entries in CrossRef, writing spreadsheets of incorrect entries for easier manual correction, updating a database based on manually corrected spreadsheets (both .csv and Google Sheets), writing the citation network the database represents to a GML file, and creating various convenience file dumps and the BibTeX file.
* subject_assignment.py is just a collection of functions which I used to tag papers with a subject based on keywords in the journal titles they were tagged with. Not intended to be part of the main package.

.ipynb files:

* Similarity Scoring Methods and Coupled Node-Edge Similarity Measure were toy implementations of a couple of specific algorithms and aren't relevant to the final thesis.
* Scraping Attempts was very early on, when I found out that you can't just scrape all the references for a DOI number with BeautifulSoup.
* Database Statistics is basic statistics for the database that don't involve the citation network.
* Bibliography Parsing has some remnants of the process of reading and writing .csv files to correct the database, but is mostly the process of tagging subjects via journal titles, and then a bit of scratch work from another class for some reason.

.gml files:
* citation_network.gml is the main citation network dataset used for tables and figures. 
* sciMet_dataset.gml and zewail_dataset.gml are the citation networks I used for comparison to my network. The cited source for these gives them to you in Pajek NET format, which Mathematica didn't recognize, so I loaded them in NetworkX and wrote the GML files myself.
* The rest were either used to generate figures, or created in the process of making figures. See the Miscellaneous Figures Mathematica notebook for details.
* I did not save the specific random networks used to generate figures. In hindsight, those numbers should have been averaged over multiple trials. 

The Paper and Database classes should be usable as-is (the jupyter notebooks have examples of how I'd call them), but I haven't tested them to production-ready level so use at your own risk. 
