import string

import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
import os

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class IndexedText(object):

    def __init__(self, tokens, stemmer=PorterStemmer()):
        self._tokens = tokens
        self._stemmer = stemmer

    def stem(self):
        return [self._stemmer.stem(t) for t in self._tokens]


def write_normalized_file(filename, words):
    with open(os.path.join(CURRENT_PATH, 'normalized_data', filename), 'w', encoding='utf-8') as f:
        for word in words:
            f.write(f'{word}\n')


def normalize_data():
    data_path = os.path.join(os.path.dirname(CURRENT_PATH), 'scrapper', 'data')
    for filename in os.listdir(data_path):
        if not filename.startswith('.'):
            with open(os.path.join(data_path, filename), 'r', encoding='utf-8') as file:
                raw = file.read()
                # Remove punctuation
                translator = str.maketrans('', '', string.punctuation)
                raw = raw.translate(translator)
                # Tokenize text
                tokens = word_tokenize(raw)
                # Convert all tokens to lowercase
                tokens = [w.lower() for w in tokens]
                # Remove stop words
                stop_words = set(stopwords.words('english'))
                filtered_tokens = [w for w in tokens if w not in stop_words]

                # Remove remaining tokens that are not alphabetic
                filtered_tokens = [word for word in filtered_tokens if word.isalpha()]

                porter = PorterStemmer()

                index = IndexedText(filtered_tokens, porter)
                stemmed = index.stem()

                write_normalized_file(filename, stemmed)


if __name__ == '__main__':
    # Install punktr if needed
    # nltk.download()
    nltk.download('stopwords')

    normalize_data()
