import collections
import configparser
import os

from nltk import PorterStemmer
from sty import fg

from inverted_index.db import DictDatabase, DatabaseAbstract
from inverted_index.index import InvertedIndex
from inverted_index.models import Document, Term

import py2neo


class SearchEngine:
    def __init__(self, db: DatabaseAbstract):
        self._db = db
        self._index = InvertedIndex(db)
        self.is_indexed = False

    @staticmethod
    def generate_result(text, url, terms: list):
        for term in terms:
            text = text.replace(term, fg.red + term + fg.rs)
        print(f'URL is {url}')
        print(text)

    @staticmethod
    def get_all_documents():
        CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
        normalized_data_path = os.path.join(os.path.dirname(CURRENT_PATH),
                                            'normalization',
                                            'normalized_data')

        for filename in os.listdir(normalized_data_path):
            with open(os.path.join(normalized_data_path, filename), 'r', encoding='utf-8') as file:
                document_id = int(filename.split('.')[0])
                yield Document(document_id=document_id, tokens=file.read().splitlines())

    def index_documents(self):
        for document in self.get_all_documents():
            self._index.index_document(document)

        self._index.write_to_file()

        self.is_indexed = True

    def process_query(self, query: str) -> dict:
        if not self.is_indexed:
            raise Exception('You need to index documents first')

        porter = PorterStemmer()
        query = porter.stem(query)
        print(query)
        result = self._index.lookup_query(query)
        return result


def generate_result(text, url, terms: list, similarity):
    for term in terms:
        text = text.replace(term, fg.red + term + fg.rs)
    print(f'URL is {url}')
    print(text)
    print(similarity)


def calculate_tf_for_query(tokens):
    tf_text = collections.Counter(tokens)
    for i in tf_text:
        tf_text[i] = tf_text[i] / float(len(tokens))
    return tf_text


def main():
    configuration = configparser.ConfigParser()
    configuration.read(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'configuration'))

    graph = py2neo.Graph(
        f"bolt://{configuration.get('NEO4J', 'host')}:{configuration.get('NEO4J', 'port')}",
        auth=(
            configuration.get('NEO4J', 'username'), configuration.get('NEO4J', 'password')))

    search_term = input("Enter term(s) to search: ")

    porter = PorterStemmer()
    stemmed = [porter.stem(word.lower()) for word in search_term.split()]
    tf = calculate_tf_for_query(stemmed)
    query_tf = []
    for t in tf:
        query_tf.append(f'{t}: {tf[t]}')

    print(','.join(query_tf))


    clauses = [f'EXISTS ((d)-[:HAS_TERM]-(:Term{{word:"{word}"}}))' for word in stemmed]

    # query = f"MATCH (t:Term)-[:HAS_TERM]-(d:Document) WHERE {' AND '.join(clauses)} RETURN DISTINCT id(d), d.original_text, d.url"
    # data = graph.run(query)

    query = f"""
    WITH {{{','.join(query_tf)}}} as query
    MATCH (d:Document)-[rel]-(t:Term) WHERE t.word in keys(query)
    MATCH (d)-[rel1:HAS_TERM]-(:Term)
    WITH reduce(acum = 0.0, n IN collect(rel1)| acum + n.tf_idf^2) AS modA, d, t, rel, query
    WITH d, rel, query, sqrt(modA) as modA, t order by t.word
    WITH d, t, rel.tf_idf as tf_idf, query[t.word]*t.idf as query_tf_idf, modA
    WITH d, modA, collect({{word: t.word, query_tf_idf: query_tf_idf, mult_tf_idf: tf_idf*query_tf_idf}}) as vector
    WITH d, modA, vector, sqrt(reduce(acum = 0.0, n IN vector| acum + n.query_tf_idf)) as modB
    return d.url, d.original_text, reduce(acum = 0.0, n IN vector| acum + n.mult_tf_idf)/(modA*modB) as similarity order by similarity desc
    """
    data = graph.run(query)


    print(query)

    for row in data:
        generate_result(row['d.original_text'], row['d.url'], stemmed, row['similarity'])
    # result = search_engine.process_query(search_term)

    # for term in result.keys():
    #     search_engine.generate_result(term, result)


if __name__ == '__main__':
    main()

# WITH {could: 0.124, record: 0.552, taupey: 0.1} as query, 2.5 as query_mod
# UNWIND keys(query) AS key
# MATCH (t:Term)-[rel]-(d:Document) where t.word=key
# return d.document_id, collect({word: t.word, tf_idf: rel.tf_idf, query: query[t.word]})
# order by d.document_id



# WITH {beauti: 0.2, fashion: 0.4} as query
# MATCH (d:Document)-[rel]-(t:Term) where t.word in keys(query)
# MATCH (d)-[rel1:HAS_TERM]-(:Term)
# WITH reduce(totalAge = 0, n IN collect(rel1)| totalAge + n.tf_idf) AS reduction, d, t, rel, query
# WITH d, rel, query, reduction, t order by t.word
# WITH d, t, rel.tf_idf as tf_idf, query[t.word]*t.idf as query_tf_idf, reduction
# return d.url, sqrt(reduction), collect({word: t.word, query_tf_idf: tf_idf*query_tf_idf})