#!/usr/bin/env python

"""The date column class of the dataframe creator, create datetime distributions"""


import random
import time
import numpy as np
import warnings

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


class Date:
    """
    Produce a column of random datetimes in a range.
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
        self.start_date = args.pop('start_date', "01/09/2016 00:00:00")
        self.end_date = args.pop('end_date', "01/09/2017 00:00:00")

        if len(args.keys()) > 0:
            for key in args.keys():
                warnings.warn('Unused key:'+str(key))

        self.col = self.create_array()

    def create_array(self):
        """
        Standard class method to produce the list to be used as a column

        :return: List, the column
        """

        array = np.ones(self.n_records)
        col = [random_date(self.start_date, self.end_date, random.random()) for x in array]

        return col


def str_time_prop(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.
    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.

    :param start: String, start time
    :param end: String, end time
    :param format: String, (strftime-style)
    :param prop: Func, method of selection of the random number

    :return: String object
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def random_date(start, end, prop):

    return str_time_prop(start, end, '%d/%m/%Y %H:%M:%S', prop)
