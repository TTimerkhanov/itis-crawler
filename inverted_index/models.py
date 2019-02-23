class Term:
    """
    Represents the appearance of a term in a given document, along with the
    frequency of appearances in the same one.
    """

    def __init__(self, document_id, frequency):
        self.document_id = document_id
        self.frequency = frequency

    def __repr__(self):
        """
        String representation of the Appearance object
        """
        return str(self.__dict__)


class Document:
    def __init__(self, document_id: int, tokens: list):
        self.document_id = document_id
        self.tokens = tokens
