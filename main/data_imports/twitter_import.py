#!/usr/bin/env python

"""Tools for mass downloading Twitter data into Twitter objects (extensions on the unified objects)"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

from main.data_imports.unified_import import TextMention, User
import pandas as pd


def create_twitter_df(mention_list, user_list):
    """
    Creates a Pandas df of records from python lists of Twitter user objects and Twitter mention objects. A record is
    the combination of a user and a mention

    :param mention_list: List of Twitter mention objects
    :param user_list: List of Twitter user objects
    :return: records_df - A Pandas df where each row is a record, consisting of a mention and user complete
    with meta-variables
    """

    mention_list = mention_list
    user_list = user_list

    mentions_df = create_twitter_mention_df(mention_list)
    users_df = create_twitter_user_df(user_list)

    record_df = pd.merge(how='left', left=mentions_df, right=users_df, on=['Author ID', 'Source', 'Domain'])

    print('Total Records: ' + str(len(record_df)))

    return record_df


def create_twitter_user_df(twitter_user_list):
    """
    Creates a Pandas df of users from a list of TwitterUser objects

    :param twitter_user_list: List of TwitterUser objects

    :return: twitter_users_df - A Pandas df where each row is a user, with all user specific meta variables
    """

    twitter_user_list = twitter_user_list

    user_lists = []
    for user in twitter_user_list:
        user_lists.append(user.to_list())

    twitter_users_df = pd.DataFrame(user_lists, columns=['Twitter Author ID', 'Domain', 'Source', 'Full Name',
                                                         'Username', 'Bio', 'Profile Picture URL', 'Follower Count',
                                                         'Profile Picture', 'Verified', 'Number of Statuses',
                                                         'Date Created', 'Author ID'])

    twitter_users_df = twitter_users_df.drop_duplicates(subset=['Twitter Author ID'])

    return twitter_users_df


def create_twitter_mention_df(twitter_mention_list):
    """
    Creates a Pandas df of users from a list of TwitterTextMention objects

    :param twitter_mention_list: List of TwitterTextMention objects

    :return: twitter_mentions_df - A Pandas df where each row is a tweet, with all tweet specific meta variables
    """

    twitter_mention_list = twitter_mention_list

    mention_lists = []
    for mention in twitter_mention_list:
        mention_lists.append(mention.to_list())

    twitter_mentions_df = pd.DataFrame(mention_lists, columns=['Tweet ID', 'Domain', 'Source', 'Url', 'Author ID',
                                                               'Date (GMT)', 'Date (Local)', 'Date (Local - Zone)',
                                                               'Snippet', 'Sentiment', 'Location', 'Long', 'Lat',
                                                               'Retweet Count', 'Favorite Count', 'Device', 'ID',
                                                               'ImageURL', 'is Retweet','ID of Reweet',
                                                               'ID of Original Tweet Author',
                                                               'Screen Name of Original Tweet Author',
                                                               'is Response','ID of Antecedent Tweet',
                                                               'ID of Antecedent Author',
                                                               'Screen Name of Antecedent Author',
                                                               'is Quoting','ID of Quoted Tweet',
                                                               'ID of Quoted Author',
                                                               'Screen Name of Quoted Author'])

    twitter_mentions_df.drop_duplicates(subset=['Tweet ID'], inplace=True)

    return twitter_mentions_df


class InvalidCredentials(Exception):
    pass


class TwitterUser(User):

    def __init__(self):

        self.twitter_author_id = None
        self.followers_count = None
        self.profile_image_full = None
        self.verified = None
        self.number_of_statuses = None
        self.created_at = None

    def to_list(self):
        """
        Convert the object into a list

        :return: List of the objects attributes
        """

        list_form = [self.twitter_author_id, self.domain, self.source, self.author_fullname, self.author_username,
                     self.bio, self.profilepictureurl, self.followers_count, self.profile_image_full, self.verified,
                     self.number_of_statuses, self.created_at, self.author_id]

        return list_form


class TwitterTextMention(TextMention):

    def __init__(self):

        self.tweet_id = None
        self.retweet_count = None
        self.favorite_count = None
        self.device = None
        self.imageURL = None
        self.is_retweet = None
        self.id_of_reweet = None
        self.id_of_original_tweet_author = None
        self.screen_name_of_original_tweet_author = None
        self.is_response = None
        self.id_of_antecedent_tweet = None
        self.id_of_antecedent_author = None
        self.screen_name_of_antecedent_author = None
        self.is_quoting = None
        self.id_of_quoted_tweet = None
        self.id_of_quoted_author = None
        self.screen_name_of_quoted_author = None

    def to_list(static):
        """
        Convert the object into a list

        :return: List of the objects attributes
        """

        list_form = [self.tweet_id, self.domain, self.source, self.url, self.author_id, self.dategmt, self.datelocal,
                     self.datelocalzone, self.snippet, self.sentiment, self.location, self.long, self.lat,
                     self.retweet_count, self.favorite_count, self.device, self.doc_id, self.imageURL,
                     self.is_retweet ,self.id_of_reweet, self.id_of_original_tweet_author,
                     self.screen_name_of_original_tweet_author, self.is_response, self.id_of_antecedent_tweet,
                     self.id_of_antecedent_author, self.screen_name_of_antecedent_author, self.is_quoting,
                     self.id_of_quoted_tweet, self.id_of_quoted_author, self.screen_name_of_quoted_author]

        return list_form
