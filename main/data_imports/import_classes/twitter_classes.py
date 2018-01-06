#!/usr/bin/env python

"""Classes for Youtube objects"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

from main.data_imports.import_classes.common_classes import User, TextMention


class TwitterUser(User):

    def __init__(self):

        self.twitter_author_id = None
        self.followers_count = None
        self.verified = None
        self.number_of_statuses = None
        self.created_at = None

    def to_list(self):
        """
        Convert the object into a list

        :return: List of the objects attributes
        """

        list_form = [self.twitter_author_id, self.domain, self.source, self.author_fullname, self.author_username,
                     self.bio, self.profilepictureurl, self.followers_count, self.verified,
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

    def to_list(self):
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
