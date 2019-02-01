# network-similarity

I went through the PNG files in mid-December and deleted those not actually included in my thesis or defense slides, so there somehow actually needs to be that many. But there are a lot of extra .csv and .gml files, and a few old thesis drafts and miscellaneous unnecessary files I never deleted because it's a lot of work to make sure deleting them won't break things and who knows what random crap will be useful later, so here's a guide to what's important instead of that:

* "Marissa Graham Thesis" PDF in the ThesisClass folder is the final draft
* "Thesis Presentation" in the main folder is the slides for my defense.
* The "bibliographies" folder contains the reference lists I formatted by hand
* The "ref_lists" folder stores the (manually corrected) references for each parent paper in their Paper class format.

Most relevant Mathematica notebooks: 

* "Miscellaneous Figures" (didn't put much effort into documentation since the figures have context in the thesis itself)
* "Subject Tagged Stuff" (good documentation)
* "Full Citation Network Statistics and Visualization" (ok documentation). 

.py files:

* paper.py is a smallish file containing the Paper class for storing the metadata I cared about for each paper, looking up citations in CrossRef, and duplicate testing.
* database.py is the workhorse file with the Database class for creating a database from a collection of reference lists for individual papers by parsing and looking up individual entries in CrossRef, writing spreadsheets of incorrect entries for easier manual correction, updating a database based on manually corrected spreadsheets (both .csv and Google Sheets), writing the citation network the database represents to a GML file, and creating various convenience file dumps and the BibTeX file.
* subject_assignment.py is just a collection of functions which I used to tag papers with a subject based on keywords in the journal titles they were tagged with. Not intended to be part of the main package.

.ipynb files:

* Similarity Scoring Methods and Coupled Node-Edge Similarity Measure were toy implementations of a couple of specific algorithms and aren't relevant to the final thesis
* Scraping Attempts was very early on, when I found out that you can't just scrape all the references for a DOI number with BeautifulSoup
* Database Statistics is basic statistics for the database that don't involve the citation network
* Bibliography Parsing has some remnants of the process of reading and writing .csv files to correct the database, but is mostly the process of tagging subjects via journal titles, and then a bit of scratch work from another class for some reason.

The Paper and Database classes should be usable as-is (the jupyter notebooks have examples of how I'd call them), but I haven't tested them to production-ready level so use at your own risk. 
