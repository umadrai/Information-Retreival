import re
import sys
import sqlite3
import time


class SPARQL:
    """ A simple SPARQL engine for a SQLite backend. """

    def __init__(self):
        """
        Creates a new SPARQL engine.
        """
        # A pattern to parse the triples in the WHERE clause of a SPARQL query.
        # Assumes that all strings are surrounded by quotation marks (").
        self.triple_pattern = re.compile(
            '\\s?(\\?[^\\s]+|"[^"]+")\\s+("[^"]+")\\s+(\\?[^\\s]+|"[^"]+")'
        )

    def sparql_to_sql(self, sparql):
        """
        Translates the given SPARQL query to a corresponding SQL query.

        TODO: Implement test case(s).
        """
        # Transform all letters to lower cases.
        sparqll = sparql.lower()

        # Find all variables in the SPARQL between the SELECT and WHERE clause.
        select_start = sparqll.find("select ") + 7
        select_end = sparqll.find(" where", select_start)
        variables = sparql[select_start:select_end].split()

        # Find all triples between "WHERE {" and "}"
        where_start = sparqll.find("{", select_end) + 1
        where_end = sparqll.rfind("}", where_start)
        where_text = sparql[where_start:where_end]
        triple_texts = where_text.split(".")
        triples = []

        # print(select_start, select_end, variables, where_start, where_text,where_end)
        for triple_text in triple_texts:
            m = self.triple_pattern.match(triple_text)
            subj = m.group(1).strip('"')
            pred = m.group(2).strip('"')
            obj = m.group(3).strip('"')
            triples.append((subj, pred, obj))

        # Find the (optional) LIMIT clause.
        limit_start = sparqll.find(" limit ", where_end)
        limit = sparql[limit_start + 7:].strip() if limit_start > 0 else None
        # print(limit)
        # print(triple_texts, triples, limit_start, limit, subj, pred, obj)

        # TODO: Compose the SQL query and return it.
        # Creating FROM Clause
        from_clause = ""
        copies_names = []
        where_clause = []
        where = ""
        
        for i in range(len(triples)):
            copies_names.append("f_" + str(i+1))
            if i == (len(triples) - 1):
                from_clause += ("wikidata " + " AS " + copies_names[i])
            else:    
                from_clause += ("wikidata " + " AS " + copies_names[i] + " , ")
        # print(from_clause)

        # Keeping tracks of variables and they occurences using dict
        # Adding variables to dict and appending where clause
        # print(copies_names)
        var_dict = dict((k, []) for k in variables)
        for i in range(len(triples)):
            subject = triples[i][0]
            predicate = triples[i][1]
            objectt = triples[i][2]
            # print(subject,predicate,objectt)
            if subject[0] == "?":
                if subject not in var_dict:
                    var_dict[subject] = []
                var_dict[subject].append(copies_names[i] + ".subject")
            else:
                where += copies_names[i] + ".subject = \"" + subject + "\""
                where_clause.append(where)
                where = ""

            if objectt[0] == "?":
                if objectt not in var_dict:
                    var_dict[objectt] = []
                var_dict[objectt].append(copies_names[i] + ".object")
            else:
                where += copies_names[i] + ".object = \"" + objectt + "\""
                where_clause.append(where)
                where = ""
        # SELECT ?x ?y WHERE { ?x "occupation" "politician" . ?x "country of citizenship" "Germany" . ?x "spouse" ?y . ?x "place of birth" ?z . ?y "place of birth" ?z }
        # SELECT ?x ?y WHERE { ?x "occupation" "politician" . ?x "country of citizenship" "Germany" . ?x "spouse" ?y . ?x "place of birth" ?z . ?y "place of birth" ?z }
        # print(var_dict)

        # Making select clause variables for SQL 
        query_var_part = ""
        for i in range(len(variables)):
            if i == (len(variables) - 1):
                query_var_part += (var_dict[variables[i]][0] + " ")    
            else:
                query_var_part += (var_dict[variables[i]][0] + " , ")

        # Completing Where Clause, checking equalities and appending
        where = ""
        for i in range(0, len(triples)):
            where += copies_names[i] + ".predicate = \"" + triples[i][1] + "\""
            where_clause.append(where)
            where = ""

            for j in range(i+1, len(triples)):
                where = ""
                if triples[i][0] == triples[j][0]:
                    where += copies_names[i] + ".subject = " + copies_names[j] + ".subject"
                    # print(where)
                    where_clause.append(where)
                    where = ""
                if triples[i][0] == triples[j][2]:
                    where += copies_names[i] + ".subject = " + copies_names[j] + ".object"
                    # print(where)
                    where_clause.append(where)
                    where = ""
                if triples[i][2] == triples[j][0]:
                    where += copies_names[i] + ".object = " + copies_names[j] + ".subject"
                    # print(where)
                    where_clause.append(where)
                    where = ""
                if triples[i][2] == triples[j][2]:
                    where += copies_names[i] + ".object = " + copies_names[j] + ".object"
                    # print(where)
                    where_clause.append(where)
                    where = ""

        #Final Where Clause
        final_where_clause = " AND ".join(where_clause)
        # print(final_where_clause)

        # Making limit clause
        limit_clause = ""
        if limit is not None:
            limit_clause += " LIMIT " + limit

        sql_query = "SELECT " + query_var_part + "FROM " + from_clause + " WHERE " + final_where_clause + limit_clause + ";"
        print("SQL Query: " + sql_query + "\n")
        
        return sql_query

    def process_sql_query(self, db_name, sql):
        """
        Runs the given SQL query against the given instance of a SQLite3
        database and returns the result rows.

        TODO: Implement test case(s).
        """
        # TODO: Run the SQL query against the database and return the result.
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(sql)
        results = c.fetchall()

        return results


