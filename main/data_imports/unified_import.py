#!/usr/bin/env python

"""Common classes for holding social media mentions from different sources"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

import pandas as pd


def create_common_df(mention_list, user_list):
    """
    Creates a Pandas df of records from python lists of common user objects and common mention objects. A record is
    the combination of a user and a mention

    :param mention_list: List of common mention objects
    :param user_list: List of common user objects
    :return: records_df - A Pandas df where each row is a record, consisting of a mention and user complete
    with meta-variables
    """

    mention_list = mention_list
    user_list = user_list

    mentions_df = create_common_mention_df(mention_list)
    users_df = create_common_user_df(user_list)

    record_df = pd.merge(how='left', left=mentions_df, right=users_df, on=['Author ID', 'Source', 'Domain'])

    print('Total Records: ' + str(len(record_df)))

    return record_df


def create_common_user_df(user_list):
    """
    Creates a Pandas df of users from a list of common user objects

    :param user_list: List of common user objects
    :return: users_df - A Pandas df where each row is a user, with all user specific meta variables
    """

    user_list = user_list

    user_lists = []
    for user in user_list:
        user_lists.append(user.to_list())

    users_df = pd.DataFrame(user_lists, columns=['Author ID', 'Domain', 'Source', 'Full Name', 'Username', 'Bio',
                                                 'Profile Picture URL'])

    users_df = users_df.drop_duplicates(subset=['Author ID'])

    return users_df


def create_common_mention_df(mention_list):
    """
    Creates a Pandas df of users from a list of common mention objects

    :param mention_list: List of common mention objects
    :return: mentions_df - A Pandas df where each row is a mention, with all mention specific meta variables
    """

    mention_list = mention_list

    mention_lists = []
    for mention in mention_list:
        mention_lists.append(mention.to_list())

    mentions_df = pd.DataFrame(mention_lists, columns=['ID', 'Domain', 'Source', 'URL', 'Author ID', 'Date (GMT)',
                                                       'Date (Local)', 'Date (Local - Zone)', 'Snippet', 'Sentiment',
                                                       'Location', 'Long', 'Lat'])

    mentions_df = mentions_df.drop_duplicates(subset=['ID'])

    return mentions_df
