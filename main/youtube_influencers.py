#!/usr/bin/env python

"""Class for finding Youtube influencers"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"

import pandas as pd
import csv
import json
import os

from scipy.stats import percentileofscore
import progressbar

from main.data_imports.youtube_api.api_class import YoutubeAPI
from main.data_imports.youtube_import import create_youtube_user_df, create_youtube_comment_df

import warnings
warnings.filterwarnings('ignore')


YT_SIZE = 300000000


def interests_identification(handles=None,
                             similar_videos=None,
                             max_comments_per_similar_influencer_video=-1,
                             save_path='',
                             TOP_X_CONNECTED=2000,
                             api_credentials=None):
    """
    Run the analysis to find the top amplifying accounts on Youtube, good for identifying interests or quick influencer
    analysis. For full influencer analysis use the influencers_identification function as it calculates
    engagement scores

    :param handles: List of Youtube handles
    :param similar_videos: List of similar influencer video ids
    :param max_comments_per_similar_influencer_video: Int, when search similar videos cap num comments retrieved to give
    a rough cap on TM size
    :param save_path: path of where save the dataframes to
    :param TOP_X_CONNECTED: Int, take the top_x_connect influencers
    :param api_credentials: Dict, api credentials
    """

    if api_credentials is None:
        with open(os.path.join(os.path.dirname(__file__), "data_imports/api_credentials.json"), 'r') as openfile:
            api_credentials = json.load(openfile)

    api = YoutubeAPI(api_credentials=api_credentials)

    if not handles:
        print('Getting TM from similar influencers')
        tm_ids = retrieve_similar_influencer_auidence(api,
                                                      save_path=save_path,
                                                      video_ids=similar_videos,
                                                      num_comments=max_comments_per_similar_influencer_video)



    print('Fortifying target market')
    target_market, TM_SIZE = fortify_tm_without_engamements(tm_ids=tm_ids, save_path=save_path, api=api)
    print('Getting sphere of influence')
    influencers = get_sphere_of_influence(target_market, save_path=save_path, api=api)
    print('Fortifying sphere of influence and getting amplification')
    influencers = get_amplification_influencers(influencers=influencers,
                                                api=api,
                                                TM_SIZE=TM_SIZE,
                                                TOP_X_CONNECTED=TOP_X_CONNECTED,
                                                save_path=save_path)
    print('Done')

    return target_market, influencers


def retrieve_similar_influencer_auidence(api,
                                         save_path='',
                                         video_ids=['tUtLHo7UQMM'],
                                         num_comments=-1):  # max
    comments = []
    for video_id in video_ids:
        comments += api.get_video_comments(video_id, num_comments=num_comments)
        print(str(len(comments)), 'comments found.')

    parsed_comments = []
    for comment in comments:
        parsed_comments += [api.parse_comment_to_youtube_comment(comment)]
    df_comments = create_youtube_comment_df(parsed_comments)

    target_market_ids = pd.DataFrame(df_comments['Youtube Author ID'].value_counts().index,
                                     columns=['Youtube Channel ID'])
    target_market_ids.to_csv(save_path + 'TM.csv', encoding='utf-8', quoting=csv.QUOTE_ALL, index=False)

    return target_market_ids


def fortify_tm_without_engamements(tm_ids, api, save_path=''):
    """
    fortify the tm with user info without engagement measures

    :param tm_ids: List of Youtube channel ids
    :param api: YoutubeAPI instance
    :param save_path: path of where save the dataframes to

    :return: target_market - pandas df of fortified Youtube users
    """

    channels = []
    for idx in tm_ids['Youtube Channel ID'].tolist():
        json_response = api.fortify_channel(channel_id=idx, fortify_with='snippet,statistics')
        if json_response.pop('found', True) is not False:
            channels.append(json_response)

    TM_SIZE = len(channels)

    print(TM_SIZE)

    target_market_arr = []
    for user in channels:
        target_market_arr += [api.parse_user_to_youtube_user(user)]

    target_market = create_youtube_user_df(target_market_arr)

    target_market.to_csv(save_path + 'TM.csv', encoding='utf-8', quoting=csv.QUOTE_ALL, index=False)

    return target_market, TM_SIZE


def get_sphere_of_influence(target_market, api, save_path=''):
    """
    Get the people the target market are following and rank by the most connected

    :param target_market:
    :param api: YoutubeAPI instance
    :param save_path: path of where save the dataframes to

    :return: partially populated influencers df
    """

    sphere = []
    with progressbar.ProgressBar(max_value=len(target_market['Youtube Author ID'])) as bar:
        for i, user_id in enumerate(target_market['Youtube Author ID'].values.tolist()):
            subscription_jsons = api.get_user_subscriptions(youtube_author_id=user_id)
            for sub in subscription_jsons:
                sphere += [sub['snippet']['resourceId']['channelId']]
            bar.update(i)

    influencers = pd.DataFrame(pd.Series(sphere).value_counts()).reset_index().rename(
        columns={'index': 'Youtube Author ID', 0: 'TM Amplification'})

    influencers.to_csv(save_path + 'Influencers.csv', encoding='utf-8', quoting=csv.QUOTE_ALL, index=False)

    return influencers


def get_amplification_influencers(TM_SIZE,
                                  api,
                                  TOP_X_CONNECTED=2000,
                                  save_path='',
                                  influencers=None,
                                  load_from_disk=False,
                                  load_path='',
                                  inc_tiers=True,
                                  tiers=[1500, 5000, 20000, 100000]):
    """
    Fortify the influencers df for the top_x_connected influencers

    :param influencers: influencers df output from get_sphere_of_influence
    :param TM_SIZE: Int, the size of the target market
    :param TOP_X_CONNECTED: Int, take the top_x_connect influencers
    :param save_path: path of where save the dataframes to
    :param load_from_disk: Bool, load previously ran influencer sdata from disk
    :param load_path: Str, path to the saved data if it is to be loaded, files must be named TM.csv and Influencers.csv
    :param inc_tiers: Bool, divide rankings by number of followers
    :param tiers: List, ascending list of integers as the upper boundaries of follower numbers per tier, a final tier
    will be added for uses with more followers than your last divide

    :return: partially populated influencers df
    """

    if load_from_disk:
        influencers = pd.read_csv(load_path + 'Influencers.csv')

    influencers = influencers[:TOP_X_CONNECTED]

    influencers_jsons = []
    with progressbar.ProgressBar(max_value=len(influencers['Youtube Author ID'])) as bar:
        for i, idx in enumerate(influencers['Youtube Author ID'].values.tolist()):
            influencers_jsons += [api.fortify_channel(channel_id=idx, fortify_with='snippet,statistics')]
            bar.update(i)

    influencers_arr = []
    for user in influencers_jsons:
        influencers_arr += [api.parse_user_to_youtube_user(user)]

    influencers_fort = create_youtube_user_df(influencers_arr)

    influencers_fort['Youtube Author ID'] = influencers_fort['Youtube Author ID']
    influencers = influencers_fort.merge(influencers, how='inner', on='Youtube Author ID')
    influencers['Amplification Index'] = influencers[['Subscriber Count', 'TM Amplification']].apply(
        lambda x: (x[1] / TM_SIZE) * (TM_SIZE / x[0]), axis=1)
    influencers.sort_values(by='Amplification Index', inplace=True, ascending=False)

    influencers['Tier'] = 0
    tiers = tiers.copy()
    tiers = [0] + tiers + [9999999999]
    for tier_ix in range(len(tiers) - 1):
        sub = influencers[(influencers['Subscriber Count'] >= tiers[tier_ix]) &
                          (influencers['Subscriber Count'] < tiers[tier_ix + 1])]

        arr = sorted(sub['Amplification Index'].values)
        influencers.ix[sub.index, 'Amplification Index'] = sub['Amplification Index']. \
            apply(lambda e: percentileofscore(arr, e)).values

        influencers.ix[sub.index, 'Tier'] = tier_ix + 1

    influencers.reset_index(drop=True, inplace=True)
    influencers.to_csv(save_path + 'Influencers.csv', encoding='utf-8', quoting=csv.QUOTE_ALL, index=False)

    return influencers
