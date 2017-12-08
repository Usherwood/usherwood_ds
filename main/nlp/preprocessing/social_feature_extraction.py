#!/usr/bin/env python

""""Functions for extracting usful features from social text data."""

__author__ = 'Peter J Usherwood'
__python_version__ = '3.5'


def extract_hashtags(text_string, remove_hashtags=False):
    """
    Extracts hashtags from a text_string

    :param text_string: String of text you wish to extract hashtags from
    :param remove_hashtags: Boolean, if True it will remove the hashtags from the text_string

    :return: text_sting: Sting as input but with hashtags removed if specified
    :return: hashtags: List of unique hashtags in the text_string
    """

    hashtags = set(part[1:] for part in text_string.split() if part.startswith('#'))
    hashtags = list(hashtags)

    if remove_hashtags:
        text_string = " ".join([part for part in text_string.split() if not part.startswith('#')])

    return text_string, hashtags


def extract_mentioned_users(text_string, remove_users=True):
    """
    Extracts mentioned_users from a text_string

    :param text_string: String of text you wish to extract mentioned_users from
    :param remove_users: Boolean, if True it will remove the mentioned_users from the text_string

    :return: text_sting: Sting as input but with mentioned_users removed if specified
    :return: mentioned_users: List of unique mentioned_users in the text_string
    """

    mentioned_users = set(part[1:] for part in text_string.split() if part.startswith('@'))
    mentioned_users = list(mentioned_users)

    if remove_users:
        text_string = " ".join([part for part in text_string.split() if not part.startswith('@')])

    return text_string, mentioned_users


def extract_urls(text_string, remove_urls=True):
    print(text_string)
    print(remove_urls)
    return False
    # TODO please build
