#!/usr/bin/env python

"""Run a query on reddit and return all comments from matching posts within a time frame"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


import time
import os

import progressbar

from usherwood_ds.data_imports.reddit_api.api_class import RedditAPI
from usherwood_ds.data_imports.unified_import import create_common_df


def search_comments_to_excel(query='dogs',
                             subreddit='funny',
                             max_posts=500,
                             date={'day': 1, 'month': 12, 'year': 2017},
                             root_dir='D:/documents/work/projects/api_data/'):

    api = RedditAPI()

    posts = api.get_subreddit_posts(subreddit=subreddit, query=query, max_posts=max_posts,
                                    date=date)

    print(str(len(posts)), 'posts found')
    comments = []
    for post in posts:
        comments += api.get_submission_comments(submission=post)

    print(str(len(comments)), 'comments found')
    mentions = []
    users = []
    with progressbar.ProgressBar(max_value=len(comments)) as bar:
        for i, comment in enumerate(comments):
            try:
                mentions += [api.parse_comment_to_common_mention(comment)]
                users += [api.parse_comment_to_common_user(comment)]
            except Exception as e:
                print(e)
            bar.update(i)

    df = create_common_df(mention_list=mentions, user_list=users)

    filename = 'downloads/reddit_search_comments_query_'+str(query)+'_'+str(time.time())+'.xlsx'

    df.to_excel(os.path.join(root_dir, filename))

    return filename


if __name__ == "__main__":
    search_comments_to_excel()
