#!/usr/bin/env python

""""Functions for stemming text"""

from nltk.stem import SnowballStemmer

from main.nlp.preprocessing.tokenizer import tokenizer_word, tokenizer_pos, de_tokenizer_pos

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def stem_text(text_string=None, tokens=None, pos_tuples=False, language='english'):
    """
    Function that stems a text string using the NLTK snowball stemmer

    :param text_string: Python string object to be tokenized and stemmed
    :param tokens: Python list of strings already tokenized
    :param pos_tuples: Bool, if tokens are a list of pos_tuples set this to true
    :parma language: String representing the language to be used

    :return: String comparable to the input but with all words stemmed.
    """

    try:
        stemmer = SnowballStemmer(language)
    except ValueError as e:
        print('Invalid language supplied to the stemmer, please choose from: ' + " ".join(SnowballStemmer.languages) +
              '\nOr add a new stemmer to the repository ;)')

    if text_string:
        tokens = tokenizer_word(text_string)
        tokens = [stemmer.stem(token) for token in tokens]
        stemmed = " ".join(tokens)
    elif pos_tuples:
        tokens, tokens_tags = tokenizer_pos(tokens)
        tokens_original = tokens
        tokens = [stemmer.stem(token) for token in tokens]
        stemmed = de_tokenizer_pos(tokens, tokens_tags, tokens_original)
    else:
        stemmed = [stemmer.stem(token) for token in tokens]

    return stemmed