if __name__ == '__main__':
    # TODO: Read the path to the SQLite3 database from the command line.
    if len(sys.argv) <= 1:
        print("Usage: python3 sparql_to_sql.py <db_name>")
        exit(1)

    db_name = sys.argv[1]

    engine = SPARQL()

    while (True):
        # Read the SPARQL query to process from the command line.
        sparql = input("Enter SPARQL query: ")

        # Translate the SPARQL query to an SQL query.
        # try:
        sql = engine.sparql_to_sql(sparql)
        # except Exception:
        #     print("Syntax error...")
        #     sys.exit(1)
        # sql = "SELECT subject FROM wikidata limit 20;"
        start_time = time.time()
        results = engine.process_sql_query(db_name, sql)
        end_time = time.time()


        # TODO: Run the SQL query against the database.
        # TODO: Output the result rows.
        for row in results:
            print("\t".join(row))

        print("Total time taken: " + str(end_time - start_time))
    # SELECT ?p1 ?p2 ?f WHERE { ?p1 "acted_in" ?f . ?p2 "acted_in" ?f . ?p1 "married_to" ?p2 }
    # for i in range(len(triples)):
    #         if i == (len(triples) - 1):
    #             from_clause += (triples[i][1] + " AS f_%s " % str(i+1))
    #         else:    
    #             from_clause += (triples[i][1] + " AS f_%s , " % str(i+1))
    # SELECT f_1.subject , f_2.subject , f_1.object FROM acted_in AS f_1 , acted_in AS f_2 , married_to AS f_3 WHERE f_1.object = f_2.object AND f_1.subject = f_3.subject AND f_2.subject = f_3.object
    # SELECT f_1.actor , f_2.actor , f_1.film FROM acted_in AS f_1 , acted_in AS f_2 , married_to AS f_3 WHERE f_1.film = f_2.film AND f_1.actor = f_3.person1 AND f_2.actor = f_3.person2
    # SELECT ?p1 WHERE { ?p1 "acted_in" ?f } limit 20
    # sql_query = sparql_to_sql(
    # SELECT ?x ?y WHERE { ?x "occupation" "politician" . ?x "country of citizenship" "Germany" . ?x "spouse" ?y . ?x "place of birth" ?z . ?y "place of birth" ?z }
    # Select ?x where { ?x "country of citizenship" "Germany" . ?x "sex or gender" "female" }


    # Query for ex 2:
    # Select ?x ?y where { ?x "country of citizenship" "Germany" . ?x "sex or gender" "female" . ?x "educated at" ?y . ?x "occupation" "computer scientist"}
