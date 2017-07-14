#!/usr/bin/env python

"""Functions for Part Of Speech (POS) tagging"""

import nltk
import os
import numpy as np
from itertools import compress
from nltk.corpus import brown
import string
import pickle
import re

from utils.linguistics.preprocessing.tokenizer import tokenizer_sentence

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def parse_browns_corpus_to_simplified(browns_tagged_sents):
    """
    Parse the tagged Browns corpus (in an array of sentences) into simplified tags

    :param browns_tagged_sents: Array of tagged Browns sentences

    :return: Array of sentences with simplified tags
    """

    sents_simplified = []
    for sent in browns_tagged_sents:
        sents_simplified.append([(tuples[0], simplify_brown_tags(tuples[1])) for tuples in sent])

    return sents_simplified


def train_pos_tagger_simplified(name='simplified_en',
                                corpus=brown.tagged_sents(),
                                simplified=True,
                                train_test_split=.8
                                ):
    """
    Train the simplified tag pos tagger and persist to disk

    :param name: The name of the file to persist to
    :param corpus: The tagged corpus to train and test on, it should be a list of sentences, each sentence should
    be a list of tuples with the word first and the pos tag second.
    :param simplified: Bool, True to parse the tags to a simplified subset
    :param train_test_split: Decimal between 0 and 1, the ration of the train to test split
    """

    if not corpus:
        print('Error no corpus supplied')
        return False

    if simplified:
        corpus = parse_browns_corpus_to_simplified(corpus)

    msk = np.random.rand(len(corpus)) < train_test_split
    train = list(compress(corpus, msk))
    test = list(compress(corpus, [not i for i in msk]))

    t0 = nltk.DefaultTagger('NN')
    t1 = nltk.UnigramTagger(train, backoff=t0)
    t2 = nltk.BigramTagger(train, backoff=t1)

    print('Accuracy ',str(t2.evaluate(test)))
    print('Saving to utils_data/models/pos_taggers/' + name + '.pkl')

    file = os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../../utils_data/models/pos_taggers/'
                        + name + '.pkl')
    save = open(file, 'wb')
    pickle.dump(t2, save, -1)
    save.close()

    return True


def tag_snippet(snippet, tagger_name):
    """
    Tag Snippets using a pos tagger

    :param snippet: Text snippet
    :param tagger_name: Name of pos tagger as it appears in utils_data/models/pos_taggers/

    :return: List of tuples for the tagged snippet
    """

    file = os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../../utils_data/models/pos_taggers/' +
                        tagger_name + '.pkl')

    input = open(file, 'rb')
    tagger = pickle.load(input)
    input.close()

    sent_tagged = []
    for sent in tokenizer_sentence(snippet):
        tokens = re.findall(r"[\w']+|[.,!?;]", sent)
        sent_tagged += tagger.tag(tokens)
    return sent_tagged


def simplify_brown_tags(tag):
    """
    Created simplified tags from the Browns corpus

    :param tag: Str, the current tag to be transformed

    :return: transformed tag
    """

    NP = ['NP']  # proper noun
    NN = ['NR', 'NN']  # noun
    VB = ['VB', 'BE', 'DO', 'EX', 'HV']  # verb
    NU = ['CD', 'OD']  # numbers
    AD = ['JJ']  # adjective
    QL = ['QL']  # qualifier
    AV = ['RB', 'RN', 'RP']  # adverb
    NG = ['*:']  # negator

    tag = tag[:2]

    if tag in NP:
        tag = 'NP'
    elif tag in list(string.punctuation):
        tag = tag
    elif tag in NN:
        tag = 'NN'
    elif tag in VB:
        tag = 'VB'
    elif tag in NU:
        tag = 'NU'
    elif tag in AD:
        tag = 'AD'
    elif tag in QL:
        tag = 'QL'
    elif tag in AV:
        tag = 'AV'
    elif tag in NG:
        tag = '*:'
    else:
        tag = 'OT'

    return tag


def simplify_parole_tags(tag):
    """
    Created simplified tag from a parole tagged corpus

    :param tag: Str, the current tag to be transformed

    :return: transformed tag
    """

    NP = ['NP']  # proper noun
    NN = ['NC']  # noun
    VB = ['VS', 'VM', 'VA']  # verb
    NU = ['Z', 'Zm', 'Zp']  # numbers
    AD = ['AO', 'AQ']  # adjective
    QL = []  # qualifier
    AV = ['RG', 'RN']  # adverb
    NG = []  # negator

    tag = tag[:2]

    if tag in NP:
        tag = 'NP'
    elif tag in list(string.punctuation):
        tag = tag
    elif tag in NN:
        tag = 'NN'
    elif tag in VB:
        tag = 'VB'
    elif tag in NU:
        tag = 'NU'
    elif tag in AD:
        tag = 'AD'
    elif tag in QL:
        tag = 'QL'
    elif tag in AV:
        tag = 'AV'
    elif tag in NG:
        tag = '*:'
    else:
        tag = 'OT'

    return tag