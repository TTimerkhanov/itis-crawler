import os

from scrapy.utils.project import data_path

from inverted_index.db import DictDatabase, DatabaseAbstract
from inverted_index.index import InvertedIndex
from inverted_index.models import Document, Term


class SearchEngine:
    def __init__(self, db: DatabaseAbstract):
        self._db = db
        self._index = InvertedIndex(db)
        self.is_indexed = False

    @staticmethod
    def generate_result(term: str, result: dict):
        document_ids = {}
        for document in result[term]:
            print(document)
            # pass

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

        result = self._index.lookup_query(query)
        return result


def main():
    db = DictDatabase()
    search_engine = SearchEngine(db)

    search_engine.index_documents()

    # search_term = raw_input("Enter term(s) to search: ")
    search_term = 'python'
    result = search_engine.process_query(search_term)

    for term in result.keys():
        search_engine.generate_result(term, result)
        for document in result[term]:
            pass
            # Belgium: { docId: 1, frequency: 1}
            document = db.get(document.document_id)
            # print(highlight_term(document.document_id, term, ""))
        print("-----------------------------")


if __name__ == '__main__':
    main()
