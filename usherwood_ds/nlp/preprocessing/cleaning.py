#!/usr/bin/env python

"""Functions for cleaning generic text data, the master function 'clean_text' calls all sub functions if required."""

import string
import re

from usherwood_ds.nlp.preprocessing.tokenizer import tokenizer_word, tokenizer_pos, de_tokenizer_pos

__author__ = "Peter J Usherwood"
__python_version__ = '3.5'


def clean_text(text_string=None,
               tokens=None,
               pos_tuples=False,
               remove_punctuation=True,
               punctuation=string.punctuation,
               remove_additional_whitespaces=True,
               lower=True,
               tokens_to_ignore=["[USER]", "[HASHTAG]", "[URL]"]):
    """
    Function that cleans text using any combination of the below functions

    :param text_string: Python string object to be tokenized and cleaned
    :param tokens: Python list of strings already tokenized
    :param pos_tuples: Bool, if tokens are a list of pos_tuples set this to true
    :param remove_punctuation: Boolean - remove punctuation if True
    :param punctuation: A string of punctuation marks to be removed
    :param remove_additional_whitespaces: Removes additional whitespaces from text (leaves standard word spaces)
    :param lower: Boolean - lower text if True
    :param tokens_to_ignore: List of Str, tokens to avoid cleaning

    :return: String comprable to the input but with all words cleaned.
    """

    if not pos_tuples:
        if tokens is None:
            tokens = []

        if text_string:
            text_string = str(text_string)
            tokens = tokenizer_word(text_string)

        if remove_punctuation:
            tokens = remove_punctuation_tokens(tokens,
                                               punctuation=punctuation,
                                               tokens_to_ignore=tokens_to_ignore)
        if remove_additional_whitespaces:
            tokens = remove_additional_whitespace(tokens)

        if lower:
            tokens = lower_tokens(tokens,
                                  tokens_to_ignore=tokens_to_ignore)

        if text_string is not None:
            cleaned = " ".join(tokens)
        else:
            cleaned = tokens

    if pos_tuples:

        tokens, tokens_tags = tokenizer_pos(tokens)

        if remove_punctuation:
            tokens = remove_punctuation_tokens(tokens,
                                               punctuation=punctuation)
        if remove_additional_whitespaces:
            tokens = remove_additional_whitespace(tokens)

        if lower:
            tokens = lower_tokens(tokens)

        cleaned = de_tokenizer_pos(tokens, tokens_tags)

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


def remove_punctuation_tokens(tokens,
                              tokens_to_ignore,
                              punctuation=string.punctuation,
                              replace_with=' '):
    """
    Removes punctuation from a list of tokens

    :param tokens: A list of tokens
    :param punctuation: A string of punctuation marks to be removed (defaults to none, used to default to =string.punctuation but not anymore)
    :param regex_replacement: use regex to define punctuation to be replaced (this is default, if punctuation is None)
    :param replace_with: the string to replace the punctuation with
    :param tokens_to_ignore: List of Str, tokens to avoid cleaning

    :return: A comparable list of tokens to the input but with punctuation removed
    """

    # Done: add more comprehensive punctuation removal: s = re.sub(r'[^\w\s]','',s)

    cleaned_tokens = []
    for token in tokens:
        if token not in tokens_to_ignore:
            token = ''.join(ch if ch not in punctuation else replace_with for ch in token)
        cleaned_tokens.append(token)
    return cleaned_tokens


def lower_tokens(tokens,
                 tokens_to_ignore):
    """
    Lowers the type case of a list of tokens

    :param tokens: A list of tokens
    :param tokens_to_ignore: List of Str, tokens to avoid cleaning

    :return: A comparable list of tokens to the input but all lower case
    """

    cleaned_tokens = []
    for token in tokens:
        if token not in tokens_to_ignore:
            token = token.lower()
        cleaned_tokens.append(token)
    return cleaned_tokens
