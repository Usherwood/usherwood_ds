#!/usr/bin/env python

"""Functions for transforming encoded taxonomy files into a bycat taxonomy df"""

import pandas as pd
import csv

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def domains_to_binary(df_encoded, domain_column_key='Domain', num_domains=10):
    """
    Transform the domains column into binary to be used as a cross-sectional category

    :param df_encoded: Standard encoded matrix file
    :param domain_column_key: String, the name of the current domain column
    :param num_domains: Int, the number of domains to use (will take top x)

    :return: df_encoded with the additional domain columns prefixed c_ for cross-sectional
    """

    domains_df = pd.get_dummies(df_encoded[domain_column_key], prefix='c_')
    domains_df = domains_df.ix[:,:num_domains]

    df_encoded = pd.concat([df_encoded,domains_df], axis=1)

    return df_encoded


def encoded_to_bycat_counts(df_encoded, tax_col_indicator='e_', cross_col_indicator='c_'):
    """
    Transform a standard encoded file into a bycat (by category) file

    :param df_encoded: Standard encoded matrix file, can have additional columns that will be discarded
    :param tax_col_indicator: String, the pattern that starts all categories in the taxonomy
    :param cross_col_indicator: String, the pattern that starts all cross-sectional categories

    :return: bycat_counts df with the taxonomy as rows and counts of the cross sectional variables as columns
    """

    tax_cols = list(df_encoded.columns[pd.Series(df_encoded.columns).str.startswith(tax_col_indicator)])
    cross_cols = list(df_encoded.columns[pd.Series(df_encoded.columns).str.startswith(cross_col_indicator)])

    df_encoded = df_encoded[tax_cols+cross_cols]

    counts = df_encoded[tax_cols].sum().values

    cooc_full = df_encoded.T.dot(df_encoded)

    bycat_counts = cooc_full.ix[tax_cols,cross_cols]
    bycat_counts.insert(0, 'Volume', value=counts)

    return bycat_counts
