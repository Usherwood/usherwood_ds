#!/usr/bin/env python

"""Run a query on youtube and save the top x video search results with meta variables"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

import os
import time

from usherwood_ds.data_imports.youtube_api.api_class import YoutubeAPI
from usherwood_ds.data_imports.youtube_import import create_youtube_video_df


def video_query_to_excel(query='dogs',
                         max_videos=50,
                         root_dir='D:/documents/work/projects/api_data/'):

    api = YoutubeAPI()

    videos = api.get_videos_by_search_term(query, max_videos=max_videos, location=None)
    print(str(len(videos)), 'videos found')

    parsed_videos = []
    for video in videos:
        parsed_videos += [api.parse_video_to_youtube_video(video)]
    df_video = create_youtube_video_df(parsed_videos)

    filename = 'downloads/youtube_video_query_'+str(query)+'_'+str(time.time())+'.xlsx'

    df_video.to_excel(os.path.join(root_dir, filename))

    return filename


if __name__ == "__main__":
    video_query_to_excel(root_dir='C:/Users/UsherwoodP/Documents/youtube_app_fix/')
