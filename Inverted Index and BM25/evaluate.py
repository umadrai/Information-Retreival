import re
import sys

from test import  InvertedIndex

class Evaluation:

	def read_benchmark(self, file_name):
		"""
		>>> eval = Evaluation()
        >>> benchmark = eval.read_benchmark("ex_bench.txt")
        >>> sorted(benchmark.items())
        [('animated film', {1, 3, 4}), ('short film', {3, 4})]
		"""
		benchmark_query = {}

		with open(file_name, encoding = 'utf-8') as file:
			for line in file:
				query, labels = line.strip().split("\t")
				#print(query , labels)
				benchmark_query[query] = {int(x) for x in labels.split(" ")}
		return benchmark_query	

	def precision_at_k(self, result_ids, relevant_docs, k ):
		"""
		>>> eval = Evaluation()
		>>> eval.precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, 2)
		0.5
		>>> eval.precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, 4)
		0.75
        """
		relevant_results = 0
		if (k == 0):
			return 0

		for i in range(0, min(len(result_ids), k)):
			if result_ids[i] in relevant_docs:
				relevant_results += 1
		relevant_results /= k
		#print(relevant_results)
		return	relevant_results

	def average_precision(self, result_ids, relevant_docs):
		"""
		>>> eval = Evaluation()
		>>> eval.average_precision([7, 17, 9, 42, 5], {5, 7, 12, 42})
		0.525
		"""
		total_avg_prec = 0

		for i in range(0, len(result_ids)):
			if result_ids[i] in relevant_docs:
				total_avg_prec += self.precision_at_k(result_ids, relevant_docs, i + 1)
				# print(total_avg_prec)
		total_avg_prec /= len(relevant_docs)
		return total_avg_prec

	def evaluate(self, inverted_index, benchmark_query):
		"""
		>>> ii = InvertedIndex()
		>>> ii.read_from_file("example.txt")
		>>> eval = Evaluation()
		>>> b = eval.read_benchmark("ex_bench.txt")
		>>> values = eval.evaluate(ii , b)
		>>> res = []
		>>> for val in values:
		...		res.append(round(val, 3))
		>>> res
		[0.667, 0.833, 0.694]
		"""
		no_of_queries = len(benchmark_query)
		total_avg_p = 0
		total_p3 = 0
		total_pr = 0

		for query, relevant_docs in benchmark_query.items():
			#print(query, relevant_docs)
			#print("Processing.")
			doc_ids = []
			r = len(relevant_docs)
			keywords = [x.lower().strip() for x in re.split("[^a-zA-Z]+", query)]
			for doc_id in inverted_index.process_query(keywords):
				doc_ids.append(doc_id[0])
			# print(keywords)
			# print(doc_ids)

			precision_at_3 = self.precision_at_k(doc_ids, relevant_docs, 3)
			total_p3 += precision_at_3
			# print(precision_at_3)
			precision_at_r = self.precision_at_k(doc_ids, relevant_docs, r)
			total_pr += precision_at_r
			# print(precision_at_r)

			avg_precision = self.average_precision(doc_ids, relevant_docs)
			total_avg_p += avg_precision
			# print(avg_precision)

			mean_p_3 = total_p3 / no_of_queries
			mean_p_r = total_pr / no_of_queries
			mean_avg_p = total_avg_p / no_of_queries

		return mean_p_3, mean_p_r, mean_avg_p

if __name__ == '__main__':

	if len(sys.argv) < 3:
		print("Usage: python3 evaluate.py movies.txt benchmark.txt")
		sys.exit()

	file_name = sys.argv[1]
	benchmark_file = sys.argv[2]

	print("Reading and creating Indexes.")

	ii = InvertedIndex()
	ii.read_from_file(file_name)

	print("Indexes has been built. Now Reading benchmark file.")
	eeval = Evaluation()
	benchmark_queries = eeval.read_benchmark(benchmark_file)

	values = eeval.evaluate(ii, benchmark_queries)

	print("Results:")
	print("Mean Precision at 3 = %s" % round(values[0], 3))
	print("Mean Precision at R =%s" % round(values[1], 3))
	print("Mean Average Precision =%s" % round(values[2], 3))