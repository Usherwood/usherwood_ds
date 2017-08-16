#!/usr/bin/env python

"""Classes for Youtube objects (and Common objects)"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


class YoutubeTextComment:

    def __init__(self):
        self.youtube_comment_id = None
        self.domain = None
        self.source = None
        self.youtube_author_id = None
        self.author_id = None
        self.author_name = None
        self.date = None
        self.snippet = None
        self.youtube_video_id = None
        self.like_count = None
        self.reply_count = None
        self.profile_picture = None

    def to_list(self):
        """
        Convert the object into a list

        :return: List of the objects attributes
        """

        list_form = [self.youtube_comment_id, self.domain, self.source, self.youtube_author_id, self.author_id,
                     self.author_name, self.date, self.snippet, self.youtube_video_id, self.like_count,
                     self.reply_count, self.profile_picture]

        return list_form


class YoutubeVideo:

    def __init__(self):
        self.author_id = None
        self.youtube_author_id = None
        self.author_name = None
        self.youtube_video_id = None
        self.title = None
        self.description = None
        self.publish_date = None
        self.view_count = None
        self.like_count = None
        self.dislike_count = None
        self.comment_count = None

    def to_list(self):
        """
        Convert the object into a list

        :return: List of the objects attributes
        """

        list_form = [self.youtube_video_id, self.youtube_author_id, self.author_id, self.author_name, self.title,
                     self.description, self.publish_date, self.view_count, self.like_count, self.dislike_count,
                     self.comment_count]

        return list_form


class User:
    """
    Common user class
    """

    def __init__(self):

        self.author_id = None
        self.domain = None
        self.source = None
        self.author_fullname = None
        self.author_username = None
        self.bio = None

    def to_list(self):
        """
        Convert the object into a list

        :return: List of the objects attributes
        """

        list_form = [self.author_id, self.domain, self.source, self.author_fullname, self.author_username,
                     self.bio]

        return list_form
