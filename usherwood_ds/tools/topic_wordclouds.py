#!/usr/bin/env python

"""Creating wordclouds for pandas series of text records"""

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


class Visualizer:
    """
    Creates a class to wrap around WordCloud
    """

    def __init__(self):

        self.textstring = None
        self.word_frequency = None
        self.wordcloud_obj = None
        self.image = None

    def wordcloud_from_series(self, series, stopwords=[], bg_colour='white', width=1200, height=1000):
        """
        Generates the wordcloud from a series of text.

        :param series: Pandas series of text records to become a wordcloud
        :param stopwords: Set of stopwords to remove, use utils>preprocessing>stopwords>create_stopwords_set
        :param bg_colour: Background colour background colour
        :param width: Int pixel width of image
        :param height: Int pixel height of image

        :return: Wordcloud image
        """

        self.textstring = " ".join(series.tolist())

        wordcloud = WordCloud(stopwords=stopwords,
                              background_color=bg_colour,
                              width=width,
                              height=height
                              ).generate(self.textstring)

        self.wordcloud_obj = wordcloud
        self.word_frequency = pd.DataFrame({'Word': list(self.wordcloud_obj.words_.keys()),
                                            'Score': list(self.wordcloud_obj.words_.values())})

        plt.imshow(wordcloud)
        plt.axis('off')
        plt.show()

        self.image = wordcloud

        return True

    def wordcloud_from_frequencies(self, frequencies, stopwords=[], bg_colour='white', width=1200, height=1000):
        """
        Generates the wordcloud from a series of text.

        :param frequencies: A pandas df of words to frequencies, columns Word and Score
        :param stopwords: Set of stopwords to remove, use utils>preprocessing>stopwords>create_stopwords_set
        :param bg_colour: Background colour background colour
        :param width: Int pixel width of image
        :param height: Int pixel height of image

        :return: Wordcloud image
        """

        self.word_frequency = frequencies

        wordcloud = WordCloud(stopwords=stopwords,
                              background_color=bg_colour,
                              width=width,
                              height=height
                              ).generate(self.textstring)

        self.wordcloud_obj = wordcloud

        plt.imshow(wordcloud)
        plt.axis('off')
        plt.show()

        return True


