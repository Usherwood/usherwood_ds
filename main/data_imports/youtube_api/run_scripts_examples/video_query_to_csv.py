#!/usr/bin/env python

"""Run a query on youtube and save the top x video search results with meta variables"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

import csv

from utils.api_class import YoutubeAPI
from utils.to_pandas import create_youtube_video_df

query = 'dogs'
max_videos = 50
save_path = 'C:/Users/usherwoodp/Documents/projects'

api = YoutubeAPI()

videos = api.get_videos_by_search_term('dogs', max_videos=50, location=None)
print(str(len(videos)), 'videos found')

parsed_videos = []
for video in videos:
    parsed_videos += [api.parse_video_to_youtube_video(video)]
df_video = create_youtube_video_df(parsed_videos)

df_video.to_csv(save_path+'/youtube_video_query_'+str(query)+'.csv',
                encoding='utf-8',
                quoting=csv.QUOTE_ALL,
                index=False)
