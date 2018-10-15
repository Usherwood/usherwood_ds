#!/usr/bin/env python

"""The binary column class of the dataframe creator, create binary sparse data (e.g. NLP outputs)"""

import numpy as np
import warnings

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


class Binary:
    """
    Produce a column of binary 1,0 values at a given ratio.
    """
    def __init__(self, name='Test Binary', n_records=50, args=None):
        """
        :param name: String column root name
        :param n_records: Int number of rows per column
        :param args:
            - perc_ones: decimal, the percentage of ones to appear in the binary data
        """

        if not args:
            args = {}

        self.name = name
        self.n_records = n_records
        self.perc_ones = args.pop('perc_ones', .05)

        if len(args.keys()) > 0:
            for key in args.keys():
                warnings.warn('Unused key:'+str(key))

        self.col = self.create_array()

    def create_array(self):
        """
        Standard class method to produce the list to be used as a column

        :return: List, the column
        """

        col = np.random.rand(self.n_records)
        split = col < self.perc_ones
        col[split] = 1
        col[~split] = 0
        col = col.astype(int)

        return col
