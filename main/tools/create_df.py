#!/usr/bin/env python

"""Creates a fully customizable dummy pandas dataframe to test solution on. The dataframe is a collection of column
classes, if there is a datatype you would like to include, please add a new class"""

import pandas as pd
import numpy as np
import random

from nltk.corpus import brown

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def DF(column_list=None, n_records=50):
    """
    Main function to import, it creates the dummy pandas dataframe

    :param column_list: a list of dictionaries, each dictionary requires the following elements:
        type: a string refering to a class name (see below for available classes)
        name: a unique name to id the column
        n_itters: integer dictating how many versions of this column you want (named name1, name2 etc)
        args: dictionary of class specific arguments to fine tune the column type
    :param n_records: number of records to be generated

    :return: pandas df
    """

    if not column_list:
        column_list = [{'type': 'Number', 'name': 'Test N', 'n_itters': 1, 'args': {}}]

    column_outputs = []
    for col_set in column_list:
        ctype = col_set['type']
        for i in range(col_set['n_itters']):

            if col_set['n_itters'] == 1:
                name = col_set['name']
            else:
                name = col_set['name'] + str(i)
                
            class_name = globals()[ctype]
            column_i = class_name(name, n_records, col_set['args'])
            column_outputs.append(column_i)

    headers = []
    data = []
    for column in column_outputs:
        headers.append(column.name)
        data.append(column.col)

    df = pd.DataFrame(np.array(data).T, columns=headers)
    return df

# To make a new class ensure it has a unuique name, ensure it accepts the following arguments (name, n_records, args)
# and be sure it has .name and .col properties. .name is a string refering to the unique name as supplied to the class
# init, and .col shoul be an n_records long numpy array of the values to be in the column


class Number:
    """
    Produce a column of random floats in a range.
    """
    def __init__(self, name='Test Number', n_records=50, args=None):
        """
        :param name: String column root name
        :param n_records: Int number of rows per column
        :param args:
            - min_val: float, the minimum value to appear in the array
            - max_val: float, the maximum value to appear in the array
        """

        if not args:
            args = {}
        self.name = name
        self.n_records = n_records
        self.max_val = args.get('max_val', 100)
        self.min_val = args.get('min_val', 0)

        self.col = self.create_array()

    def create_array(self):
        """
        Standard class method to produce the list to be used as a column

        :return: List, the column
        """

        col = np.random.rand(self.n_records)
        col += self.min_val
        col *= (self.max_val - self.min_val)
        return col


class Binary:
    """
    Produce a column of binary 1,0 values at a given ratio.
    """
    def __init__(self, name='Test Binary', n_records=50, args=None):
        """
        :param name: String column root name
        :param n_records: Int number of rows per column
        :param args:
            - perc_ones: decimal, the percentage of ones to appear in the binary data
        """

        if not args:
            args = {}
        self.name = name
        self.n_records = n_records
        self.perc_ones = args.get('perc_ones', .05)

        self.col = self.create_array()

    def create_array(self):
        """
        Standard class method to produce the list to be used as a column

        :return: List, the column
        """

        col = np.random.rand(self.n_records)
        split = col < self.perc_ones
        col[split] = 1
        col[~split] = 0
        col = col.astype(int)

        return col


class TextRandom:
    """
    Produce a column of random sentences, 1 per row, generated by markov chains on a given corpus.
    """
    def __init__(self, name='Test Random Text', n_records=50, args=None):
        """
        :param name: String column root name
        :param n_records: Int number of rows per column
        :param args:
            - corpus: An uncleaned tokenized corpus to be used as a training set for the markov chains
            - remove_brackets_and_quotes: Bool, remove brackets and quotes that can otherwise appear irregular
        """

        self.name = name
        self.n_records = n_records
        self.corpus = args.get('corpus', brown.words()[:100000])
        self.remove_brackets_and_quotes = args.get('remove_brackets_and_quotes', True)

        self.cache = {}

        if self.remove_brackets_and_quotes:
            self.corpus = [w for w in self.corpus if w not in ['"', '`', '(', ')', '``', "'", "''"]]

        self.corpus_size = len(self.corpus)
        self.database()

        self.col = self.create_array()

    def triples(self):
        """
        Generates triples from the given data string.
        1st (word1, word2, word3)
        2nd (word2, word3, word4)
        etc
        """

        if len(self.corpus) < 3:
            return

        for i in range(len(self.corpus) - 2):
            yield (self.corpus[i], self.corpus[i + 1], self.corpus[i + 2])

    def database(self):
        for w1, w2, w3 in self.triples():
            key = (w1, w2)
            if key in self.cache:
                self.cache[key].append(w3)
            else:
                self.cache[key] = [w3]

    def generate_sentence(self,
                          non_forward_space_punctuation='.?,:;',
                          clean_punctuation=True):
        """
        Generate a sentence using markov chains

        :param non_forward_space_punctuation: String, collection of punctuation marks to remove white space before
        :param clean_punctuation: Bool, whether to remove the whitespaces before selected punctuation marks

        :return: String, the sentence generated
        """

        sentence_ending_keys = [key for key in self.cache.keys() if key[0] == '.']
        seed_key = random.choice(sentence_ending_keys)
        seed_word = seed_key[1]
        next_word = random.choice(self.cache[seed_key])

        w1, w2 = seed_word, next_word
        gen_words = []
        while w2 not in ['.', '?', '!']:
            gen_words.append(w1)
            w1, w2 = w2, random.choice(self.cache[(w1, w2)])

        gen_words.append(w2)

        text = ' '.join(gen_words)

        if clean_punctuation:
            for punc in non_forward_space_punctuation:
                text = text.replace(' ' + punc, punc)

        return text

    def create_array(self,
                     non_forward_space_punctuation='.?,:;',
                     clean_punctuation=True):
        """
        Standard class method to produce the list to be used as a column

        :param non_forward_space_punctuation: String, collection of punctuation marks to remove white space before
        :param clean_punctuation: Bool, whether to remove the whitespaces before selected punctuation marks

        :return: List, the column
        """

        col = []
        for n in range(self.n_records):
            col += [self.generate_sentence(non_forward_space_punctuation=non_forward_space_punctuation,
                                           clean_punctuation=clean_punctuation)]

        return col


