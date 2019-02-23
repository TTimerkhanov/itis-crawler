from abc import ABC, abstractmethod

from inverted_index.models import Document


class DatabaseAbstract(ABC):
    @abstractmethod
    def get(self, pk: int):
        """
        Get document by primary key
        :param pk:
        :return: document
        """
        pass

    @abstractmethod
    def add(self, document: Document):
        """
        Adds a document to the DB.
        :param document:
        :return:
        """
        pass

    @abstractmethod
    def remove(self, document: Document):
        """
        Removes document from DB.
        :param document:
        :return:
        """
        pass


class DictDatabase(DatabaseAbstract):
    """
    In memory database representing the already indexed documents.
    """

    def __init__(self):
        self.db = dict()

    def __repr__(self):
        """
        String representation of the Database object
        """
        return str(self.__dict__)

    def get(self, id):
        return self.db.get(id, None)

    def add(self, document):
        return self.db.update({document.document_id: document})

    def remove(self, document):
        return self.db.pop(document.document_id, None)
