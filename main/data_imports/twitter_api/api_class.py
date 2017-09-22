#!/usr/bin/env python

"""Class for querying the Twitter API"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

import json
import os
import tweepy
import time
from datetime import datetime
import math
import io
from tweepy.streaming import StreamListener
from tweepy import Stream

from requests.exceptions import Timeout, ConnectionError
import ssl

from main.data_imports.import_classes.twitter_classes import TwitterTextMention, TwitterUser
from main.data_imports.import_classes.common_classes import TextMention, User


with open(os.path.join(os.path.dirname(__file__), "../api_credentials.json"),'r') as openfile:
    api_credentials = json.load(openfile)


class TwitterAPI:

    def __init__(self,
                 api_credentials=api_credentials,
                 run_time=1200,
                 save_increment=600,
                 stream_save_path='raw_tweets.json'):

        self.consumer_key = api_credentials["Twitter"]["consumer_key"]
        self.consumer_secret = api_credentials["Twitter"]["consumer_secret"]
        self.access_token_key = api_credentials["Twitter"]["access_token_key"]
        self.access_token_secret = api_credentials["Twitter"]["access_token_secret"]
        self.api = None
        self.stream_api = None
        self.setup_api(run_time=run_time,
                       save_incrememnt=save_increment,
                       stream_save_path=stream_save_path)

    def setup_api(self,
                  run_time,
                  save_incrememnt,
                  stream_save_path):
        """
        Setup the API, ran during the init
        """

        l = StdOutListener(time_limit=run_time,
                           save_increment=save_incrememnt,
                           stream_save_path=stream_save_path)

        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token_key, self.access_token_secret)

        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.stream_api = Stream(auth, l)

        return True

    def fortify_twitter_tweet(self, tweet_id):
        """
        Fortifies data from a Tweet ID

        :param tweet_id: Twitter Tweet ID

        :return: json response of fortified Tweet
        """

        tweet = None
        try:
            tweet = self.api.get_status(tweet_id)
            tweet = tweet._json
        except Exception as e:
            print(e)

        return tweet

    def fortify_twitter_tweets_batch(self, tweet_ids=None):
        """
        Fortifies data for tweets in batch, much more cost efficient than fortify_twitter_tweet

        :param tweet_id: Twitter Tweet ID

        :return: list of json responses of fortified tweets and users
        """

        tweets = []
        users = []
        for chunk in chunks(tweet_ids, 100):
            try:
                batch_tweets = self.api.statuses_lookup(chunk)
                batch_tweets = [tweet._json for tweet in batch_tweets]
                batch_users = [tweet['user'] for tweet in batch_tweets]
                tweets += batch_tweets
                users += batch_users
            except Exception as e:
                print(e)

        return tweets, users

    def fortify_twitter_user(self, username=None, user_id=None):
        """
        Fortifies data from a username or user_id

        :param username: Twitter username/screen_name
        :param user_id: Twitter user_id

        :return: json response of fortified user
        """

        user = None
        try:
            if username:
                user = self.api.get_user(screen_name=username)
            elif user_id:
                user = self.api.get_user(user_id=user_id)

            user = user._json
        except Exception as e:
            print(e)

        return user

    def fortify_twitter_users_batch(self, usernames=None, user_ids=None):
        """
        Fortifies data for users in batch, much more cost efficient than fortify_twitter_user

        :param username: List containing Twitter usernames/screen_names
        :param user_id: List containing Twitter user_id

        :return: list of json responses of fortified users
        """

        users = []
        if usernames:
            for chunk in chunks(usernames, 100):
                try:
                    batch_users = self.api.lookup_users(screen_names=chunk)
                    batch_users = [user._json for user in batch_users]
                    users += batch_users
                except Exception as e:
                    print(e)
        if user_ids:
            for chunk in chunks(user_ids, 100):
                try:
                    batch_users = self.api.lookup_users(user_ids=chunk)
                    batch_users = [user._json for user in batch_users]
                    users += batch_users
                except Exception as e:
                    print(e)

        return users

    def get_user_followers(self, username=None, user_id=None, max_number=200):
        """
        Retrieves the users following the user specified by a username or user_id

        :param username: Twitter username/screen_name
        :param user_id: Twitter user_id
        :param max_number: The maximum number of Twitter followers to retrieve, 200 can be done in one api call and
        thus this makes it a good lower threshold.

        :return: list of json responses of fully fortified user objects, one json response for every follower retrieved
        """

        followers = []
        cursor = -1
        valid_run = True
        while valid_run:
            try:
                if username:
                    batch_followers = self.api.followers(screen_name=username, cursor=cursor, count=200)

                elif user_id:
                    batch_followers = self.api.followers(user_id=user_id, cursor=cursor, count=200)

                cursor = batch_followers[1][1]
                batch_followers = [follower._json for follower in batch_followers[0]]

                followers += batch_followers

                if cursor == 0:
                    valid_run = False
                elif len(followers) + 200 > max_number:
                    valid_run = False

            except Exception as e:
                print(e)

        return followers

    def get_user_tweets(self, username=None, user_id=None, max_number=20):
        """
        Retrieves the tweets of the user starting with the newest

        :param username: Twitter username/screen_name
        :param user_id: Twitter user_id
        :param max_number: The maximum number of Tweets to retrieve, 20 can be done in one api call and
        thus this makes it a good lower threshold.

        :return: list of json responses of fully fortified Tweet objects, one json response for every Tweet retrieved
        """

        tweets = []
        user = []
        try:
            if username:
                batch_tweets = self.api.user_timeline(screen_name=username, count=max_number)

            elif user_id:
                batch_tweets = self.api.user_timeline(user_id=user_id, count=max_number)

            batch_tweets = [tweet._json for tweet in batch_tweets]

            tweets += batch_tweets
            user = tweets[0]['user']
        except Exception as e:
            print(e)

        return tweets, user

    def get_user_friends_ids(self, username=None, user_id=None, max_number=5000):
        #use this function if you want to limit the number of friends retrieved in one call
        COUNTS_PPAGE = 5000
        max_page = math.ceil(max_number/COUNTS_PPAGE)
        ids = []
        try:
            if username:
                for ix, page in enumerate(tweepy.Cursor(self.api.friends_ids, screen_name=username).pages()):
                    if ix < max_page:
                        ids += page
                        if len(page) != COUNTS_PPAGE:
                            return ids
                    else:
                        return ids
                    # time.sleep(60)
            elif user_id:
                # friends = self.api.friends_ids(user_id=user_id,cursor=cursor)
                for ix, page in enumerate(tweepy.Cursor(self.api.friends_ids, user_id=user_id).pages()):
                    if ix < max_page:
                        ids += page
                        if len(page) != COUNTS_PPAGE:
                            return ids
                    else:
                        return ids
        except (Timeout, ssl.SSLError,  ConnectionError) as exc: # ReadTimeoutError,
            print('Error, retrying in 15 minutes')
            time.sleep(60*15)
            self.get_user_friends_ids(self, username=username, user_id=user_id, max_number=max_number)
        except tweepy.TweepError as re:
            print(re)
            print('Passing User')
            return []

    @staticmethod
    def parse_tweet_to_common_mention(tweet):
        """
        Creates a common text mention from a tweet from the Twitter API

        :param tweet: the Twitter json response

        :return: TextMention, used by unified_import
        """

        common_mention = TextMention()

        common_mention.doc_id = str(tweet['text']) + 'https://twitter.com/'+tweet['user']['screen_name']+\
                                '/statuses/' + str(tweet['id'])
        common_mention.domain = 'twitter.com'
        common_mention.source = 'TwitterAPI'
        common_mention.url = 'https://twitter.com/'+tweet['user']['screen_name']+'/statuses/' + str(tweet['id'])
        common_mention.author_id = 'twitter.com' + str(tweet['user']['screen_name'])
        common_mention.dategmt = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
        common_mention.datelocal = None #TODO add
        common_mention.datelocalzone = None  # TODO add
        common_mention.snippet = tweet['text']
        common_mention.sentiment = 'Not Found because it does not exist'
        common_mention.location = 'Need to Add'

        if tweet['geo'] is not None:
            common_mention.lat = tweet['geo']['coordinates'][1]
            common_mention.long = tweet['geo']['coordinates'][0]
        else:
            common_mention.lat = None
            common_mention.long = None

        return common_mention

    @staticmethod
    def parse_user_to_common_user(user):
        """
        Creates a common user from a user object from the Twitter API

        :param user: the Twitter json response

        :return: User, used by unified_import
        """

        common_user = User()

        common_user.author_id = 'twitter.com' + str(user['screen_name'])
        common_user.domain = 'twitter.com'
        common_user.source = 'TwitterAPI'
        common_user.author_fullname = user['name']
        common_user.author_username = user['screen_name']
        common_user.bio = user['description']
        common_user.profilepictureurl = user['profile_image_url_https']

        return common_user

    @staticmethod
    def parse_user_to_twitter_user(user):
        """
        Creates a Twitter user (a Twitter specific extension of the user class) from a user from the Twitter API

        :param user: the Twitter json response

        :return: TwitterUser
        """

        twitter_user = TwitterUser()

        twitter_user.twitter_author_id = str(user['id'])
        twitter_user.domain = 'twitter.com'
        twitter_user.source = 'TwitterAPI'
        twitter_user.author_fullname = user['name']
        twitter_user.author_username = user['screen_name']
        twitter_user.bio = user['description']
        twitter_user.profilepictureurl = user['profile_image_url_https']
        twitter_user.followers_count = user['followers_count']
        twitter_user.profile_image_full = user['profile_image_url_https'].replace("_normal", "")
        twitter_user.verified = user['verified']
        twitter_user.number_of_statuses = user['statuses_count']
        twitter_user.created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S %z %Y')
        twitter_user.author_id = 'twitter.com' + str(user['id'])

        return twitter_user

    @staticmethod
    def parse_tweet_to_twitter_mention(tweet):
        """
        Creates a Twitter text mention (a Twitter specific extension of the mention class) from a tweet from the
        Twitter API

        :param tweet: the Twitter json response

        :return: TwitterTextMention
        """

        twitter_mention = TwitterTextMention()

        twitter_mention.tweet_id = str(tweet['id'])
        twitter_mention.domain = 'twitter.com'
        twitter_mention.source = 'TwitterAPI'
        twitter_mention.url = 'https://twitter.com/statuses/' + str(tweet['id'])
        twitter_mention.author_id = 'twitter.com' + str(tweet['user']['id'])
        twitter_mention.dategmt = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
        twitter_mention.datelocal = None #TODO add
        twitter_mention.datelocalzone = None  # TODO add
        twitter_mention.snippet = tweet['text']
        twitter_mention.sentiment = 'Not Found'
        twitter_mention.location = 'Not added'
        twitter_mention.favorite_count = tweet['favorite_count']
        twitter_mention.device = tweet['source']
        twitter_mention.doc_id = str(tweet['text']) + 'https://twitter.com/statuses/' + str(tweet['id'])

        if tweet['geo'] is not None:
            twitter_mention.lat = tweet['geo']['coordinates'][1]
            twitter_mention.long = tweet['geo']['coordinates'][0]
        else:
            twitter_mention.lat = None
            twitter_mention.long = None
        if tweet['entities'] is not None:
            if tweet['entities'].get('media'):
                if tweet['entities']['media'] is not None:
                    if tweet['entities']['media'][0].get('media_url'):
                        twitter_mention.imageURL = tweet['entities']['media'][0]['media_url']
                    else:
                        twitter_mention.imageURL=None

        # adding retweet information
        retweeted_status = None
        try:
            retweeted_status = tweet['retweeted_status']
        except KeyError:
            pass

        if retweeted_status is not None:
            # is retweeted thus setting retweet count to 0, because otherwise it would use the retweet count
            # of original tweet (which we don't want)
            twitter_mention.retweet_count = 0
            twitter_mention.is_retweet = 1
            twitter_mention.id_of_reweet = tweet['retweeted_status']['id']
            twitter_mention.id_of_original_tweet_author = tweet['retweeted_status']['user']['id']
            twitter_mention.screen_name_of_original_tweet_author = tweet['retweeted_status']['user']['screen_name']
        else:
            twitter_mention.retweet_count = tweet['retweet_count']
            twitter_mention.is_retweet = 0

        # adding quoting info
        quoted_status = None
        try:
            quoted_status = tweet['quoted_status']
        except KeyError:
            pass

        if quoted_status is not None:
            twitter_mention.is_quoting = 1
            twitter_mention.id_of_quoted_tweet = tweet['quoted_status']['id']
            twitter_mention.id_of_quoted_author = tweet['quoted_status']['user']['id']
            twitter_mention.screen_name_of_quoted_author = tweet['quoted_status']['user']['screen_name']
        else:
            twitter_mention.is_quoting = 0

        # adding reply information
        twitter_mention.id_of_antecedent_tweet = tweet['in_reply_to_status_id']
        twitter_mention.screen_name_of_antecedent_author = tweet['in_reply_to_screen_name']
        twitter_mention.id_of_antecedent_author = tweet['in_reply_to_user_id']

        if tweet['in_reply_to_status_id'] is None:
            twitter_mention.is_response = 0
        else:
            twitter_mention.is_response = 1

        return twitter_mention


class StdOutListener(StreamListener):

    def __init__(self,
                 time_limit=60,
                 save_increment=600,
                 stream_save_path='raw_tweets.json'):

        self.time = time.time()
        self.limit = time_limit
        self.tweet_data = []
        self.save_tick = 1
        self.call_tick = 0
        self.save_increment = save_increment
        self.path = stream_save_path
        self.new_file=False

    def on_data(self, data):

        if not os.path.exists(self.path):
            saveFile = io.open(self.path, 'w', encoding='utf-8')
            self.new_file=True
            saveFile.close()
        else:
            if self.call_tick == 0:
                file = open(self.path, "r+", encoding="utf-8")
                file.seek(0, os.SEEK_END)
                pos = file.tell() - 1

                while pos > 0 and file.read(1) != "\n":
                    pos -= 1
                    file.seek(pos, os.SEEK_SET)

                if pos > 0:
                    file.seek(pos, os.SEEK_SET)
                    file.truncate()

                file.close()

        saveFile = io.open(self.path, 'a', encoding='utf-8')

        while (time.time() - self.time) < self.limit:

            try:
                self.tweet_data.append(data)
                if (time.time() - self.time) >= self.save_tick*self.save_increment:
                    print(str(len(self.tweet_data)), 'new records saved')
                    if self.save_tick == 1 and self.new_file:
                        saveFile.write(u'[\n')
                        saveFile.write(','.join(self.tweet_data))
                    else:
                        saveFile.write(','+','.join(self.tweet_data))

                    self.tweet_data = []
                    self.save_tick += 1
                self.call_tick += 1
                return True

            except Exception as e:
                print('failed ondata,', str(e))
                time.sleep(60)
                pass

        self.save_tick = 0
        self.call_tick = 0
        saveFile.write(u'\n]')
        saveFile.close()
        return False

    def on_error(self, status):
        time.sleep(60)
        print(status)


def finalize_tweet_stream(file_path='raw_tweets_closed.json'):

    saveFile = io.open(file_path, 'a', encoding='utf-8')
    saveFile.write(u'\n]\n')
    saveFile.close()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
