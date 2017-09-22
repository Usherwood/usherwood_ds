#!/usr/bin/env python

"""Get all videos for a particular channel, also get all comments for each video, and save all objects a summary
excel"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

import pandas as pd

from main.data_imports.youtube_api.utils.api_class import YoutubeAPI
from main.data_imports.youtube_api.utils.to_pandas import create_youtube_video_df, create_youtube_comment_df

youtube_author_id = 'UCa1yUHQmV6Z0PpAUtfgNd9g'
save_path = 'C:/Users/usherwoodp/Documents/projects/'
video_comment_filter_max_comment_count = -1
video_comment_filter_start_date = '2016-11-01' #yyyy-mm-dd
video_comment_filter_end_date = '2017-02-28' #yyyy-mm-dd


api = YoutubeAPI()


def get_user_video_ids(api, youtube_author_id):

    video_ids = []

    playlists = api.get_user_playlists(youtube_author_id=youtube_author_id)

    for playlist in playlists:
        video_ids += api.get_playlist_video_ids(playlist['id'])

    print('Total videos found:', str(len(video_ids)))

    return video_ids


def get_video_comments_df(api, video_id, max_comments):

    try:
        comments = api.get_video_comments(video_id=video_id,
                                          num_comments=max_comments)
        print(str(len(comments)), 'comments found.')

        parsed_comments = []
        for comment in comments:
            parsed_comments += [api.parse_comment_to_youtube_comment(comment)]
        df_comments = create_youtube_comment_df(parsed_comments)

        return df_comments
    except Exception as e:
        print('Cant retrieve comments for', video_id)
        return None


def create_comment_pages(api,
                         df_video,
                         video_comment_filter_max_comment_count):

    comment_pages = []

    for index in df_video.index:

        if df_video.ix[index, 'Comments Found'] == 'Searching':

            video_id = df_video.ix[index, 'Youtube Video ID']
            video_title = df_video.ix[index, 'Title']

            print('Getting', str(video_id), 'comments...')

            df_comments = get_video_comments_df(api,
                                                video_id,
                                                video_comment_filter_max_comment_count)

            if df_comments is not None:
                comments_found = True
                df_video.set_value(col='Comments Found', index=index, value='Found')
                comment_pages.append({'id': video_id, 'title': video_title, 'df': df_comments, 'found': comments_found})
            else:
                df_video.set_value(col='Comments Found', index=index, value='Not Found')

    return comment_pages


def make_summary_excel(videos_df, comment_pages):
    writer = pd.ExcelWriter(save_path +
                            'campaign_summary_author=' +
                            str(youtube_author_id) + '_range_' +
                            str(video_comment_filter_start_date) +
                            '_to_' +
                            str(video_comment_filter_end_date) +
                            '.xlsx', engine='xlsxwriter')

    videos_df.to_excel(excel_writer=writer, sheet_name='Video Summary')
    for page in comment_pages:
        print(page['title'])
        page['df'].to_excel(excel_writer=writer, sheet_name=page['id'])

    writer.close()

    return True

# Get all video ids for a user
video_ids = get_user_video_ids(api,
                               youtube_author_id)

# Fortify all videos
video_jsons = []
for video_id in video_ids:
    video_jsons += [api.fortify_video(video_id)]

parsed_videos = []
for video in video_jsons:
    parsed_videos += [api.parse_video_to_youtube_video(video)]

df_video = create_youtube_video_df(parsed_videos)

df_video['Comments Found'] = 'Searching'

df_video.ix[(df_video['Publish Date'] < video_comment_filter_start_date)|
            (df_video['Publish Date'] > video_comment_filter_end_date),'Comments Found'] = 'Out of Date Range'

df_video.ix[df_video['Publish Date'].apply(lambda e: str(e)) == 'NaT', 'Comments Found'] = 'Video Unavailable'

comment_pages = create_comment_pages(api,
                                     df_video,
                                     video_comment_filter_max_comment_count)

make_summary_excel(df_video,
                   comment_pages)
