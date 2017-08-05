#!/usr/bin/env python

"""Function for removing stop words from text using a combination of NLTK and custom lists.

Custom lists can be found in data>stopwords. language_basics are basic stopword lists in languages not
supplied by nltk, additional are for add on to the basic languages, for example explicit language removal."""

import os

from nltk.corpus import stopwords
from main.nlp.preprocessing.tokenizer import tokenizer_word

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def stopword_removal(text_string=None,
                     tokens=None,
                     pos_tuples=False,
                     language='english',
                     additional_language_list=[],
                     adhoc_list=[],
                     ignore_nltk=False):
    """
    Main function you should import for stopword removal

    :param text_string: String you wish to remove stopwords from, this should be pre cleaned to lower and remove
    punctuation first, please see cleaning.py
    :param tokens: Python list of strings already tokenized to have stopwords removed
    :param pos_tuples: Bool, if tokens are a list of pos_tuples set this to true
    :param language: String of the language name you wish to remove basic stop words for, by default
    the program will look in NLTK for the language list, and if it cannot find it, it will look in
    utils_data>stopwords>language_basics.
    :param additional_language_list: List of strings refering to additional stopword lists found in
    utils_data>stopwords>additional. These will be lists such as catagory specific removal terms, explicit language
    filters, etc.
    :param adhoc_list: List of strings of specific adhoc words you would like removed
    :param ignore_nltk: Boolean to ignor NLTK presets for basic language and look first in:
    utils_data>stopwords>language_basics, not recommended for common languages

    :return: Returns the string you entered minus the stopwords in the superset of the above lists
    """

    stopwords_set = create_stopwords_set(basic_language=language,
                                         additional_language_list=additional_language_list,
                                         adhoc_list=adhoc_list,
                                         ignore_nltk=ignore_nltk)

    if tokens is None:
        tokens = []
    if text_string:
        tokens = tokenizer_word(text_string)
        tokens = [token for token in tokens if token not in stopwords_set]
        stopped = " ".join(tokens)
    elif pos_tuples:
        stopped = [(token, tag) for token, tag in tokens if token not in stopwords_set]
    else:
        stopped = [token for token in tokens if token not in stopwords_set]

    return stopped


def create_stopwords_set(basic_language, additional_language_list=[], adhoc_list=[], ignore_nltk=False):
    """
    Function used to create a superset of stopwords from multiple lists

    :param basic_language: String of the language name you wish to remove basic stop words for, by default
    the program will look in NLTK for the language list, and if it cannot find it, it will look in
    utils_data>stopwords>language_basics.
    :param additional_language_list: List of strings refering to additional stopword lists found in
    utils_data>stopwords>additional. These will be lists such as catagory specific removal terms, explicit language
    filters, etc.
    :param adhoc_list: List of strings of specific adhoc words you would like removed
    :param ignore_nltk: Boolean to ignor NLTK presets for basic language and look first in:
    utils_data>stopwords>language_basics, not recommended for common languages
    :return: Set of stopwords
    """

    stopwords_set = set([])

    # Append basic language sets using NLTK and/or language_basic files
    try:
        if not ignore_nltk:
            stopwords_set = stopwords_set.union(stopwords.words(basic_language))
        else:
            raise OSError
    except OSError:
        print(basic_language + ' is not in NLTK, looking in utils_data...')
        try:
            with open(os.path.join(os.path.dirname(__file__),
                                   '../../data/stopwords/language_basics/'+basic_language+'.txt'), 'r') as file:
                stopwords_file = file.read().split(',')
                stopwords_file = set(stopwords_file)
                stopwords_set = stopwords_set.union(stopwords_file)
        except OSError:
            print(basic_language + ' is not currently available. Skipping')
    except Exception as e:
        print(e)

    # Append additional sets to set
    for additional_list in additional_language_list:
        try:
            with open(os.path.join(os.path.dirname(__file__),
                                   '../../data/stopwords/additional/' + additional_list + '.txt'), 'r') as file:
                stopwords_file = file.read().split(',')
                stopwords_file = set(stopwords_file)
                stopwords_set = stopwords_set.union(stopwords_file)
        except OSError:
            print(str(additional_list) + ' does not exist. Skipping')

    # Append adhoc words to set
    adhoc_set = set(adhoc_list)
    stopwords_set = stopwords_set.union(adhoc_set)

    return stopwords_set