class TextTopic(object):
    """
    Produce a column of random sentences containing a given key word, 1 per row, generated by markov chains on a
    given corpus.
    """
    def __init__(self, name='Test Text Topic', n_records=50, args=None):
        """
        :param name: String column root name
        :param n_records: Int number of rows per column
        :param args:
            - topic_word: String, word to generate sentences around
            - corpus: An uncleaned tokenized corpus to be used as a training set for the markov chains
            - remove_brackets_and_quotes: Bool, remove brackets and quotes that can otherwise appear irregular
        """

        self.name = name
        self.n_records = n_records
        self.topic_word = args.get('topic_word', 'city')
        self.corpus = args.get('corpus', brown.words()[:100000])
        self.remove_brackets_and_quotes = args.get('remove_brackets_and_quotes', True)

        self.cache_f = {}
        self.cache_b = {}

        if self.remove_brackets_and_quotes:
            self.corpus = [w for w in self.corpus if w not in ['"', '`', '(', ')', '``', "'", "''"]]
        else:
            self.corpus = self.corpus

        self.corpus_size = len(self.corpus)
        self.database()

        self.col = self.create_array()

    def triples(self):
        """
        Generates triples from the given data string.
        1st (word1, word2, word3)
        2nd (word2, word3, word4)
        etc
        """

        if len(self.corpus) < 3:
            return

        for i in range(len(self.corpus) - 2):
            yield (self.corpus[i], self.corpus[i + 1], self.corpus[i + 2])

    def database(self):

        # Forward dict
        for w1, w2, w3 in self.triples():
            key = (w1, w2)
            if key in self.cache_f:
                self.cache_f[key].append(w3)
            else:
                self.cache_f[key] = [w3]

        # Backward dict
        for w1, w2, w3 in self.triples():
            key = (w2, w3)
            if key in self.cache_b:
                self.cache_b[key].append(w1)
            else:
                self.cache_b[key] = [w1]

    def generate_topic_sentence(self,
                                non_forward_space_punctuation='.?,:;',
                                clean_punctuation=True):
        """
        Generate a sentence using markov chains, it will contain the topic word

        :param non_forward_space_punctuation: String, collection of punctuation marks to remove white space before
        :param clean_punctuation: Bool, whether to remove the whitespaces before selected punctuation marks

        :return: String, the sentence generated
        """

        # Forward
        topic_word_keys = [key for key in self.cache_f.keys() if self.topic_word == key[0]]
        seed_key = random.choice(topic_word_keys)
        seed_word, next_word = seed_key

        w1, w2 = seed_word, next_word
        forward_gen_words = []
        while w2 not in ['.', '?', '!']:
            forward_gen_words.append(w1)
            w1, w2 = w2, random.choice(self.cache_f[(w1, w2)])

        forward_gen_words.append(w2)

        # Backward
        topic_word_keys = [key for key in self.cache_b.keys() if self.topic_word == key[1]]
        seed_key = random.choice(topic_word_keys)
        previous_word, seed_word = seed_key

        w1, w2 = previous_word, seed_word
        backward_gen_words = []
        while w1 not in ['.', '?', '!']:
            backward_gen_words.append(w1)
            w1, w2 = random.choice(self.cache_b[(w1, w2)]), w1

        # Join
        backward_gen_words = list(reversed(backward_gen_words))
        text = ' '.join(backward_gen_words + forward_gen_words)

        if clean_punctuation:
            for punc in non_forward_space_punctuation:
                text = text.replace(' ' + punc, punc)

        return text

    def create_array(self,
                     non_forward_space_punctuation='.?,:;',
                     clean_punctuation=True):
        """
        Standard class method to produce the list to be used as a column

        :param non_forward_space_punctuation: String, collection of punctuation marks to remove white space before
        :param clean_punctuation: Bool, whether to remove the whitespaces before selected punctuation marks

        :return: List, the column
        """

        col = []
        for n in range(self.n_records):
            col += [self.generate_topic_sentence(non_forward_space_punctuation=non_forward_space_punctuation,
                                                 clean_punctuation=clean_punctuation)]

        return col
