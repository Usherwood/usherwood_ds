#!/usr/bin/env python

"""Return and save the top x comments in a Youtube video with meta variables"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

import csv

from main.data_imports.youtube_api.api_class import YoutubeAPI
from main.data_imports.youtube_import import create_youtube_comment_df

video_id = 'sr6lr_VRsEo'
num_comments = -1 #Max
save_path = 'C:/Users/usherwoodp/Documents/projects'

api = YoutubeAPI()

comments = api.get_media_comments(video_id, num_comments=num_comments)
print(str(len(comments)), 'comments found.')

parsed_comments = []
for comment in comments:
    parsed_comments += [api.parse_comment_to_youtube_comment(comment)]
df_comments = create_youtube_comment_df(parsed_comments)

df_comments.to_csv(save_path+'/youtube_comments_'+str(video_id)+'.csv',
                   encoding='utf-8',
                   quoting=csv.QUOTE_ALL,
                   index=False)
