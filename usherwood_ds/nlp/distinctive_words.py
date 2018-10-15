#!/usr/bin/env python

"""Finds distinctive word between two corpuses"""

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


class DistinctiveWords:
    """Parent class for finding the distinctive words between two corpuses of text"""

    def __init__(self, raw_text, max_features=10000):
        """

        :param raw_text: A 2 element list with each corpus as a string occupying 1 element
        :param max_features: The maximum number of features to analyse
        """

        self.raw_text = raw_text
        self.keyness = pd.DataFrame(None)

        cv = CountVectorizer(max_features=max_features)
        self.wfm = cv.fit_transform(self.raw_text)
        self.vocab = np.array(cv.get_feature_names())
        self.rates = np.asarray(1000*self.wfm / np.sum(self.wfm, axis=1))

    def unique_words(self, drop_uniques=True):
        """
        Returns a dataframe of the words that are unique to one of the corpuses. It is recommended these are removed
        from subsequent analysis as they are trivial cases that will dominate.

        :param drop_uniques: Boolean, drop the unique words from the wfm and recalculate rates

        :return: Dataframe of the words that are unique to one of the corpuses
        """

        a_rates = np.asarray(self.rates[0])
        b_rates = np.asarray(self.rates[1])

        distinctive_indices = (a_rates*b_rates) == 0

        joint_average_rates = a_rates[distinctive_indices] + b_rates[distinctive_indices]

        ab_distincts = pd.DataFrame(np.array([self.vocab[distinctive_indices], joint_average_rates]).T,
                                    columns=['Vocab', 'Rates']).sort_values(by=['Rates'], ascending=False)

        if drop_uniques:
            self.wfm = self.wfm[:, np.invert(distinctive_indices)]
            self.rates = self.rates[:, np.invert(distinctive_indices)]
            self.vocab = self.vocab[np.invert(distinctive_indices)]

        return ab_distincts

    def basic_rate_differences(self):
        """
        Populates the keyness dataframe with 3 columns:
            - Mean Avergae Rate, the average rate the word appears in both corpuses
            - Average Rate Difference, the difference in the average rates between the two corpuses, a simple measure
            of distinctiveness, however frequent words will dominate
            - Normalized Average Rate Difference The Average Rate Difference / Mean Avergae Rate, this is to normalize
            so that frequent words do not dominate, however now rare words come through more than they should
        """

        a_rates = np.asarray(self.rates[0])
        b_rates = np.asarray(self.rates[1])

        keyness_arr = np.abs(a_rates - b_rates)

        if self.keyness.empty:
            self.keyness = pd.DataFrame(np.array([self.vocab, keyness_arr]).T, columns=['Vocab',
                                                                                        'Average Rate Difference'])

        self.keyness['Mean Average Rate'] = np.mean(self.rates, axis=0)
        self.keyness['Average Rate Difference'] = self.keyness['Average Rate Difference'].astype(float)
        self.keyness['Mean Average Rate'].astype(np.float)
        self.keyness['Normalized Average Rate Difference'] = self.keyness['Average Rate Difference'] /\
            self.keyness['Mean Average Rate']

        return True

    def bayesian_group_comparison(self):
        """
        https://de.dariah.eu/tatom/feature_selection.html

        Populates the keyness dataframe with a column Keyness, this is defined through Bayesian group comparison, where
        we model each words rate in a corpus as a normal distribution, seperated by a half distance that we will use as
        a measure of whether the means are the same or not. We split the means of the distributions into the average
        mean rate, and this half distance, and set priors for these along with the standard deviation. We then use
        Gibbs samplung to estimate the half distance.

        The hyperparameters on the priors are hard coded into this class but can be fined tuned if necessary.
        """

        a_rates = np.asarray(self.rates[0])
        b_rates = np.asarray(self.rates[1])

        keyness_arr = []
        for index, word in enumerate(self.vocab):
            keyness_arr.append(delta_confidence(word, a_rates, b_rates, self.vocab, smax=200, mu0=3, tau20=1.5 ** 2,
                                                nu0=1, sigma20=1, delta0=0, gamma20=1.5 ** 2))

        if self.keyness.empty:
            self.keyness = pd.DataFrame(np.array([self.vocab, keyness_arr]).T, columns=['Vocab', 'Keyness'])
        else:
            self.keyness['Keyness'] = keyness_arr

        return True


def sample_posterior(y1, y2, mu0, sigma20, nu0, delta0, gamma20, tau20, smax):
    """
    Draw samples from posterior distribution using Gibbs sampling

    Parameters
    :param y1: Rate of the word in the first corpus
    :param y2: Rate of the word in the second corpus
    :param mu0: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param sigma20: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param nu0: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param delta0: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param gamma20: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param tau20: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param smax: int - Number of samples

    :return: chains - dict of array. Dictionary has keys: 'mu', 'delta', and 'sigma2'.
    """
    """

     ----------
    `S` is the number of samples
    Returns
    -------
    chains : dict of array
     Dictionary has keys: 'mu', 'delta', and 'sigma2'.
    """
    n1, n2 = len(y1), len(y2)
    mu = (np.mean(y1) + np.mean(y2)) / 2
    delta = (np.mean(y1) - np.mean(y2)) / 2
    bay_vars = ['mu', 'delta', 'sigma2']
    chains = {key: np.empty(smax) for key in bay_vars}
    for s in range(smax):
        a = (nu0 + n1 + n2) / 2
        b = (nu0 * sigma20 + np.sum((y1 - mu - delta) ** 2) + np.sum((y2 - mu + delta) ** 2)) / 2
        sigma2 = 1 / np.random.gamma(a, 1 / b)
        mu_var = 1 / (1 / gamma20 + (n1 + n2) / sigma2)
        mu_mean = mu_var * (mu0 / gamma20 + np.sum(y1 - delta) / sigma2 + np.sum(y2 + delta) / sigma2)
        mu = np.random.normal(mu_mean, np.sqrt(mu_var))
        delta_var = 1 / (1 / tau20 + (n1 + n2) / sigma2)
        delta_mean = delta_var * (delta0 / tau20 + np.sum(y1 - mu) / sigma2 - np.sum(y2 - mu) / sigma2)
        delta = np.random.normal(delta_mean, np.sqrt(delta_var))
        chains['mu'][s] = mu
        chains['delta'][s] = delta
        chains['sigma2'][s] = sigma2

    return chains


def delta_confidence(word, a_rates, b_rates, vocab, smax=200, mu0=3, tau20=1.5 ** 2, nu0=1, sigma20=1, delta0=0,
                     gamma20=1.5 ** 2):
    """
    Calculate the difference in mean rates using Gibbs sampling for a given word.

    :param word: String, the word to sample
    :param a_rates: wfm for the first corpus
    :param b_rates: wfm for the second corpus
    :param vocab: Array of strings, the vocabulary used in the wfm defining a_rates and b_rates
    :param mu0: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param sigma20: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param nu0: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param delta0: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param gamma20: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param tau20: Hyperparameter, see https://de.dariah.eu/tatom/feature_selection.html
    :param smax: int - Number of samples

    :return: The maximum half distance measure, as we only care about distance the positivity is not important
    """

    y1, y2 = a_rates[vocab == word], b_rates[vocab == word]
    chains = sample_posterior(y1, y2, mu0, sigma20, nu0, delta0, gamma20, tau20, smax)
    delta = chains['delta']

    return np.max([np.mean(delta < 0), np.mean(delta > 0)])
