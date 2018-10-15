#!/usr/bin/env python

"""Functions to parse lists of Youtube objects to pandas dataframes"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

import pandas as pd
import numpy as np


def create_youtube_video_df(youtube_video_list):
    """
    Creates a Pandas df of users from a list of YoutubeVideo objects

    :param youtube_video_list: List of YoutubeVideo objects

    :return: youtube_video_df - A Pandas df where each row is a video, with all video specific meta variables
    """

    video_list = []
    for video in youtube_video_list:
        video_list.append(video.to_list())

    youtube_video_df = pd.DataFrame(video_list, columns=['Youtube Video ID', 'Youtube Author ID', 'Author ID',
                                                         'Author Name', 'Title', 'Description', 'Publish Date',
                                                         'View Count', 'Like Count', 'Dislike Count', 'Comment Count'])

    youtube_video_df = youtube_video_df.drop_duplicates(subset=['Youtube Video ID'])

    return youtube_video_df


def create_youtube_comment_df(youtube_comment_list):
    """
    Creates a Pandas df of mentions from a list of YoutubeTextComment objects

    :param youtube_comment_list: List of YoutubeTextComment objects

    :return: youtube_comment_df - A Pandas df where each row is a comment, with all comment and user
    specific meta variables
    """

    comment_list = []
    for comment in youtube_comment_list:
        comment_list.append(comment.to_list())

    youtube_comment_df = pd.DataFrame(comment_list, columns=['Youtube Comment ID', 'Domain', 'Source',
                                                             'Youtube Author ID', 'Author ID','Author Name',
                                                             'Publish Date', 'Snippet', 'Youtube Video ID',
                                                             'Like Count', 'Reply Count', 'Profile Picture URL'])

    youtube_comment_df = youtube_comment_df.drop_duplicates(subset=['Youtube Comment ID'])

    return youtube_comment_df


def create_youtube_user_df(youtube_user_list):
    """
    Creates a Pandas df of users from a list of YoutubeUser objects

    :param youtube_user_list: List of YoutubeUser objects

    :return: youtube_user_df - A Pandas df where each row is a user/channel, with all user
    specific meta variables
    """

    user_list = []
    for user in youtube_user_list:
        user_list.append(user.to_list())

    youtube_user_df = pd.DataFrame(user_list, columns=['Youtube Author ID', 'Domain', 'Source', 'Author Full Name',
                                                       'Author Username', 'Bio', 'Profile Picture URL', 'View Count',
                                                       'Comment Count', 'Subscriber Count', 'Hidden Sub Count',
                                                       'Video Count', 'Author ID'])

    youtube_user_df['View Count'] = youtube_user_df['View Count'].astype(np.int64)
    youtube_user_df['Comment Count'] = youtube_user_df['Comment Count'].astype(np.int64)
    youtube_user_df['Subscriber Count'] = youtube_user_df['Subscriber Count'].astype(np.int64)
    youtube_user_df['Video Count'] = youtube_user_df['Video Count'].astype(np.int64)

    youtube_user_df = youtube_user_df.drop_duplicates(subset=['Author ID'])

    return youtube_user_df
