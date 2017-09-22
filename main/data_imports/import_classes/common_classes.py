#!/usr/bin/env python

"""Classes for Youtube objects"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


class TextMention:
    """
    Common text mention class
    """

    def __init__(self):

        self.doc_id = None
        self.domain = None
        self.source = None
        self.url = None
        self.author_id = None
        self.dategmt = None
        self.datelocal = None
        self.datelocalzone = None
        self.snippet = None
        self.sentiment = None
        self.location = None
        self.lat = None
        self.long = None

    def to_list(self):
        """
        Convert the object into a list

        :return: List of the objects attributes
        """

        list_form = [self.doc_id, self.domain, self.source, self.url, self.author_id, self.dategmt, self.datelocal,
                     self.datelocalzone, self.snippet, self.sentiment, self.location, self.long, self.lat]
        return list_form


class User:

    def __init__(self):

        self.author_id = None
        self.domain = None
        self.source = None
        self.author_fullname = None
        self.author_username = None
        self.bio = None
        self.profilepictureurl = None

    def to_list(self):
        """
        Convert the object into a list

        :return: List of the objects attributes
        """

        list_form = [self.author_id, self.domain, self.source, self.author_fullname, self.author_username,
                     self.bio, self.profilepictureurl]

        return list_form
