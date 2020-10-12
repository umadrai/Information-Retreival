# Copyright 2018, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Hannah Bast <bast@cs.uni-freiburg.de>

import re
import sys

class InvertedIndex:
    """ A simple inverted index, as explained in L1. """

    def __init__(self):
        """ Start with an empty index. """

        self.inverted_lists = {}

    def read_from_file(self, file_name):
        """
        Construct from given file.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt")
        >>> sorted(list(ii.inverted_lists.items()))
        [('a', [1, 2]), ('doc', [1, 2, 3]), ('film', [2]), ('movie', [1, 3])]
        """


        with open(file_name) as file:
            record_id = 0
            for line in file:
                record_id += 1
                words = re.split("[^a-zA-Z]+", line)
                for word in words:
                    if (len(word) > 0):
                        word = word.lower()
                        # print(word)
                        if (word not in self.inverted_lists):
                            self.inverted_lists[word] = []
                        if(record_id not in self.inverted_lists[word]):
                            self.inverted_lists[word].append(record_id)
            print(self.inverted_lists)

    def intersect(self, list1, list2):
        """
        >>> ii = InvertedIndex()
        >>> ii.intersect([1, 5, 7], [2, 4])
        []

        >>> ii.intersect([1, 2, 5, 7], [1, 3, 5, 6, 7, 9])
        [1, 5, 7]
        """
        result = []

        i , j =0,0
        while(i < len(list1) and j < len(list2)):
            if(list1[i] == list2[j]):
                result.append(list1[i])
                i+=1
                j+=1
            elif(list1[i] < list2[j]):
                i += 1
            else:
                j += 1
       # print(result)
        return result


    def Process_Query(self, query_Keywords):

        """
        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt")
        >>> ii.Process_Query("")
        []
        
        >>> ii.read_from_file("example.txt")
        >>> ii.Process_Query("doc movie")
        [1, 3]

        >>> ii.read_from_file("example.txt")
        >>> ii.Process_Query("doc movie comedy")
        []
        """

        keywords_List  = []
        result = []
       
        words = re.split("[^a-zA-Z]+", query_Keywords)
        if(len(words) <= 1):
           # print("Not enough words.")
            result = []
            return result
        for keyword in words:
            if(len(keyword) > 0):
                keyword = keyword.lower()
                if(keyword not in keywords_List):
                    keywords_List.append(keyword)
       
        for keyword in keywords_List:
            if (keyword not in self.inverted_lists):
                result = []
                # print("Query Keyword is not in Dictionary, therefore resulted InterSection is " + str(result))                
                return result
            

        for x in range(0, len(keywords_List)-1):
            if(x == 0):
                temp = self.inverted_lists[keywords_List[0]]
            result = self.intersect(temp, self.inverted_lists[keywords_List[x+1]])
            temp = result
        return result
        # print(result)
       


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print("Usage: python3 inverted_index.py <file>")
        sys.exit(1)
    file_name = sys.argv[1]
    ii = InvertedIndex()
    ii.read_from_file(file_name)
    print  ("Inverted Index has been built\n")

    """Process Query Part"""
    while (True):
        input_query = input("Please Enter the keyword query(atleast two words): ")
        if(input_query == "E" or input_query == "e"):
            sys.exit(1)
        result = ii.Process_Query(input_query)
        i = 0
        with open(file_name) as file:
            record_id = 0
            for line in file:
                record_id += 1
                if (i == len(result) or i == 3):
                    break
                if(result[i] == record_id):
                    print (line)
                    i+=1

        print("If you want to exit enter E or e.")
