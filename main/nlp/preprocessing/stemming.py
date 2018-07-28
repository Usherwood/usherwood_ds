#!/usr/bin/env python

""""Functions for stemming text, this is by no means perfect, if you find a great stemmer please add it
- Peter 26/10/16"""

import re
import warnings

from nltk.stem import SnowballStemmer

from main.nlp.preprocessing.tokenizer import tokenizer_word, tokenizer_pos, de_tokenizer_pos

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


class Stemmer():

    def __init__(self, language='english'):
        """
        :param language: String representing the language to be used
        """

        self.stemmer = None

        try:
            self.stemmer = SnowballStemmer(language)
        except ValueError as e:
            print(
                'Invalid language supplied to the stemmer, please choose from: ' + " ".join(SnowballStemmer.languages) +
                '\nOr add a new stemmer to the repository ;)')

    def stem_text(self, text_string=None, tokens=None, pos_tuples=False, check_trailing=True):
        """
        Function that stems a text string using the NLTK snowball stemmer

        :param text_string: Python string object to be tokenized and stemmed
        :param tokens: Python list of strings already tokenized
        :param pos_tuples: Bool, if tokens are a list of pos_tuples set this to true

        :return: String comparable to the input but with all words stemmed.
        """


        if tokens is None:
            tokens = []
        if text_string is not None:
            tokens = tokenizer_word(text_string)
            if check_trailing:
                [check_trailing_characters(token) for token in tokens]
            tokens = [self.stemmer.stem(token) for token in tokens]
            stemmed = " ".join(tokens)
        elif pos_tuples:
            tokens, tokens_tags = tokenizer_pos(tokens)
            if check_trailing:
                [check_trailing_characters(token) for token in tokens]
            tokens = [self.stemmer.stem(token) for token in tokens]
            stemmed = de_tokenizer_pos(tokens, tokens_tags)
        else:
            if check_trailing:
                [check_trailing_characters(token) for token in tokens]
            stemmed = [self.stemmer.stem(token) for token in tokens]

        return stemmed


def check_trailing_characters(token):
    """
    Raise warnings if tokens arn't properly cleaned for stemming. We do not force cleaning as that is the job of the
    cleaning script and precprocessing will force this before stemming. However if somebody wished to use the stemmer
    alone they have the choice how and what to clean.

    :param token: token to be checked before being stemmed
    """

    if token is '':
        pass
    else:
        if re.findall(r'[^\w\s]| ', token[-1]) is not []:
            warnings.warn('token ends with punctuation and/or white spaces and as such will not be properly stemmed')

    return True
