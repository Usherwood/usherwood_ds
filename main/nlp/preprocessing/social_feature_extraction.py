#!/usr/bin/env python

""""Functions for extracting usful features from social text data."""

__author__ = 'Peter J Usherwood'
__python_version__ = '3.5'


import re


def extract_hashtags(text_string,
                     remove_hashtags=False,
                     replace_with_token=False,
                     token_to_replace='[HASHTAG]'):
    """
    Extracts hashtags from a text_string

    :param text_string: String of text you wish to extract hashtags from
    :param remove_hashtags: Boolean, if True it will remove the hashtags from the text_string
    :param replace_with_token: Boolean, replace the hashtags in the original string with a marker token
    :param token_to_replace: Str, the token to replace the hashtag

    :return: text_sting: Sting as input but with hashtags removed if specified
    :return: hashtags: List of unique hashtags in the text_string
    """

    hashtags = list(set(re.findall(r"#\w+", text_string)))

    if replace_with_token:
        text_string = re.sub(r"#\w+",
                             token_to_replace,
                             text_string)

    if remove_hashtags and not replace_with_token:
        text_string = re.sub(r"#\w+",
                             '',
                             text_string)

    return text_string, hashtags


def extract_mentioned_users(text_string,
                            remove_users=False,
                            replace_with_token=True,
                            token_to_replace='[USER]'):
    """
    Extracts mentioned_users from a text_string

    :param text_string: String of text you wish to extract mentioned_users from
    :param remove_users: Boolean, if True it will remove the mentioned_users from the text_string
    :param replace_with_token: Boolean, replace the users in the original string with a marker token
    :param token_to_replace: Str, the token to replace the user

    :return: text_sting: Sting as input but with mentioned_users removed if specified
    :return: mentioned_users: List of unique mentioned_users in the text_string
    """

    mentioned_users = list(set(re.findall(r"@\w+", text_string)))

    if replace_with_token:
        text_string = re.sub(r"@\w+",
                             token_to_replace,
                             text_string)

    if remove_users and not replace_with_token:
        text_string = re.sub(r"@\w+",
                             '',
                             text_string)

    return text_string, mentioned_users


def extract_urls(text_string,
                 remove_urls=False,
                 replace_with_token=True,
                 token_to_replace='[URL]'):
    """
    Extracts url from a text_string

    :param text_string: String of text you wish to extract url from
    :param remove_urls: Boolean, if True it will remove the url from the text_string
    :param replace_with_token: Boolean, replace the urls in the original string with a marker token
    :param token_to_replace: Str, the token to replace the url

    :return: text_sting: Sting as input but with urls removed if specified
    :return: urls: List of unique urls in the text_string
    """

    urls = list(set(re.findall(r"(?:http|ftp|https)://[\w_-]+(?:\.[\w_-]+)+(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",
                               text_string)))

    if replace_with_token:
        text_string = re.sub(r"(?:http|ftp|https)://[\w_-]+(?:\.[\w_-]+)"
                             r"+(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",
                             token_to_replace,
                             text_string)

    if remove_urls and not replace_with_token:
        text_string = re.sub(r"(?:http|ftp|https)://[\w_-]+(?:\.[\w_-]+)"
                             r"+(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",
                             '',
                             text_string)

    return text_string, urls
