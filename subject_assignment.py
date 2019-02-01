import paper
import database
import numpy as np

from collections import defaultdict
"""
Notes
- This needs to be a separate thing from database? Not part of the main package
- Maybe same thing for the .csv and .gml writing and so on? idk
- How to integrate this into my graph objects?

Functions needed:
- Clear any Paper values of "subject" that are a list 
	* This removes the possibility of clearing mine, since they'll be a set
	* Ignores NoneTypes, as desired
	* Should requite the least modification of the initial setup
	* Potential problems: Does eval(thing) work on sets? 
- Go through Papers and tag by subject(s) according to their container-title
"""

def initialize_journals(db, verbose=False):
	"""Get an initial set of container-titles from the database."""
	with_container = 0
	without_container = 0
	journals = defaultdict(set)

	for p_hash, p in db.all_papers.items():
		if p.container_title is not None:
			for title in set(p.container_title):
				journals[title] = set()
			with_container += 1
		else:
			without_container += 1

	if verbose:
		print("Number of papers with a container-title:", with_container)
		print("Number of papers without a container-title:", without_container)
		print("Number of unique container titles:", len(journals))
	return journals

def get_wordlists():
	""" Store the wordlists and make the topic_words dictionary. """

	CS = {'ACM', 'IEEE', 'Computer Science', 'Artificial Intelligence',
		'Pattern Recognition', 'Computer Vision', 'Machine Learning',
		'Signal Processing', 'Electrical Engineering', 'Image Processing',
		'Data Mining', 'Neural Networks', 'Computer Graphics', 'Graphics',
		'Language Processing', 'Internet', 'Intelligent Systems',
		'Robotic','Data','Software', 'Machine Vision', 'Image Analysis',
		'Scientific Computing', 'SIAM', 'Malware','World Wide Web', 
		'Computational Intelligence', 'Computational Linguistics',
		'Computational linguistics','Algorithm','Computer','ITiCSE',
		'ITICSE','Machine learning','Learning','learning',
		'Artificial intelligence','CIVR','Document Analysis'}

	bio = {'Biology', 'Microbiology', 'Molecular', 'Medical', 'Biological',
		'Cancer', 'Genome', 'Bioinformatics', 'Protein', 'Biocomputing',
		'Biomedical', 'biology', 'Medicine', 'Biosystems', 'Virology',
		'Brain', 'Psychology', 'Genetics', 'Bioengineering', 'Cell',
		'Cardiology', 'Metabolic', 'Biotechnology', 'Pathogens',
		'Pathology', 'Plant', 'PLANT', 'Virus', 'Drug','Medicinal',
		'Neuro','Psych',
		'Genomic','Diseases','Endocrinology', 'Epidemiology',
		'Proteom','Biochem', 'DNA', 'Pharma', 'Biomedic', 'biomedica',
		'Neurobiological'}

	math = {'Mathemati','Markov','Probability','Algebra','Network',
		'Topology','Optimization', 'Geometr','Statistic','Algorithm',
		'Graph ','Graphs','Combinatori','Riemann Surfaces','Permutation Groups',
		'Functional Analysis', 'SIAM','Fixed Point','Wavelet','Statistics',
		'Linear Regression','Fractal','geometry','Multivariate','Chaos',
		'mathemati','Kernel'}

	linguistics = {}

	computer_vision = {}

	chemistry = {}

	physics = {}

	# Rename "Computer Vision" to "Image Processing"?
	topic_names = ['Computer Science','Biology','Mathematics','Chemistry',
		'Physics','Computer Vision','Natural Language Processing']
	topics = [CS, bio, math]#, linguistics, computer_vision, chemistry, physics]

	return {topic_names[i]:topics[i] for i in range(len(topics))}

def check_words(title, wordlist, verbose=False):
	"""Helper function to check if any words in wordlist are in title."""
	for word in wordlist:
		if title.find(word) >= 0:
			if verbose:
				print("\t\tFOUND '"+word+"' IN:", title)
			return True
	return False

def tag_journals(db, journals, topics, verbose=False):

	is_topic = defaultdict(set)

	for journal in journals.keys():
		for topic, topic_words in topics.items():
			if check_words(journal, topic_words):
				journals[journal].add(topic)
				is_topic[topic].add(journal)
	
	if verbose:

		topic_assigned = set().union(*is_topic.values())
		print("Total number of journals:", len(journals))
		print("Number of journals assigned a topic:", len(topic_assigned))
		print("Number of journals with no topic assigned:", 
			len(journals) - len(topic_assigned))
		for topic in topics.keys():
			print("\tNumber of '"+topic+"':", len(is_topic[topic]))

	return journals, is_topic

def clear_subjects(db):
	"""Clear the current values of 'subject' for papers in the database."""
	
	for p_hash, p in db.all_papers.items():
		if p.subject:
			p.subject = None

def tag_papers(db, journals, topics, verbose=False):
	"""Assign subject values to papers based on their container title."""

	papers_by_topic = defaultdict(set)

	for p_hash, p in db.all_papers.items():

		# If we have journal information for this paper
		if p.container_title:

			# Collect all topics for each journal the paper was published in
			subjects = set().union(*[journals[j] for j in p.container_title])

			# If nontrivial, assign that info to p.subject and papers_by_topic
			if len(subjects) > 0:
				p.subject = subjects

				for subject in subjects:
					papers_by_topic[subject].add(p_hash)

	if verbose:

		topic_assigned = set().union(*papers_by_topic.values())
		print("Total number of papers:", len(db.all_papers))
		print("Number of papers assigned a topic:", len(topic_assigned))
		print("Number of papers with no topic assigned:", 
			len(db.all_papers) - len(topic_assigned))
		for topic in topics.keys():
			print("\tNumber of '"+topic+"':", len(papers_by_topic[topic]))

	return papers_by_topic

