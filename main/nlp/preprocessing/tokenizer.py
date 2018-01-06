#!/usr/bin/env python

"""Functions for tokenizing data, the below can be updated to account for new lines without spaces, or contiguous
non-English languages"""

import shlex
from nltk.tokenize import sent_tokenize

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def tokenizer_word(text_string, keep_phrases=False):
    """
    Tokenizer that tokenizes a string of text on spaces and new lines (regardless of however many of each.)

    :param text_string: Python string object to be tokenized.
    :param keep_phrases: Booalean will not split "quoted" text
    :return: Array of strings, each is a word
    """

    text_string = str(text_string)

    if keep_phrases:
        tokens = shlex.split(text_string.replace('\n', ' ').replace('/', ' '))
    else:
        tokens = text_string.replace('\n', ' ').replace('/', ' ').split()

    return tokens


def tokenizer_sentence(text_string):
    """
    Tokenizer that tokenizes a string of text into sentences

    :param text_string: Python string object to be tokenized.
    :return: Array of strings, each is a sentence
    """

    sent_tokenize_list = sent_tokenize(text_string)

    return sent_tokenize_list


def tokenizer_pos(pos_tuplets):
    """
    Tokenizer that tokenizes a list of part of speech tuplets into array of tokens for each word, and an array for each
    tag

    :param pos_tuplets: List of pos tuplets

    :return: tokens, list of word tokens; tokens_tags, list of pos tags
    """

    if type(pos_tuplets) != type(['list']):
        raise TypeError('Input should be a list of POS tuples')
    if set([type(b) for b in pos_tuplets]) != set([type(('Tuple', 'E'))]):
        raise TypeError('Input should be a list of POS tuples')

    tokens = []
    tokens_tags = []
    for tup in pos_tuplets:
        tokens.append(tup[0])
        tokens_tags.append(tup[1])

    return tokens, tokens_tags


def de_tokenizer_pos(tokens, tokens_tags):
    """
    Rezips the 2 tokenized lists of the tokenizer_pos into a list of pos tuples

    :param tokens: List of str, word tokens
    :param tokens_tags: List of str, pos tags

    :return: pos_tuplets, List of pos tuplets
    """

    if type(tokens) != type(['list']):
        raise TypeError('tokens should be a list')
    if set([type(b) for b in tokens]) != set([type('String')]):
        raise TypeError('tokens should be a list of strings')
    if type(tokens_tags) != type(['list']):
        raise TypeError('tokens_tags should be a list')
    if set([type(b) for b in tokens_tags]) != set([type('String')]):
        raise TypeError('tokens_tags should be a list of strings')

    pos_tuplets = [(x, y) for x, y in zip(tokens, tokens_tags) if x is not None]

    return pos_tuplets
