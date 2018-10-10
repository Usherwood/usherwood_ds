#!/usr/bin/env python

"""Class for querying the Youtube API and parsing to Youtube objects"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

import json
import os
import time
from datetime import datetime

from apiclient.discovery import build
from main.data_imports.import_classes.youtube_classes import YoutubeTextComment, YoutubeVideo, YoutubeUser
from main.data_imports.import_classes.common_classes import User, TextMention


with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../api_credentials.json"), 'r') as openfile:
    api_credentials = json.load(openfile)


class YoutubeAPI:

    def __init__(self, api_credentials=api_credentials):

        self.developer_key = api_credentials["Youtube"]["developer_key"]
        self.api = build("youtube", "v3", developerKey=self.developer_key)
        self.wait_time = 0

    def fortify_channel(self, channel_id=None, channel_name=None, fortify_with='snippet,statistics'):
        """
        Fortify a channel with the full json response

        :param channel_id: Str, optional, youtube channel id
        :param channel_name: Str, optional, youtube channel name
        :param fortify_with: Str, the parts of the json to return

        :return: Youtube channel json response
        """

        try:
            response = self.api.channels().list(part=fortify_with, id=channel_id, forUsername=channel_name).execute()

            video = response['items'][0]

            return video

        except Exception as e:
            print('All parts not found for video, skipping')
            return {'channel_id': channel_id, 'channel_name': channel_name, 'found':False}

    def fortify_video(self, video_id, fortify_with='snippet,contentDetails,statistics'):
        """
        Fortify a youtube video id with the full json response

        :param video_id: Str, Youtube video if
        :param fortify_with: Str, the parts of the json to return

        :return: Youtube video json response
        """

        try:
            response = self.api.videos().list(part=fortify_with,
                                              id=video_id).execute()

            video = response['items'][0]

            return video

        except Exception as e:
            print('All parts not found for video, skipping')
            return {'id':video_id}

    def get_videos_by_search_term(self,
                                  query,
                                  max_videos=50,
                                  location=None):
        """
        Find a number of Youtube videos given a search term

        :param query: Str, the term to search for
        :param max_videos: Int, the maximum number of videos to return
        :param location: List, [lat, long, radius (km)]

        :return: List of youtube video json responses
        """

        time.sleep(self.wait_time)

        videos = []
        n_requests = 0

        next_page_token = ""

        if not location:
            geocode = {'location': None, 'location_radius': None}
        else:
            geocode = {'location': str(location[0]) + ',' + str(location[1]), 'location_radius': location[2]}

        while (next_page_token is not None) and (len(videos) < max_videos):
            response = self.api.search().list(q=query,
                                              type="video",
                                              location=geocode['location'],
                                              locationRadius=geocode['location_radius'],
                                              part="id",
                                              maxResults=50,
                                              pageToken=next_page_token
                                              ).execute()

            n_requests += 1
            next_page_token = response.get('nextPageToken')

            for item in response['items']:
                video_id = item['id']['videoId']
                videos.append(self.fortify_video(video_id))

        print(str(n_requests * 50), 'videos searched')

        return videos

    def get_video_comments(self, video_id, num_comments=100, pt=''):
        """
        Get the comments from a Youtube video

        :param video_id: Str, The Youtube video id
        :param num_comments: Int, the ideal maximum number of comments, -1 for all
        :param pt: Str, Starting page token, '' for begining

        :return comments: List of json Youtube comments
        """

        comments = []

        while True:
            response = self.api.commentThreads().list(
                videoId=video_id,
                part='snippet',
                pageToken=pt,
                maxResults=50).execute()

            for item in response['items']:
                comments.append(item)

            pt = response.get('nextPageToken')

            if (len(comments) >= num_comments) & (num_comments != -1):
                print('User defined max comments found:', str(len(comments)))

                return comments

            elif pt is None:
                print('All comments found:', str(len(comments)))

                return comments

    def get_user_subscriptions(self, youtube_author_id, num_subscriptions=20, pt=''):
        """
        Return a list of jsons, where each json is a user json of a user that the youtube_author_id subscribes to

        :param youtube_author_id: Str, Youtube author ID
        :param num_subscriptions: Int, Maximum number of subscriptions to return
        :param pt: Str, page token

        :return: List of jsons, where each json is a user json
        """

        subscriptions = []

        try:
            while True:
                response = self.api.subscriptions().list(
                    part='snippet,contentDetails',
                    channelId=youtube_author_id,
                    pageToken=pt
                ).execute()

                for item in response['items']:
                    subscriptions.append(item)
                pt = response.get('nextPageToken')

                if (len(subscriptions) >= num_subscriptions) & (num_subscriptions != -1):
                    print('User defined max subscriptions found:', str(len(subscriptions)))

                    return subscriptions

                elif pt is None:
                    print('All subscriptions found:', str(len(subscriptions)))

                    return subscriptions

        except Exception as e:

            print(e)
            return subscriptions

    def get_playlist_video_ids(self, youtube_playlist_id, pt=''):
        """
        Return a list of video ids given a playlist ID

        :param youtube_playlist_id: Str, Youtube playlist ID
        :param pt: Str, page token

        :return: List of strings, list of video ids
        """

        video_ids = []

        try:
            while True:
                response = self.api.playlistItems().list(
                    part='contentDetails',
                    playlistId=youtube_playlist_id,
                    maxResults=25,
                    pageToken=pt).execute()

                for item in response['items']:
                    video_ids.append(item['contentDetails']['videoId'])
                pt = response.get('nextPageToken')

                if pt == None:
                    print('All videos found:', str(len(video_ids)))
                    return video_ids

        except Exception as e:
            print(e)
            return video_ids

    def get_user_playlists(self, youtube_author_id, pt=''):
        """
        Return a list of all playlist ids for a particular user/channel. A first step to returning all video ids for
        a user

        :param youtube_author_id: Str, Youtube author id
        :param pt: Str, page token

        :return: List of strings, list of all playlist ids
        """

        playlists = []

        try:
            while True:
                response = self.api.playlists().list(
                    part='snippet,contentDetails',
                    channelId=youtube_author_id,
                    maxResults=1,
                    pageToken=pt).execute()

                for item in response['items']:
                    playlists.append(item)
                pt = response.get('nextPageToken')

                if pt is None:
                    print('All playlists found:', str(len(playlists)))
                    return playlists

        except Exception as e:
            print(e)
            return None

    def get_last_page_token(self, video_id):
        """
        Return the page token corresponding to the first comments on a video

        :param video_id: The video id

        :return last_page_token: the token used to get comments from the last page
        """

        next_page_token = ""
        next_page_tokens = []

        try:
            while next_page_token is not None:
                response = self.api.commentThreads().list(
                    videoId=video_id,
                    part='id',
                    maxResults=100).execute()

                next_page_token = response.get('nextPageToken')
                next_page_tokens.append(next_page_token)
                print(next_page_token)
            return next_page_tokens
        except Exception as e:
            print(e)
            return next_page_tokens

    @staticmethod
    def parse_video_to_youtube_video(video):
        """
        Creates a Youtube Video object from a video response from the Youtube Data API

        :param video: the Youtube json response for a video

        :return: YoutubeVideo
        """

        youtube_video = YoutubeVideo()

        try:
            snippet = video['snippet']
            statistics = video['statistics']
        except Exception as E:
            print('Full video parts not found')
            snippet = {}
            statistics = {}

        youtube_video.youtube_video_id = video['id']
        youtube_video.youtube_author_id = snippet.pop('channelId', None)
        youtube_video.author_id = 'youtube.com' + str(snippet.pop('channelId', None))
        youtube_video.author_name = snippet.pop('channelTitle', None)
        youtube_video.title = snippet.pop('title', None)
        youtube_video.description = snippet.pop('description', None)
        raw_time = snippet.pop('publishedAt', None)
        if raw_time is None:
            youtube_video.publish_date = None
        else:
            youtube_video.publish_date = datetime.strptime(raw_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        youtube_video.view_count = statistics.pop('viewCount', 0)
        youtube_video.like_count = statistics.pop('likeCount', 0)
        youtube_video.dislike_count = statistics.pop('dislikeCount', 0)
        youtube_video.comment_count = statistics.pop('commentCount', 0)

        return youtube_video

    @staticmethod
    def parse_comment_to_youtube_comment(comment):
        """
        Creates a Youtube Comment Mention object from a comment from the Youtube Data API

        :param comment: the Youtube json response for a video comment

        :return: YoutubeTextComment
        """

        youtube_comment = YoutubeTextComment()

        youtube_comment.youtube_comment_id = comment['id']
        youtube_comment.domain = 'youtube.com'
        youtube_comment.source = 'Youtube API'

        try:
            youtube_comment.youtube_author_id = comment['snippet']['topLevelComment']['snippet']['authorChannelId'][
                'value']
            youtube_comment.author_id = 'youtube.com' + comment['snippet']['topLevelComment']['snippet'] \
                                                               ['authorChannelId']['value']
        except Exception as e:
            print(e)
            youtube_comment.youtube_author_id = 'Not Found'
            youtube_comment.author_id = 'Not Found'

        youtube_comment.author_name = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
        youtube_comment.date = datetime.strptime(comment['snippet']['topLevelComment']['snippet']['publishedAt'],
                                                 '%Y-%m-%dT%H:%M:%S.%fZ')
        youtube_comment.snippet = comment['snippet']['topLevelComment']['snippet']['textDisplay']
        youtube_comment.youtube_video_id = comment['snippet']['topLevelComment']['snippet']['videoId']
        youtube_comment.like_count = comment['snippet']['topLevelComment']['snippet']['likeCount']
        youtube_comment.reply_count = comment['snippet']['totalReplyCount']
        youtube_comment.profile_picture = comment['snippet']['topLevelComment']['snippet']['authorProfileImageUrl']

        return youtube_comment

    @staticmethod
    def parse_user_to_common_user(user):
        """
        Creates a common user from a user (channel) object from the Youtube API

        :param user: the Youtube json response

        :return: User, used by unified_import
        """

        common_user = User()

        common_user.author_id = 'youtube.com' + str(user['id'])
        common_user.domain = 'youtube.com'
        common_user.source = 'YoutubeAPI'
        common_user.author_fullname = None
        common_user.author_username = user['snippet']['title']
        common_user.bio = user['snippet']['description']
        common_user.profilepictureurl = user['snippet']['thumbnails']['high']['url']

        return common_user


    @staticmethod
    def parse_user_to_youtube_user(user):
        """
        Creates a common user from a user (channel) object from the Youtube API

        :param user: the Youtube json response

        :return: YoutubeUser
        """

        youtube_user = YoutubeUser()

        youtube_user.youtube_author_id = str(user['id'])
        youtube_user.author_id = 'youtube.com' + str(user['id'])
        youtube_user.domain = 'youtube.com'
        youtube_user.source = 'YoutubeAPI'
        youtube_user.author_fullname = None
        youtube_user.author_username = user['snippet']['title']
        youtube_user.bio = user['snippet']['description']
        youtube_user.profilepictureurl = user['snippet']['thumbnails']['high']['url']
        youtube_user.view_count = user['statistics']['viewCount']
        youtube_user.comment_count = user['statistics']['commentCount']
        youtube_user.subscriber_count = user['statistics']['subscriberCount']
        youtube_user.hidden_subscriber_count = user['statistics']['hiddenSubscriberCount']
        youtube_user.video_count = user['statistics']['videoCount']

        return youtube_user

    @staticmethod
    def parse_comment_to_common_user(comment):
        """
        Creates a common user from a comment object from the Youtube API

        :param comment: the Youtube json response

        :return: CommonUser
        """

        common_user = User()

        user = comment['snippet']['topLevelComment']['snippet']

        common_user.author_id = 'youtube.com' + str(user['authorChannelId']['value'])
        common_user.domain = 'youtube.com'
        common_user.source = 'YoutubeAPI'
        common_user.author_fullname = None
        common_user.author_username = user['authorDisplayName']
        common_user.bio = None
        common_user.profilepictureurl = user['authorProfileImageUrl']

        return common_user

    @staticmethod
    def parse_comment_to_common_mention(comment):
        """
        Creates a Text Comment Mention object from a comment from the Youtube Data API

        :param comment: the Youtube json response for a video comment

        :return: TextMention
        """

        common_comment = TextMention()

        common_comment.doc_id = comment['snippet']['topLevelComment']['snippet']['textDisplay'] + \
            'https://www.youtube.com/watch?v='+str(comment['snippet']['videoId'])
        common_comment.url = 'https://www.youtube.com/watch?v='+str(comment['snippet']['videoId'])
        common_comment.domain = 'youtube.com'
        common_comment.source = 'YoutubeAPI'

        try:
            common_comment.author_id = 'youtube.com' + comment['snippet']['topLevelComment']['snippet']\
                                                               ['authorChannelId']['value']
        except Exception as e:
            print(e)
            common_comment.author_id = 'Not Found'

        common_comment.dategmt = datetime.strptime(comment['snippet']['topLevelComment']['snippet']['publishedAt'],
                                                 '%Y-%m-%dT%H:%M:%S.%fZ')
        common_comment.datelocal = None
        common_comment.datelocalzone = None
        common_comment.snippet = comment['snippet']['topLevelComment']['snippet']['textDisplay']

        common_comment.sentiment = None
        common_comment.location = None
        common_comment.lat = None
        common_comment.long = None

        return common_comment