def check_intersections(db, topics, papers_by_topic):
	"""See how many papers are in combinations of categories."""

	# Print the distribution of "number of topics"
	num_subjects = []
	for p_hash, p in db.all_papers.items():
		if p.subject:
			num_subjects.append(len(p.subject))
		else:
			num_subjects.append(0)
	num_subjects = np.array(num_subjects)

	for i in range(np.max(num_subjects)+1):
		print("Number of papers with", i, "topics:", 
			len(np.where(num_subjects==i)[0]))

	# Figure out what's going on with triple-tagged guys (nothing weird)
	"""
	for p_hash, p in db.all_papers.items():
		if p.subject:
			if len(p.subject) > 2:
				print("\n",p.title,"\n\t",p.container_title,"\n\t", p.subject)
				
				for topic, topic_words in topics.items():
					print("\tCheck against '" + topic + "':")
					for journal in p.container_title:
						check_words(journal, topic_words, verbose=True)
	"""

	# Look in more detail at double-tagged guysfor p_hash, p in db.all_papers.items():
	combos = defaultdict(int)
	for p_hash, p in db.all_papers.items():
		if p.subject:
			if len(p.subject) == 2:
				combos[frozenset(p.subject)] += 1
				#print("\n",p.title,"\n\t",p.container_title,"\n\t", p.subject)
				if p.subject == {'Computer Science', 'Biology'}:
					#print("\n",p.title,"\n\t",p.container_title)#,"\n\t", p.subject)
					
					
					bio_words = set()
					CS_words = set()
					for journal in p.container_title:
						for word in topics['Biology']:
							if journal.find(word) >= 0:
								bio_words.add(word)
						for word in topics['Computer Science']:
							if journal.find(word) >= 0:
								CS_words.add(word)

					#print("\tBiology words:", bio_words)
					#print("\tCS words:", CS_words)
	
	for k, v in combos.items():
		print(k, v)

# We're using a different version of the citation network writer function,
# because I want it in here. The preprocess and edge functions don't need to
# be different, so we'll just call them. 
# We need our own citation_network as well, since we want to call our own 
# version of add_node

def get_to_read_hashes():
	hashes = []
	with open('to_read_hashes.txt') as f:
		for line in f:
			hashes.append(eval(line.strip('\n')))
	return hashes

def add_node(db, p, p_hash, output, nodes, hashes):
		
	if p_hash not in nodes:
		
		nodes[p_hash] = len(nodes) + 1

		out = '\n\tnode [ \n'
		out += '\t\tid ' + str(nodes[p_hash]) + '\n'
		out += '\t\ttitle "' + db.preprocess(p.title) + '"\n'
		out += '\t\tyear ' + str(p.year) + '\n'
		out += '\t\treferenceCount ' + str(p.reference_count) + '\n'
		out += '\t\tcitationCount ' + str(p.is_referenced_by_count) + '\n'

		if p_hash in hashes:
			out += "\t\ttoRead 1.0\n"
		else:
			out += "\t\ttoRead 0.0\n"

		subj_out = ""
		is_CS, is_bio, is_math = '0.0', '0.0', '0.0'
		is_CS_bio, is_CS_math, is_bio_math = '0.0', '0.0', '0.0'

		if p.subject:
			if 'Computer Science' in p.subject:
				is_CS = '1.0'
				subj_out += '1'
			if 'Biology' in p.subject:
				is_bio = '1.0'
				subj_out += '2'
			if 'Mathematics' in p.subject:
				is_math = '1.0'
				subj_out += '3'
			out += '\t\tsubject "' + subj_out + '"\n'
		else:
			out += '\t\tsubject "0"\n'

		# Test by if you're EITHER of two properties
		if is_CS == '1.0' or is_bio == '1.0':
			is_CS_bio = '1.0'
		if is_CS == '1.0' or is_math == '1.0':
			is_CS_math = '1.0'
		if is_bio == '1.0' or is_math == '1.0':
			is_bio_math = '1.0'

		out += '\t\tisCSBio ' + is_CS_bio + '\n'
		out += '\t\tisBioMath ' + is_bio_math + '\n'
		out += '\t\tisCSMath ' + is_CS_math + '\n'
		out += '\t\tisCS ' + is_CS + '\n'
		out += '\t\tisBio ' + is_bio + '\n'
		out += '\t\tisMath ' + is_math + '\n'
		out += '\t]\n'
		
		output.write(out)

def citation_network(db, filename, max_edges=1e6):
	"""
	Write the citation network to a .gml file.
	"""
	nodes = dict()
	edges = set()
	num_edges = 0

	hashes = get_to_read_hashes()

	with open(filename, 'w', errors='backslashreplace') as f:

		f.write("graph [\n\tdirected 1\n")

		for parent_hash, ref_list in db.parents.items():

			if len(ref_list) > 0:

				add_node(db, db.all_papers[parent_hash], parent_hash, f, nodes, hashes)
				
				for child in ref_list:

					add_node(db, child, child.hash, f, nodes, hashes)

					source_id = nodes[parent_hash]
					target_id = nodes[child.hash]
					db.add_edge(source_id, target_id, f, nodes, edges)
					num_edges += 1

					if num_edges > max_edges:
						print("MAX EDGES REACHED", num_edges, len(nodes))
						f.write("]")
						return

		print(num_edges, "edges written with max_edges =", max_edges)
		f.write("]")