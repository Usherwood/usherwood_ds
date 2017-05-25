#!/usr/bin/env python

"""Functions for transforming encoded taxonomy files into a bycat taxonomy df"""

import pandas as pd
import numpy as np

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

    top_domains = df_encoded[domain_column_key].value_counts()[:num_domains].index.tolist()
    top_domains = ['c_'+domain for domain in top_domains]
    domains_df = pd.get_dummies(df_encoded[domain_column_key], prefix='c')
    domains_df = domains_df[top_domains]

    df_encoded = pd.concat([df_encoded,domains_df], axis=1)

    return df_encoded


def date_to_binary_tod(pd_datetime, lower_hour=0, lower_minute=0, upper_hour=23, upper_minute=59):
    """
    Turn a pandas datetime value into a binary variable, good if "applied" to pandas column

    :param pd_datetime: pandas datetime variable
    :param lower_hour: Int, lower hour, 0-23
    :param lower_minute: Int, lower minute, 0-59
    :param upper_hour: Int, upper hour, 0-23
    :param upper_minute: Int, upper minute, 0-59

    :return: valid 1 or 0 to be assigned to a binary column
    """
    
    current_hour = pd_datetime.hour
    current_minute = pd_datetime.minute

    valid = 0
    if current_hour >= lower_hour:
        if current_minute >= lower_minute:
            if current_hour <= upper_hour:
                if current_minute <= upper_minute:
                    valid = 1
    return valid


def encoded_to_bycat_counts(df_encoded, tax_col_indicator='e_', cross_col_indicator='c_', prediction=True):
    """
    Transform a standard encoded file into a bycat (by category) file

    :param df_encoded: Standard encoded matrix file, can have additional columns that will be discarded
    :param tax_col_indicator: String, the pattern that starts all categories in the taxonomy
    :param cross_col_indicator: String, the pattern that starts all cross-sectional categories
    :param prediction: Bool, if True adds dVolumedt and dSentimentdt values

    :return: bycat_counts df with the taxonomy as rows and counts of the cross sectional variables as columns
    """

    df_encoded.fillna(0, inplace=True)

    tax_cols = list(df_encoded.columns[pd.Series(df_encoded.columns).str.startswith(tax_col_indicator)])
    cross_cols = list(df_encoded.columns[pd.Series(df_encoded.columns).str.startswith(cross_col_indicator)])

    df_cross = df_encoded[tax_cols+cross_cols]

    counts = df_cross[tax_cols].sum().values

    cooc_full = df_cross.T.dot(df_cross)

    bycat_counts = cooc_full.ix[tax_cols,cross_cols]
    bycat_counts.insert(0, 'Volume', value=counts)

    if prediction:
        df_encoded.index = pd.to_datetime(df_encoded['Date'])
        df_encoded['Volume'] = 1

        dvolumedts = []
        dsentimentdts = []
        for tax in tax_cols:
            sub = df_encoded[df_encoded[tax] == 1].ix[:, ['Date', 'Volume', cross_col_indicator+'Sentiment']]

            sent = sub.resample('W').mean()[cross_col_indicator+'Sentiment']\
                .fillna(sub.resample('W').mean()[cross_col_indicator+'Sentiment'].mean())

            volume = sub.resample('W').sum()['Volume'].fillna(sub.resample('W').sum()['Volume'].mean())

            x = np.arange(len(volume))

            if len(x) <= 1:
                mv, ms = 0, 0
            else:
                mv, cv = np.polyfit(x=x, y=volume, deg=1)
                ms, cs = np.polyfit(x=x, y=sent, deg=1)

            dvolumedts.append(mv)
            dsentimentdts.append(ms)

        bycat_counts.insert(1, 'dVolume dt', value=dvolumedts)
        bycat_counts.insert(1, 'dSentiment dt', value=dsentimentdts)

    return bycat_counts


def bycat_counts_to_bycat_scores(bycat_counts, cross_lists):
    """
    Transform a bycat_counts df into a bycat_scores df which gives an index based on sub cross-category groups and
    volumes

    :param bycat_counts: bycat_counts df
    :param cross_lists: A list of lists, where each list is a group of common column names (e.g. brands, moments)

    :return: bycat_scores
    """

    bycat_scores = bycat_counts.ix[:,list(set(bycat_counts.columns.values.tolist())-
                                          set([l for sub in cross_lists for l in sub]))]

    for cross in cross_lists:
        M = bycat_counts.ix[:,cross]
        sumjM = M.sum(axis=0).values
        sumiM = M.sum(axis=1).values
        sumijM = M.sum().sum()
        cross_scores = M - np.outer(sumjM,sumiM).T/sumijM
        bycat_scores = pd.concat([bycat_scores,cross_scores], axis=1)

    return bycat_scores
