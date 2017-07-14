#!/usr/bin/env python

"""Functions designed to help n_grams>main run but shouldnt ever need to be called directly by the user."""

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def generate_ngrams(data,
                    min_gram,
                    max_gram,
                    text_field_key='Snippet',
                    max_features=1000,
                    tfidf=True,
                    pos_tuples=False):
    """
    The main code for generating the ngrams used by the primary class

    :param data: The main pandas dataframe
    :param min_gram: Int, The minimum n
    :param max_gram: Int, The maximim n
    :param text_field_key: The name of the text field (by default Snippet)
    :param max_features: Int the maximum number of features to generate
    :param tfidf: Bool, whether to use the rate countvectorizer instead of the deafult counts one
    :param pos_tuples: Bool, if text_key_field is a list of pos_tuples set this to true
    :return:
    """

    if pos_tuples:
        _pos_ngrams = create_pos_ngrams(min_gram, max_gram)

        def my_analyzer(tokens):
            """
            Custom analyser for the countvectorizer when using pos tuples

            :param tokens: List of pos tuples (one record at a time)

            :return: List of ngram tokens
            """
            tokens = [str(tup) for tup in tokens]
            return _pos_ngrams(tokens)

        text = data[text_field_key].values.tolist()
        if tfidf:
            cv = TfidfVectorizer(max_features=50, preprocessor=None, analyzer=my_analyzer)
        else:
            cv = CountVectorizer(max_features=50, preprocessor=None, analyzer=my_analyzer)
        word_frequency_matrix = cv.fit_transform(raw_documents=text)
    else:
        text = data[text_field_key]

        if tfidf:
            cv = TfidfVectorizer(ngram_range=(min_gram, max_gram), max_features=max_features)
        else:
            cv = CountVectorizer(ngram_range=(min_gram, max_gram), max_features=max_features)
        word_frequency_matrix = cv.fit_transform(raw_documents=text.values.astype('U'))

    print(word_frequency_matrix.shape)

    freqs = [(word, word_frequency_matrix.getcol(idx).sum(), idx) for word, idx in cv.vocabulary_.items()]
    ngrams = pd.DataFrame(freqs, columns=['Ngram','Frequency','Index'])
    ngrams.sort_values(by=['Frequency'], ascending=False, inplace=True)
    ngrams.reset_index(drop=True, inplace=True)
    return ngrams, word_frequency_matrix, cv


def create_pos_ngrams(min_gram, max_gram):
    """
    Create the custom ngram creator used with the custom analyser for pos tuples

    :param min_gram: Int, min gram
    :param max_gram: Int, max gram

    :return: Custom ngram creator used with the custom analyser for pos tuples
    """

    def _pos_ngrams(tokens):
        """
        Custom ngram creator used with the custom analyser for pos tuples

        :param tokens: List of pos tuples

        :return: List of ngram tokens
        """
        min_n, max_n = min_gram, max_gram
        if max_n != 1:
            original_tokens = tokens
            tokens = []
            n_original_tokens = len(original_tokens)
            for n in range(min_n,min(max_n + 1, n_original_tokens + 1)):
                for i in range(n_original_tokens - n + 1):
                    tokens.append(" ".join(original_tokens[i: i + n]))

        return tokens

    return _pos_ngrams
