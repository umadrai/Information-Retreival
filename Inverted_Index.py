import re
import math
import sys

class InvertedIndex:
	def __init__(self):
	        """
	        Start with empty nverted index.
	        """
	        self.inverted_lists = {}
	        self.length_of_docs = []  # Length of document.
	        self.records = []  # Tuple for storing title and description.


	def read_from_file(self,file_name, b = None, k = None):
		"""
		>>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt", b=0, k=float("inf"))
        >>> r_list = sorted(ii.inverted_lists.items())
		>>> res_list = []
		>>> for title, list in r_list:
		...		res_list.append((title, [(num, '%.3f' %term) for num, term in list]))
		>>> res_list
		... # doctest: +NORMALIZE_WHITESPACE
		[('animated', [(1, '0.415'), (2, '0.415'), (4, '0.415')]),
		 ('animation', [(3, '2.000')]),
		 ('film', [(2, '1.000'), (4, '1.000')]),
		 ('movie', [(1, '0.000'), (2, '0.000'), (3, '0.000'), (4, '0.000')]),
		 ('non', [(2, '2.000')]),
		 ('short', [(3, '1.000'), (4, '2.000')])]
		
        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt", b=0.75, k=1.75)
        >>> r_list = sorted(ii.inverted_lists.items())
        >>> res_list = []
		>>> for title, list in r_list:
		...		res_list.append((title, [(num, '%.3f' %term) for num, term in list]))
		>>> res_list
		... # doctest: +NORMALIZE_WHITESPACE
		[('animated', [(1, '0.459'), (2, '0.402'), (4, '0.358')]),
		 ('animation', [(3, '2.211')]),
		 ('film', [(2, '0.969'), (4, '0.863')]),
		 ('movie', [(1, '0.000'), (2, '0.000'), (3, '0.000'), (4, '0.000')]),
		 ('non', [(2, '1.938')]),
		 ('short', [(3, '1.106'), (4, '1.313')])]
		"""

		if (b == None):	#Setting b and k values
			b = 0.75
			k = 1.75
		else:
			b = b
			k = k
		with open(file_name , encoding ="utf-8") as file:
		    record_id = 0
		    for line in file:
		    	record_id += 1
		    	doc_length = 0
		    	words = re.split("[^a-zA-Z]+", line)
		    	for word in words:
		        	if (len(word) > 0):
		           		word = word.lower()
		           		doc_length += 1
		           		if (word not in self.inverted_lists):
		           			self.inverted_lists[word] = [(record_id, 1)]
		           			continue
		   	       		exist = self.inverted_lists[word][-1] #Checking if record exists
		   	       		if (exist[0] == record_id):	#if True ad 1 in TF
		   	       			self.inverted_lists[word][-1] = (record_id, exist[1] + 1)
		   	       		else:
		           			self.inverted_lists[word].append((record_id, 1))
		    	
		    	#Saving all the records as tuples
		    	self.records.append(tuple(line.split("\t")))
		    	#Length of each record/doc
		    	self.length_of_docs.append(doc_length)
		    	
		   	#Total Documents
		    n = len(self.records)

		    #Average Length
		    avdl = sum(self.length_of_docs)/n

		    #print (b, k)

		    #BM25 Scores implementation
		    for word, inverted_list in self.inverted_lists.items():
		    	for i, (record_id, tf) in enumerate(inverted_list):
		    		doc_length = self.length_of_docs[record_id - 1]
		    		a = 1 - b + (b * doc_length / avdl)		    		
		    		if (k > 0):
		    			tf2 = tf * (1 + (1/k)) / (a + (tf/k))
		    		else:
		    			tf2 = 1
		    		#Document Frequency
		    		doc_freq = len(self.inverted_lists[word])
		    		inverted_list[i] = (record_id, tf2 * math.log(n / doc_freq , 2))
		    		# print(inverted_list)


	def merge(self, list1, list2):
		"""
		>>> ii = InvertedIndex()
        >>> merged = ii.merge([(1, 2.1), (5, 3.2)], [(1, 1.7), (2, 1.3), (6, 3.3)])
        >>> [(title, "%.1f" % term) for title, term in merged]
        [(1, '3.8'), (2, '1.3'), (5, '3.2'), (6, '3.3')]

        >>> merged = ii.merge([(3, 1.7), (5, 3.2), (7, 4.1)], [(1, 2.3), (5, 1.3)])
        >>> [(title, "%.1f" % term) for title, term in merged]
        [(1, '2.3'), (3, '1.7'), (5, '4.5'), (7, '4.1')]
        """
		i , j = 0 , 0
		result = []

		while (i < len(list1) and j < len(list2)):
			if (i < list1[i][0]  and list1[i][0] == list2[j][0]):
				result.append((list1[i][0], list1[i][1] + list2[j][1]))
				i += 1
				j += 1
			elif (list1[i][0] < list2[j][0]):
				result.append(list1[i])
				i += 1
			else:
				result.append(list2[j])
				j += 1
		#Extending remaining lists
		if (i < len(list1)):
			result.extend(list1[i:])
		if (j < len(list2)):
			result.extend(list2[j:])

		return result
		
	def process_query(self, query_Keywords):
		"""
		>>> ii = InvertedIndex()
        >>> ii.inverted_lists = {
        ... "foo": [(1, 0.2), (3, 0.6)],
        ... "bar": [(1, 0.4), (2, 0.7), (3, 0.5)],
        ... "baz": [(2, 0.1)]}
        >>> result = ii.process_query(["foo", "bar"])
        >>> [(title, "%.1f" % term) for title, term in result]
        [(3, '1.1'), (2, '0.7'), (1, '0.6')]
		"""
		query_res = []

		#If user enters nothing
		if (len(query_Keywords) < 0):
			return []

		for keyword in query_Keywords:
			if (keyword in self.inverted_lists):
				query_res.append(self.inverted_lists[keyword])

		if (len(query_res) == 0):
			return []

		#Assigning first value to compute the merge with remaining
		merged = query_res[0]
		for i in range(1, len(query_res)):
			merged = self.merge(merged, query_res[i])

		# Filtering out 0 BM25 scores in list
		filter_merged = []
		for tuplee in merged:
			if (tuplee != 0):
				filter_merged.append(tuplee)
		# print(filter_merged)
		sorted_result = sorted(filter_merged, key = lambda rec:rec[1], reverse = True)
		return 	sorted_result


	def render_output(self, result, keywords, k=3):
	        """
	        Renders the output for the top-k of the given record_ids. Fetches the
	        the titles and descriptions of the related records and highlights
	        the occurences of the given keywords in the output, using ANSI escape
	        codes.
	        """

	        # Compile a pattern to identify the given keywords in a string.
	        #p = re.compile('\\b(' + '|'.join(keywords) + ')\\b', re.IGNORECASE)

	        # Output at most k matching records.
	        for i in range(min(len(result), k)):
	        	record_id, term_freq = result[i]
	        	title, desc = self.records[record_id - 1]  # ids are 1-based.

	            # Highlight the keywords in the title in bold and red.
	        	#title = re.sub(p, "\033[0m\033[1;31m\\1\033[0m\033[1m", title)

	            # Print the rest of the title in bold.
	        	#title = "\033[1m%s\033[0m" % title

	            # Highlight the keywords in the description in red.
	        	#desc = re.sub(p, "\033[31m\\1\033[0m", desc)

	        	print("\n%s\n%s" % (title, desc))

	        print("\n# total hits: %s." % len(result))

if __name__ == "__main__":

	if (len(sys.argv) < 2):
		print ("Usage: python3 inverted_index.py <file> [Optional:<b> <k>] ")
		sys.exit()

	file_name = sys.argv[1]
	if (len(sys.argv) > 2):
		b = float(sys.argv[2])
		k = float(sys.argv[3])
	else:
		b = None
		k = None

	print("Reading from file  '%s' ." %file_name) 
	ii = InvertedIndex()
	ii.read_from_file(file_name)

	print("Inverted Index, BM25 Scores calculated.\n")

	while (True):
	 	input_query = input("Please Enter the keyword query: ")

	 	keywords = [x.lower().strip() for x in re.split("[^A-Za-z]+", input_query)]
	 	print(keywords)
	 	result	= ii.process_query(keywords)
	 	#print(result)
	 	ii.render_output(result, keywords)