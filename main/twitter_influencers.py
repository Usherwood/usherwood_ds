#!/usr/bin/env python

"""Class for finding Twitter influencers"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"

import pandas as pd
import numpy as np
import csv
import json
import os

from scipy.stats import percentileofscore
import progressbar

from main.data_imports.twitter_import import create_twitter_user_df
from main.data_imports.twitter_api.api_class import TwitterAPI


def influencer_identification(handles,
                              save_path='',
                              TOP_X_CONNECTED=2000,
                              api_credentials=None,
                              inc_tiers=True,
                              tiers=[1500, 5000, 20000, 100000],
                              TOP_X_PER_TIER=-1):
    """
    Run the analysis to find the top influential accounts on Twitter. This is the full influencer analysis, for a
    quicker insight run interests_identification.

    :param handles: List of Twitter handles
    :param save_path: path of where save the dataframes to
    :param TOP_X_CONNECTED: Int, take the top_x_connect influencers
    :param api_credentials: Dict, api credentials
    :param inc_tiers: Bool, divide rankings by number of followers
    :param tiers: List, ascending list of integers as the upper boundaries of follower numbers per tier, a final tier
    will be added for uses with more followers than your last divide
    :param TOP_X_PER_TIER: int, keep only top x per influence tier, -1 is all, good for power BI
    """

    if api_credentials is None:
        with open(os.path.join(os.path.dirname(__file__), "data_imports/api_credentials.json"), 'r') as openfile:
            api_credentials = json.load(openfile)

    api = TwitterAPI(api_credentials=api_credentials)

    print('Fortifying target market')
    target_market, TM_SIZE = fortify_tm_with_previous_posts(handles=handles, save_path=save_path, api=api)
    print('Getting sphere of influence')
    influencers = get_sphere_of_influence(target_market=target_market, save_path=save_path, api=api)
    print('Fortifying sphere of influence and getting amplification')
    influencers = get_amplification_influencers(influencers=influencers,
                                                api=api,
                                                TM_SIZE=TM_SIZE,
                                                TOP_X_CONNECTED=TOP_X_CONNECTED,
                                                save_path=save_path,
                                                tiers=tiers,
                                                TOP_X_PER_TIER=TOP_X_PER_TIER)
    print('Calculating Engagement and overall influence')
    influencers = get_engagement_influencers(influencers=influencers,
                                             target_market=target_market,
                                             save_path=save_path,
                                             TOP_X_PER_TIER=TOP_X_PER_TIER)
    print('Done')

    return target_market, influencers


def interests_identification(handles, save_path='', TOP_X_CONNECTED=2000, api_credentials=None, TOP_X_PER_TIER=-1):
    """
    Run the analysis to find the top amplifying accounts on Twitter, good for identifying interests or quick influencer
    analysis. For full influencer analysis use the influencers_identification function as it calculates
    engagement scores

    :param handles: List of Twitter handles
    :param save_path: path of where save the dataframes to
    :param TOP_X_CONNECTED: Int, take the top_x_connect influencers
    :param api_credentials: Dict, api credentials
    :param TOP_X_PER_TIER: int, keep only top x per influence tier, -1 is all, good for power BI
    """

    if api_credentials is None:
        with open(os.path.join(os.path.dirname(__file__), "../api_credentials.json"), 'r') as openfile:
            api_credentials = json.load(openfile)

    api = TwitterAPI(api_credentials=api_credentials)

    print('Fortifying target market')
    target_market, TM_SIZE = fortify_tm_without_engamements(handles=handles, save_path=save_path, api=api)
    print('Getting sphere of influence')
    influencers = get_sphere_of_influence(target_market, save_path=save_path, api=api)
    print('Fortifying sphere of influence and getting amplification')
    influencers = get_amplification_influencers(influencers=influencers,
                                                api=api,
                                                TM_SIZE=TM_SIZE,
                                                TOP_X_CONNECTED=TOP_X_CONNECTED,
                                                save_path=save_path,
                                                TOP_X_PER_TIER=TOP_X_PER_TIER)
    print('Done')

    return target_market, influencers


def fortify_tm_without_engamements(handles, api, save_path=''):
    """
    fortify the tm with user info without engagement measures

    :param handles: List of Twitter handles
    :param api: TwitterAPI instance
    :param save_path: path of where save the dataframes to

    :return: target_market - pandas df of fortified Twitter users and their engagements
    """

    users = api.fortify_twitter_users_batch(usernames=handles)

    TM_SIZE = len(users)

    print(TM_SIZE)

    target_market_arr = []
    for user in users:
        target_market_arr += [api.parse_user_to_twitter_user(user)]

    target_market = create_twitter_user_df(target_market_arr)

    target_market.to_csv(save_path+'TM.csv', encoding='utf-8', quoting=csv.QUOTE_ALL, index=False)

    return target_market, TM_SIZE


def fortify_tm_with_previous_posts(handles, api, max_tweets=100, save_path=''):
    """
    fortify the tm with user info and past max_tweets for engagement measures

    :param handles: List of Twitter handles
    :param api: TwitterAPI instance
    :param max_tweets: Int, this is the number of tweets the engagement will be based on
    :param save_path: path of where save the dataframes to

    :return: target_market - pandas df of fortified Twitter users and their engagements
    """

    engagements = []
    users = []
    for handle in handles:
        try:
            tweets, user = api.get_user_tweets(username=handle, max_number=max_tweets)
            print(user['screen_name'])
            users += [user]
            at_mentions = []
            reply_to = []
            retweets = []
            for tweet in tweets:
                try:
                    user_mention_blocks = tweet['entities']['user_mentions']
                    for block in user_mention_blocks:
                        at_mentions += [block['id']]
                except Exception as e:
                    pass
                try:
                    if tweet['in_reply_to_user_id']:
                        reply_to += [tweet['in_reply_to_user_id']]
                except Exception as e:
                    pass
                try:
                    retweets += [tweet['retweeted_status']['user']['id']]
                except Exception as e:
                    pass
            engagements.append(at_mentions + reply_to + retweets)
        except Exception as e:
            print(e)


    target_market_arr = []
    for user in users:
        target_market_arr += [api.parse_user_to_twitter_user(user)]

    target_market = create_twitter_user_df(target_market_arr)
    target_market['Engagements in Past 100 Tweets'] = engagements

    target_market = target_market[target_market['Engagements in Past 100 Tweets'].astype(str) != '[]']

    TM_SIZE = len(target_market)

    target_market.to_csv(save_path+'TM.csv', encoding='utf-8', quoting=csv.QUOTE_ALL, index=False)

    return target_market, TM_SIZE


def get_sphere_of_influence(target_market, api, save_path=''):
    """
    Get the people the target market are following and rank by the most connected

    :param target_market:
    :param api: TwitterAPI instance
    :param save_path: path of where save the dataframes to

    :return: partially populated influencers df
    """

    sphere = []
    with progressbar.ProgressBar(max_value=len(target_market['Twitter Author ID'])) as bar:
        for i, user_id in enumerate(target_market['Twitter Author ID'].values.tolist()):
            friends = api.get_user_friends_ids(user_id=user_id, max_number=5000)
            if friends is None:
                pass
            else:
                sphere += friends
            bar.update(i)

    influencers = pd.DataFrame(pd.Series(sphere).value_counts()).reset_index().rename(
        columns={'index': 'Twitter Author ID', 0: 'TM Amplification'})

    influencers.to_csv(save_path+'Influencers.csv', encoding='utf-8', quoting=csv.QUOTE_ALL, index=False)

    return influencers


def get_amplification_influencers(TM_SIZE,
                                  api,
                                  TOP_X_CONNECTED=2000,
                                  save_path='',
                                  influencers=None,
                                  load_from_disk=False,
                                  load_path='',
                                  tiers=[1500,5000,20000,100000],
                                  TOP_X_PER_TIER=-1):
    """
    Fortify the influencers df for the top_x_connected influencers

    :param influencers: influencers df output from get_sphere_of_influence
    :param TM_SIZE: Int, the size of the target market
    :param TOP_X_CONNECTED: Int, take the top_x_connect influencers
    :param save_path: path of where save the dataframes to
    :param load_from_disk: Bool, load previously ran influencer sdata from disk
    :param load_path: Str, path to the saved data if it is to be loaded, files must be named TM.csv and Influencers.csv
    :param tiers: List, ascending list of integers as the upper boundaries of follower numbers per tier, a final tier
    will be added for uses with more followers than your last divide
    :param TOP_X_PER_TIER: int, keep only top x per influence tier, -1 is all, good for power BI

    :return: partially populated influencers df
    """

    if load_from_disk:
        influencers = pd.read_csv(load_path+'Influencers.csv')

    influencers = influencers[:TOP_X_CONNECTED]
    influencers_jsons = api.fortify_twitter_users_batch(user_ids=influencers['Twitter Author ID'].values.tolist())

    influencers_arr = []
    for user in influencers_jsons:
        influencers_arr += [api.parse_user_to_twitter_user(user)]

    influencers_fort = create_twitter_user_df(influencers_arr)

    influencers_fort['Twitter Author ID'] = influencers_fort['Twitter Author ID'].astype(np.int64)
    influencers = influencers_fort.merge(influencers, how='inner', on='Twitter Author ID')
    influencers['Amplification Index'] = influencers[['Follower Count', 'TM Amplification']].apply(
        lambda x: x[1] * (TM_SIZE / x[0]), axis=1)
    influencers.sort_values(by='Amplification Index', inplace=True, ascending=False)

    influencers['Tier'] = 0
    tiers = tiers.copy()
    tiers = [0]+tiers+[9999999999]

    influencers = apply_tiers(influencers, tiers)
    influencers = run_indexing(influencers=influencers,
                               base_column_name='Amplification Index',
                               TOP_X_PER_TIER=-1,
                               reindexed_column_name='Amplification Index')
    influencers = run_indexing(influencers=influencers,
                               base_column_name='Amplification Index',
                               TOP_X_PER_TIER=TOP_X_PER_TIER,
                               reindexed_column_name='Amplification Index PowerBI')
    influencers.reset_index(drop=True, inplace=True)
    influencers['Channel'] = 'Twitter'
    influencers.to_csv(save_path+'Influencers.csv', encoding='utf-8', quoting=csv.QUOTE_ALL, index=False)

    return influencers


def get_engagement_influencers(target_market=None,
                               influencers=None,
                               save_path='',
                               load_from_disk=False,
                               load_path='',
                               TOP_X_PER_TIER=-1):
    """
    Fortify influencers df with amplification

    :param influencers: influencers df
    :param target_market: target market df
    :param save_path: path of where save the dataframes to
    :param load_from_disk: Bool, load previously ran influencer sdata from disk
    :param load_path: Str, path to the saved data if it is to be loaded, files must be named TM.csv and influencers.csv
    :param TOP_X_PER_TIER: int, keep only top x per influence tier, -1 is all, good for power BI

    :return: influencers df fortified with tm engagement and overall influence
    """

    if load_from_disk:
        influencers = pd.read_csv(load_path+'influencers.csv')
        target_market = pd.read_csv(load_path+'TM.csv')

    if isinstance(target_market['Engagements in Past 100 Tweets'].iloc[0], str):
        target_market['Engagements in Past 100 Tweets'] = target_market['Engagements in Past 100 Tweets']\
            .apply(lambda e: eval(e))

    all_tm_engagements = [item for sublist in target_market['Engagements in Past 100 Tweets'].values.tolist() for item
                          in sublist]

    def get_tm_eng_count(influencer_id, all_tm_engagements):
        eng_counts = len([1 for ix in all_tm_engagements if ix == influencer_id])
        return eng_counts

    influencers['TM Engagement'] = influencers['Twitter Author ID'].apply(
        lambda x: get_tm_eng_count(x, all_tm_engagements))

    influencers['Engagement Index'] = influencers['TM Engagement']/influencers['TM Amplification']

    influencers = run_indexing(influencers=influencers,
                               base_column_name='Engagement Index',
                               TOP_X_PER_TIER=-1,
                               reindexed_column_name='Engagement Index')
    influencers = run_indexing(influencers=influencers,
                               base_column_name='Engagement Index',
                               TOP_X_PER_TIER=TOP_X_PER_TIER,
                               reindexed_column_name='Engagement Index PowerBI')

    influencers['Influence Index'] = (influencers['Engagement Index']+influencers['Amplification Index'])/2.0
    influencers['Influence Index PowerBI'] = (influencers['Engagement Index PowerBI']\
                                              + influencers['Amplification Index PowerBI']) / 2.0

    influencers.to_csv(save_path+'Influencers.csv', encoding='utf-8', quoting=csv.QUOTE_ALL, index=False)

    return influencers


def apply_tiers(influencers, tiers):
    for tier_ix in range(len(tiers) - 1):
        sub = influencers[(influencers['Follower Count'] >= tiers[tier_ix]) &
                          (influencers['Follower Count'] < tiers[tier_ix + 1])]
        influencers.ix[sub.index, 'Tier'] = 'Tier ' + str(tier_ix + 1)
    return influencers


def run_indexing(influencers,
                 TOP_X_PER_TIER=-1,
                 base_column_name='Amplification Index',
                 reindexed_column_name='Amplification Index'):
    if reindexed_column_name not in influencers.columns:
        influencers[reindexed_column_name] = 0

    for tier_ix in influencers['Tier'].value_counts().index:
        sub = influencers[(influencers['Tier'] == tier_ix)]

        arr = sorted(sub[base_column_name].values)
        if TOP_X_PER_TIER >= 0:
            arr = arr[-TOP_X_PER_TIER:]
        influencers.ix[sub.index, reindexed_column_name] = sub[base_column_name]. \
            apply(lambda e: percentileofscore(arr, e)).values

    return influencers
