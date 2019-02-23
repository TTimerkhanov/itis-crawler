import os

from inverted_index.models import Term, Document


class InvertedIndex:
    """
    Inverted Index class.
    """

    def __init__(self, db):
        self.index = dict()
        self.db = db

    def __repr__(self):
        """
        String representation of the Database object
        """
        return str(self.index)

    def write_to_file(self):
        CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(CURRENT_PATH, 'index.txt'), 'w', encoding='utf-8') as output:
            for value, data in self.index.items():
                documents = [document.document_id for document in data]
                output.write(f'{value}: {documents}\n')

    def index_document(self, document: Document):
        """
        Process a given document, save it to the DB and update the index.
        """

        appearances_dict = dict()
        # Dictionary with each term and the frequency it appears in the text.
        for term in document.tokens:
            term_frequency = appearances_dict[term].frequency if term in appearances_dict else 0
            appearances_dict[term] = Term(document_id=document.document_id,
                                          frequency=term_frequency + 1)

        # Update the inverted index
        update_dict = {}
        for (key, appearance) in appearances_dict.items():
            if key in self.index:
                update_dict[key] = self.index[key] + [appearance]
            else:
                update_dict[key] = [appearance]

        self.index.update(update_dict)
        # Add the document into the database
        self.db.add(document)
        return document

    def lookup_query(self, query):
        """
        Returns the dictionary of terms with their correspondent Documents.
        This is a very naive search since it will just split the terms and show
        the documents where they appear.
        """
        return {term: self.index[term] for term in query.split(' ') if term in self.index}
