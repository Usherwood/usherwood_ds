#!/usr/bin/env python

"""Root functions for producing the time series plots and analysis"""

import numpy as np
import pandas as pd
import collections
from itertools import count

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


def day_of_week_and_hour_cross(df, dependent_variable):

    if dependent_variable == 'Volume':
        cross = pd.get_dummies(df['when: Day of Week']).T.dot(pd.get_dummies(df['when: Hour of Day']))
    else:
        cross = (pd.get_dummies(df['when: Day of Week']).multiply(df[dependent_variable], axis="index")).T.\
            dot(pd.get_dummies(df['when: Hour of Day']).multiply(df[dependent_variable], axis="index"))

    for i in list(set(range(24)) - set(cross.columns)):
        cross.insert(1, i, np.zeros(len(cross)))
    for i in list(set(range(7)) - set(cross.index)):
        cross = cross.append(pd.DataFrame([np.zeros(len(cross.columns)).tolist()], columns=cross.columns, index=[i]))
    cross = cross.sort_index(1)
    cross = cross.sort_index(0)

    cross.index = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    return cross


def create_cat_summary_table(df,
                             year_list,
                             cat,
                             sentiment_column_key='Sentiment',
                             reach_column_key='Reach',
                             categorical_sentiment=True):

    if categorical_sentiment:
        sent_cols = []
        cat_sentiments = []
        sents = pd.get_dummies(df[sentiment_column_key])
        for col in sents.columns:
            sents.rename(columns={col:'Sentiment ' + str(col)}, inplace=True)
            sent_cols += ['Sentiment ' + str(col)]
            cat_sentiments.append([])
        df = pd.concat([df, sents], axis=1)

    volumes = []
    sentiments = []
    reach = []
    weeks = []
    years = []
    combi_id = []

    if sentiment_column_key not in df.columns:
        df[sentiment_column_key] = 0
    if reach_column_key not in df.columns:
        df[reach_column_key] = 0

    for year in year_list:
        for week in range(0, 53):
            sub = df[(df['when: Year'] == year) & (df['when: Week'] == week) & (df[cat] == 1)]

            if week == 0 and year != year_list[0]:
                volumes[len(volumes) - 1] += len(sub)
                sentiments[len(sentiments) - 1] += sub[sentiment_column_key].sum()
                reach[len(reach) - 1] += sub[reach_column_key].sum()
            else:
                volumes.append(len(sub))
                reach.append(sub[reach_column_key].sum())
                sentiments.append(sub[sentiment_column_key].sum())

                if categorical_sentiment:
                    for i, col in enumerate(sent_cols):
                        cat_sentiments[i].append(sub[col].sum())

                weeks += [week]
                years += [year]
                combi_id += [int(str(year) + str(week))]

    summary = pd.DataFrame(np.array([combi_id, years, weeks, volumes, sentiments, reach]).T,
                           columns=['ID', 'Year', 'Week', 'Volume', 'Sentiment', 'Reach'])

    if categorical_sentiment:
        cat_sents_df = pd.DataFrame(np.array(cat_sentiments).T, columns=sent_cols)

    summary = pd.concat([summary, cat_sents_df], axis=1)

    summary['Week Cumm'] = np.arange(len(summary))
    return summary


def moving_average(data, window_size):
    """
    Computes moving average using discrete linear convolution of two one dimensional sequences.

    :param data: pandas.Series, volumes over time
    :param window_size: Int, rolling window size

    :returns: ndarray of linear convolution
    """

    window = np.ones(int(window_size)) / float(window_size)
    rolling_avg = np.convolve(data, window, 'same')
    return rolling_avg


def explain_anomalies(y, window_size, sigma=1.0):
    """
    Helps in exploring the anamolies using stationary standard deviation

    :param y: pandas.Series, volumes over time
    :param window_size: Int, rolling window size
    :param sigma: Int, digma confidence levelvalue for standard deviation

    :returns:
        a dict (dict of 'standard_deviation': int, 'anomalies_dict': (index: value))
        containing information about the points indentified as anomalies
    """

    avg = moving_average(y, window_size).tolist()
    residual = y - avg
    std = np.std(residual)

    anomalies_dict = collections.OrderedDict([(index, y_i) for
                                              index, y_i, avg_i in zip(count(), y, avg)
                                              if (y_i > avg_i + (sigma * std)) | (y_i < avg_i - (sigma * std))])

    master_dict = {'standard_deviation': round(std, 3),
                   'anomalies_dict': anomalies_dict}
    return master_dict


