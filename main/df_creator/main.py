#!/usr/bin/env python

"""Creates a fully customizable dummy pandas dataframe to test solution on. The dataframe is a collection of column
classes, if there is a datatype you would like to include, please add a new class"""

import pandas as pd
import numpy as np
from main.df_creator.columns import *

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def DF(column_list=None, n_records=50):
    """
    Main function to import, it creates the dummy pandas dataframe

    :param column_list: a list of dictionaries, each dictionary requires the following elements:
        type: a string refering to a class name (see below for available classes)
        name: a unique name to id the column
        n_itters: integer dictating how many versions of this column you want (named name1, name2 etc)
        args: dictionary of class specific arguments to fine tune the column type
    :param n_records: number of records to be generated

    :return: pandas df
    """

    if not column_list:
        column_list = [{'type': 'Number', 'name': 'Test N', 'n_itters': 1, 'args': {}}]

    column_outputs = []
    for col_set in column_list:
        ctype = col_set['type']
        for i in range(col_set['n_itters']):

            if col_set['n_itters'] == 1:
                name = col_set['name']
            else:
                name = col_set['name'] + str(i)

            class_name = globals()[ctype]
            column_i = class_name(name, n_records, col_set['args'])
            column_outputs.append(column_i)

    headers = []
    data = []
    for column in column_outputs:
        headers.append(column.name)
        data.append(column.col)

    df = pd.DataFrame(np.array(data).T, columns=headers)
    return df

# To make a new class ensure it has a unuique name, ensure it accepts the following arguments (name, n_records, args)
# and be sure it has .name and .col properties. .name is a string refering to the unique name as supplied to the class
# init, and .col shoul be an n_records long numpy array of the values to be in the column