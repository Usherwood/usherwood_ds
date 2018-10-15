#!/usr/bin/env python

"""Convert a gmt time column in a pandas dataframe to a local time specified by a secondary column."""

from dateutil import tz
import progressbar

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def df_convert_gmt_to_local(df, gmt_col='Date (GMT)', zone_col='Date (Local - Zone)', output_col='Date (Local)'):
    """
    Convert a gmt time to a local time using a specified zone, all in a pandas df

    :param df: Pandas dataframe
    :param gmt_col: Str, column name of column containing gmt
    :param zone_col: Str, column name of column containing the zone
    :param output_col: Str, name of output column
    """

    with progressbar.ProgressBar(max_value=len(df)) as bar:
        for i in range(len(df)):

            gmt_time = df[gmt_col].iloc[i]
            #print(type(gmt_time))
            zone = df[zone_col].iloc[i]

            if gmt_time is not None:
                if (zone is None) or (zone == 'nan'):
                    df.set_value(index=i, col=output_col, value=gmt_time)
                else:
                    try:
                        to_zone = tz.gettz(zone)
                        original_time = gmt_time.replace(tzinfo=tz.gettz('UTC'))
                        local = original_time.astimezone(to_zone)
                        df[output_col] = local
                    except Exception as e:
                        print(zone)
                        print(gmt_time)
            bar.update(i)