def explain_anomalies_rolling_std(y, window_size, sigma=1.0):
    """ Helps in exploring the anamolies using rolling standard deviation
    Args:
    -----
        y (pandas.Series): independent variable
        window_size (int): rolling window size
        sigma (int): value for standard deviation

    Returns:
    --------
        a dict (dict of 'standard_deviation': int, 'anomalies_dict': (index: value))
        containing information about the points indentified as anomalies
    """
    avg = moving_average(y, window_size)
    avg_list = avg.tolist()
    residual = y - avg
    # Calculate the variation in the distribution of the residual
    testing_std = pd.rolling_std(residual, window_size)
    testing_std_as_df = pd.DataFrame(testing_std)
    rolling_std = testing_std_as_df.replace(np.nan,
                                            testing_std_as_df.ix[window_size - 1]).round(3).iloc[:, 0].tolist()
    std = np.std(residual)
    return {'stationary standard_deviation': round(std, 3),
            'anomalies_dict': collections.OrderedDict([(index, y_i)
                                                       for index, y_i, avg_i, rs_i in zip(count(),
                                                                                          y, avg_list, rolling_std)
                                                       if (y_i > avg_i + (sigma * rs_i)) | (
                                                       y_i < avg_i - (sigma * rs_i))])}


def plot_anomalies_and_ts(x,
                          y,
                          window_size,
                          ax,
                          sigma_value=1,
                          text_xlabel="X Axis",
                          text_ylabel="Y Axis",
                          text_title='Title',
                          applying_rolling_std=False):
    """
    Helps in generating the plot and flagging the anamolies.
    Supports both moving and stationary standard deviation. Use the 'applying_rolling_std' to switch
    between the two.

    :param x: pandas.Series, time series
    :param y: pandas.Series, dependent variable
    :param window_size: Int, rolling window size
    :param sigma_value: Int, value for standard deviation
    :param text_xlabel: Str, label for annotating the X Axis
    :param text_ylabel: Str, label for annotatin the Y Axis
    :param text_title: Str, label for the title
    :param applying_rolling_std: Bool, for using rolling vs stationary standard deviation
    """

    ax.plot(x, y, "k.")
    y_av = moving_average(y, window_size)
    ax.plot(x, y_av, color='green')
    ax.set_xlabel(text_xlabel)
    ax.set_ylabel(text_ylabel)
    ax.set_title(text_title)

    # Query for the anomalies and plot the same
    events = {}
    if applying_rolling_std:
        events = explain_anomalies_rolling_std(y, window_size=window_size, sigma=sigma_value)
    else:
        events = explain_anomalies(y, window_size=window_size, sigma=sigma_value)

    x_anomaly = np.fromiter(events['anomalies_dict'].keys(), dtype=int, count=len(events['anomalies_dict']))
    y_anomaly = np.fromiter(events['anomalies_dict'].values(), dtype=float,
                            count=len(events['anomalies_dict']))
    ax.plot(x_anomaly, y_anomaly, "r*", markersize=12)

    return ax


def get_top_snippets_and_authors_per_anomoly_for_cat(cat,
                                                     summaries,
                                                     df,
                                                     snippet_key_field='Snippet'):

    weeks = summaries[cat][summaries[cat]['Anomaly'] == True]['Week'].tolist()
    years = summaries[cat][summaries[cat]['Anomaly'] == True]['Year'].tolist()

    top_snippets = []
    top_authors = []

    for i in range(len(weeks)):

        week = weeks[i]
        year = years[i]

        if week == 52:
            sub = df[(df['when: Year'] == year) & (df['when: Week'] == week) & (df[cat] == 1)]
            sub.append(df[(df['when: Year'] == year + 1) & (df['when: Week'] == 0) & (df[cat] == 1)])
        else:
            sub = df[(df['when: Year'] == year) & (df['when: Week'] == week) & (df[cat] == 1)]

        top_snippets.append(sub[snippet_key_field].value_counts()[:20])
        top_authors.append(sub['Username'].value_counts()[:20])

    return top_snippets, top_authors, weeks, years


def create_excel_for_one_cat(writer,
                             dependent_variable,
                             anomaly_snippets,
                             anomaly_authors,
                             weeks,
                             years):

    for i in range(len(anomaly_snippets)):
        pd.DataFrame(np.array([anomaly_snippets[i].index, anomaly_snippets[i].values]).T,
                     columns=['Top Snippets', 'Count']).to_excel(writer, dependent_variable + ' ' + str(i) + ". Date- "
                                                                 + str(years[i]) + "-" + str(weeks[i]), startcol=0)
        pd.DataFrame(np.array([anomaly_authors[i].index, anomaly_authors[i].values]).T,
                     columns=['Top Authors', 'Count']).to_excel(writer, dependent_variable + ' ' + str(i) + ". Date- "
                                                                + str(years[i]) + "-" + str(weeks[i]), startcol=3)
    return True
