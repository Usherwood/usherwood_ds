#!/usr/bin/env python

"""Functions for cleaning generic text data, the master function 'clean_text' calls all sub functions if required."""

import string

from pos_ngrams.preprocessing.tokenizer import tokenizer_word, tokenizer_pos, de_tokenizer_pos

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def clean_text(text_string=None,
               tokens=None,
               pos_tuples=False,
               remove_punctuation=True,
               punctuation=string.punctuation,
               remove_additional_whitespaces=True,
               lower=True):
    """
    Function that cleans text using any combination of the below functions

    :param text_string: Python string object to be tokenized and cleaned
    :param tokens: Python list of strings already tokenized
    :param pos_tuples: Bool, if tokens are a list of pos_tuples set this to true
    :param remove_punctuation: Boolean - remove punctuation if True
    :param punctuation: A string of punctuation marks to be removed
    :param remove_additional_whitespaces: Removes additional whitespaces from text (leaves standard word spaces)
    :param lower: Boolean - lower text if True
    :return: String comprable to the input but with all words cleaned.
    """

    if text_string:
        text_string = str(text_string)
        tokens = tokenizer_word(text_string)

    if pos_tuples:
        tokens, tokens_tags = tokenizer_pos(tokens)
        tokens_original = tokens

    if tokens is None:
        text = ''
    else:
        if remove_punctuation:
            tokens = remove_punctuation_tokens(tokens,
                                               punctuation=punctuation)
        if remove_additional_whitespaces:
            tokens = remove_additional_whitespace(tokens)

        if lower:
            tokens = lower_tokens(tokens)


    if text_string:
        cleaned = " ".join(tokens)
    elif pos_tuples:
        cleaned = de_tokenizer_pos(tokens, tokens_tags, tokens_original)
    else:
        cleaned = tokens

    return cleaned


def remove_additional_whitespace(tokens):
    """
    Removes additional whitespaces

    :param tokens: A list of tokens
    :return: A comparable list of tokens to the input but with additional whitespaces removed
    """

    cleaned_tokens = []
    for token in tokens:
        token = token.replace(' ', '')
        cleaned_tokens.append(token)
    return cleaned_tokens


def remove_punctuation_tokens(tokens, punctuation=string.punctuation, replace_with=' '):
    """
    Removes punctuation from a list of tokens

    :param tokens: A list of tokens
    :param punctuation: A string of punctuation marks to be removed
    :return: A comparable list of tokens to the input but with punctuation removed
    """

    cleaned_tokens = []
    for token in tokens:
        token = ''.join(ch if ch not in punctuation else replace_with for ch in token)
        cleaned_tokens.append(token)
    return cleaned_tokens


def lower_tokens(tokens):
    """
    Lowers the type case of a list of tokens

    :param tokens: A list of tokens
    :return: A comparable list of tokens to the input but all lower case
    """

    cleaned_tokens = []
    for token in tokens:
        token = token.lower()
        cleaned_tokens.append(token)
    return cleaned_tokens
