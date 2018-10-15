#!/usr/bin/env python

"""Return and save the top x comments in a Youtube video with meta variables"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"

import os
import time

from usherwood_ds.data_imports.youtube_api.api_class import YoutubeAPI
from usherwood_ds.data_imports.youtube_import import create_youtube_comment_df


def video_comments_to_excel(video_id='sr6lr_VRsEo',
                            num_comments=-1, #Max
                            root_dir='D:/documents/work/projects/api_data/'):

    api = YoutubeAPI()

    comments = api.get_video_comments(video_id, num_comments=num_comments)
    print(str(len(comments)), 'comments found.')

    parsed_comments = []
    for comment in comments:
        parsed_comments += [api.parse_comment_to_youtube_comment(comment)]
    df_comments = create_youtube_comment_df(parsed_comments)

    filename = 'downloads/youtube_comments_'+str(video_id)+'_'+str(time.time())+'.xlsx'

    df_comments.to_excel(os.path.join(root_dir, filename))

    return filename


if __name__ == "__main__":
    video_comments_to_excel()