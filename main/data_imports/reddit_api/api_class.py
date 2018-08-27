#!/usr/bin/env python

"""Class for querying the Reddit API"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"

import praw
import os
import json
from datetime import datetime
import copy

from main.data_imports.import_classes.common_classes import TextMention, User


with open(os.path.join(os.path.dirname(__file__), "../api_credentials.json"), 'r') as openfile:
    api_credentials = json.load(openfile)



class RedditAPI:
    def __init__(self, api_credentials=api_credentials):

        self.consumer_key = api_credentials["Reddit"]["consumer_key"]
        self.consumer_secret = api_credentials["Reddit"]["consumer_secret"]
        self.user_agent = api_credentials["Reddit"]["user_agent"]
        self.api = None
        self.setup_api()

    def setup_api(self):
        """
        Setup the API, ran during the init
        """

        self.api = praw.Reddit(client_id=self.consumer_key,
                               client_secret=self.consumer_secret,
                               user_agent=self.user_agent)

        return True

    def get_subreddit_posts(self, subreddit, sort_type=None, max_posts=100, query=None,
                            date=None):
        """
        Get the posts from a subreddit sorted by the sort_by method, 100 per request

        :param subreddit: String subreddit name
        :param sort_type: String how to sort which posts to retrieve first, options are:
            controversial
            gilded
            hot
            new
            rising
            top
        :param max_posts: The maximum number of posts to return, 100 per request
        :param query: String search term, how it is searched depends on the sort_type
        :param date: Dict of the date you wish to search back to

        :return: submissions. A list of Praw submission objects
        """

        if date is None:
            date = {'day': 1, 'month': 1, 'year': 2017}

        subreddit = self.api.subreddit(subreddit)

        submissions = []
        date_m = datetime(date['year'], date['month'], date['day'])

        if not query:
            if not sort_type:
                sort_type = 'hot'
            fn = getattr(subreddit, sort_type, None)
            if callable(fn):
                for submission in fn(limit=max_posts):
                    if (datetime.fromtimestamp(int(submission.created)) - date_m).total_seconds() > 0:
                        submissions += [submission]
        else:
            if not sort_type:
                sort_type = 'relevant'
            for submission in subreddit.search(query=query, limit=max_posts, sort=sort_type):
                if (datetime.fromtimestamp(int(submission.created)) - date_m).total_seconds() > 0:
                    submissions += [submission]

        return submissions

    def get_submission_comments(self, submission=None, id=None, max_replace_limit=1000):
        """
        Get the comments (sorted by best) for a submission

        :param submission: Praw submission object
        :param id: The reddit post id
        :param max_replace_limit: The maximum number of load more comment tokens to replace per load more comment token

        :return: all_comments. a list of Praw comment objects
        """

        submission = copy.deepcopy(submission)
        id = id
        max_replace_limit = max_replace_limit

        if not submission:
            submission = self.api.submission(id=id)

        submission.comments.replace_more(limit=max_replace_limit)
        submission.comment_sort = 'new'

        all_comments = submission.comments.list()

        return all_comments

    @staticmethod
    def parse_comment_to_common_mention(comment):
        """
        Creates a common text mention from a comment from the Reddit API

        :param comment: the Praw comment object

        :return: TextMention, used by unified_import
        """

        comment = copy.deepcopy(comment)

        common_mention = TextMention()

        if isinstance(comment, MoreComments):
            pass
        else:
            common_mention.domain = 'reddit.com'
            common_mention.source = 'RedditAPI'
            common_mention.url = 'https://www.reddit.com/r/' + comment.subreddit.display_name + '/comments/' \
                                 + comment.submission.id + '/'
            common_mention.snippet = comment.body
            common_mention.doc_id = common_mention.snippet + common_mention.url
            if comment.author:
                common_mention.author_id = 'reddit.com' + comment.author.name
            common_mention.dategmt = datetime.fromtimestamp(int(comment.created))
            common_mention.datelocal = None #TODO add to class
            common_mention.datelocalzone = None  # TODO add to class
            common_mention.sentiment = 'Not Found because it does not exist'
            common_mention.location = 'Doesnt Exist'  # TODO add location
            common_mention.long = None
            common_mention.lat = None

        return common_mention

    @staticmethod
    def parse_comment_to_common_user(comment):
        """
        Creates a common user from a comment from the Reddit API

        :param comment: the Praw comment object

        :return: User, used by unified_import
        """

        comment = copy.deepcopy(comment)

        common_user = User()

        if isinstance(comment, MoreComments):
            pass
        else:
            common_user.domain = 'reddit.com'
            common_user.source = 'RedditAPI'
            if comment.author:
                common_user.author_id = 'reddit.com' + comment.author.name
                common_user.author_fullname = comment.author.name
                common_user.author_username = comment.author.name
            common_user.bio = 'Doesnt Exist'
            common_user.profilepictureurl = 'Doesnt Exist'

        return common_user
