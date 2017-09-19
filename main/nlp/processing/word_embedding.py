#!/usr/bin/env python

"""word embeddings using Googles word2vec"""

import gensim
import numpy as np
from main.nlp.preprocessing.tokenizer import tokenizer_sentence

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


class MySentences(object):
    """
    A class for itterating in text lines from a directory on line at a time, this requires the text to be preprocessed
    to 1 sentence per line.
    """

    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        for line in open(self.filename, encoding='utf-8', errors='ignore'):
            yield line.split()


class WordEmbedding(object):
    """
    A simple wrapper for gensim's word2vec word embedder, this maps similar words together in vector space where their
    similarity is determined by their use within a single sentence.
    """

    def __init__(self):

        self.model = None
        self.sorted_model_array = []
        self.labels = []

    def load_word2vec_model(self, filename):
        """
        Load in pre trained embeddings

        :param filename: filepath to embeddings (.bin)
        """

        self.model = gensim.models.Word2Vec.load_word2vec_format(filename,
                                                                 binary=True)

    def create_word2vec_model(self, filename, workers=4, min_count=5, size=200):
        """
        Trains the model

        :param filename: The file containing a series of sentences with 1 sentence per line to be used as a corpus
        for the model
        :param min_count: Integer, the minimum number of times a word can appear in the corpus to be considered
        :param workers: Integer, the number of cores to be used for processing, word2vec uses cython for this
        :param size: Integer, the size of the vector space
        """

        sentences = MySentences(filename)
        self.model = gensim.models.Word2Vec(sentences, workers=workers, min_count=min_count, size=size)

        return True

    def create_key_vector_pairings(self):
        """
        Populates two arrays:
        sorted_model_array - an array of n-dimentional vectors where each vector is a word in the word embeddings space
        labels - an array of words corresponding to the sorted_model_array, liked by implicit index
        """

        for key in self.model.vocab:
            self.sorted_model_array.append(self.model[key])
            self.labels.append(key)

        return True


def snippets_to_file(snippet_series, folder):
    """
    Write snippet_series to file to be used to create embeddings, does not preprocess, preferably use other method

    :param snippet_series List, pandas Series, series of snippets
    :param folder: Str, folder name
    """

    array_of_arrays = snippet_series.apply(lambda e: tokenizer_sentence(e)).tolist()
    array = [item for sublist in array_of_arrays for item in sublist]

    lengths_of_snippets = [len(snippet) for snippet in array_of_arrays]
    indexes = np.arange(0,len(lengths_of_snippets)).tolist()
    list_of_indexes = [[b] * a for a, b in zip(lengths_of_snippets, indexes)]
    list_of_indexes = [el for lists in list_of_indexes for el in lists]

    with open(folder+ '/text.txt', 'w', encoding='utf-8') as thefile:
        for line in array:
            thefile.write(str(line + '\n'))
    with open(folder+ '/ids.csv', 'w', encoding='utf-8') as thefile:
        for element in list_of_indexes:
            thefile.write(str(element) + '\n')

    return True


def sentences_to_file(sentence_array, folder):
    """
    Write array of sentences to file to be used to create embeddings, manually preprocess beforehand

    :param sentence_array: List, array of strings where the strings are sentences
    :param folder: Str, folder name
    """

    with open(folder+ '/text.txt', 'w', encoding='utf-8') as thefile:
        for line in sentence_array:
            thefile.write(str(line + '\n'))

    return True
