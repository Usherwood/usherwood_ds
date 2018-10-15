#!/usr/bin/env python

"""The numbers column class of the dataframe creator, create continuous number distributions"""

import numpy as np
import random
import warnings

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


class Number:
    """
    Produce a column of random floats in a range.
    """
    def __init__(self, name='Test Number', n_records=50, args=None):
        """
        :param name: String column root name
        :param n_records: Int number of rows per column
        :param args:
            - type: string, the type of distribution:
                - uniform, uniform distribution
                type_args:
                    - int: bool, make the values integer when true
                    - min_val: float, the minimum value to appear in the array
                    - max_val: float, the maximum value to appear in the array
        """

        if not args:
            args = {}
        self.name = name
        self.n_records = n_records
        self.type = args.pop('type', 'uniform')
        self.type_args = args.pop('type_args', {})
        self.max_val = args.pop('max_val', 100)
        self.min_val = args.pop('min_val', 0)
        self.int = args.pop('int', False)

        if len(args.keys()) > 0:
            for key in args.keys():
                warnings.warn('Unused key:'+str(key))

        self.col = self.create_array()

    def create_array(self):
        """
        Standard class method to produce the list to be used as a column

        :return: List, the column
        """

        if self.int:
            col = np.random.randint(low=self.min_val,
                                    high=self.max_val,
                                    size=self.n_records)
        else:
            col = np.random.rand(self.n_records)
            range = self.max_val - self.min_val
            col = (col*range) + self.min_val

        return col
