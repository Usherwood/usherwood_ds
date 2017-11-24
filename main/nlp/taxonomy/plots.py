#!/usr/bin/env python

"""Functions for plotting taxonomy categories"""

import seaborn as sns
import numpy as np

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def opportunities(ax, category_names, volumes, opportunity_scores, tertiary=None, labels=False, labels_min_vol=50,
                  opportunity_name='Sentiment', colour_scale=.5, font_size=7, x_lims=None, y_lims=None,
                  colour=None, bubble_scale=1):
    """
    To plot opportunities for categories made through a taxonomy

    :param ax: Matplotlib axis
    :param category_names: Series - Names of the categories
    :param volumes: Series - Volumes
    :param opportunity_scores: Series - Opportunity scores
    :param tertiary: Series - Any 3rd variable to plot, it will be represented through colour
    :param labels: Whether to plot labels
    :param labels_min_vol: Integer, minimum volume value to plot labels for
    :param opportunity_name: String name for the type of function defining opportunities
    :param colour_scale: Int, power to raise the tertiary values for to get better distinctions
    :param font_size: Matplotlib font size for labels
    :param x_lims: List of 2 integers, the min and max values for the x-axis
    :param y_lims: List of 2 integers, the min and max values for the y-axis
    :param colour: List of 3 floats representing the rgb colour of the markers
    :param bubble_scale: Float, scale the size of the bubbles

    :return ax1: Matplotlib axis
    """

    sns.set_style("white")

    if not colour:
        colour = [140/255, 200/255, 219/255]
    if not x_lims:
        x_lims = [0, 500]
    if not y_lims:
        y_lims = [-10, 40]

    if labels:
        for x, y, s in zip(volumes, opportunity_scores, category_names):
            if x < labels_min_vol:
                pass
            else:
                ax.text(x, y, s, size=font_size, color='k')# + np.random.standard_normal(1)*.05

    if tertiary is None:
        ax.scatter(volumes, opportunity_scores, s=volumes*bubble_scale, c=colour, lw=0)
    else:
        green = np.zeros((len(volumes), 4))
        green[:, 0] = 30 / 255
        green[:, 1] = 150 / 255
        green[:, 2] = 50 / 255
        green[:, 3] = pow(tertiary, colour_scale) / max(pow(tertiary, colour_scale))
        ax.scatter(volumes*bubble_scale, opportunity_scores, s=volumes, c=green, lw=0)

    ax.set_xlabel('Mentions')
    ax.set_ylabel(opportunity_name)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_xlim(x_lims)
    ax.set_ylim(y_lims)

    return ax
