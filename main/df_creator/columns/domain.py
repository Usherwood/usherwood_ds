#!/usr/bin/env python

"""The domain column class of the dataframe creator, creates random domains, however specific pre-built patterns can
be used, e.g. Twitter"""

import numpy as np
import random
import warnings

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


class Domain:
    """
    Produce a column of random floats in a range.
    """
    def __init__(self, name='Test Domain', n_records=50, args=None):
        """
        :param name: String column root name
        :param n_records: Int number of rows per column
        :param args:
            - twitter: float, the % of Tweet urls
        """

        if not args:
            args = {}
        self.name = name
        self.n_records = n_records

        twitter_perc = args.pop('twitter', .5)
        self.num_twitter = int(twitter_perc*self.n_records)
        self.num_other = n_records - (self.num_twitter)

        if len(args.keys()) > 0:
            for key in args.keys():
                warnings.warn('Unused key:'+str(key))

        self.col = self.create_array()

    def create_array(self):
        """
        Standard class method to produce the list to be used as a column

        :param num_other: Int, the number of non-specific domains to generate (this and all others should sum to
                          n_records)
        :param num_twitter: Int, the number of Tweet URLs to generate (this and all others should sum to n_records)

        :return: List, the column
        """

        col = []

        col += self.twitter_domains()
        col += self.other_domains()

        return col

    def twitter_domains(self):
        """
        Create a list of random Tweet URLs

        :return: List of length num_twitter of random Tweet URLs
        """

        random_tweet_ids = np.random.randint(low=1000000,
                                             high=100000000,
                                             size=self.num_twitter)

        col = ['https://twitter.com/day9tv/status/'+str(rand_id) for rand_id in random_tweet_ids]

        return col

    def other_domains(self):
        """
        Create a list of random domains

        :return: List of length num_other of random domains
        """

        col = ['facebook.com']*self.num_other

        return col
