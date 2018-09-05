#!/usr/bin/env python

"""Implements LDA"""

import numpy as np
import pandas as pd
import functools

from sklearn.feature_extraction.text import CountVectorizer
import lda
from gensim.models.ldamulticore import LdaMulticore
from gensim.matutils import Sparse2Corpus


__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


class LDA(object):
    """
    Simple wrapper around the lda module
    """

    def __init__(self, df, snippet_field='Snippet', id_field='Url', max_features=2000):

        self.df_main = df
        self.snippet_field = snippet_field
        self.id_field = id_field

        self.cv = CountVectorizer(max_features=max_features)
        self.wfm = self.cv.fit_transform(self.df_main[self.snippet_field])
        self.vocab = self.cv.get_feature_names()

    def run_model(self, n_topics=20, n_iter=1500, random_state=1, n_top_words=8):

        model = lda.LDA(n_topics=n_topics, n_iter=n_iter, random_state=random_state)
        model.fit(self.wfm)
        topic_word = model.topic_word_
        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(self.vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
            print('Topic {}: {}'.format(i, ' '.join(topic_words)))

        return True

class GensimLDA(object):
    """
    Wrapper around Gensim's lda model
    """

    def __init__(self, df, snippet_field='Snippet', id_field='Url', create_wfm=True, max_features=2000, wfm=None,
                 cv=None):
        """

        :param df: Pandas dataframe containing the text field, id field, and meta variables
        :param snippet_field: The pandas column key for the text field to be used
        :param id_field: The pandas column key for the id field to be used
        :param create_wfm: Whether the GensimLDA should create the wfm or whether one is to be supplied, if GensimLDA
        is to create one it will only do so using bag of words
        :param max_features: If create_wfr = True this is the maximum number of features to be used
        :param wfm: If create_wfr = False this is the supplied wfm
        :param cv: If create_wfr = False this is the supplied cv
        """

        self.topic_word_occurrences = None
        self.document_topic_matrix = None
        self.model = None

        self.df_main = df
        self.snippet_field = snippet_field
        self.id_field = id_field

        if create_wfm:
            self.corpus, self.cv, self.vocab = fit_transform_corpus_from_df(self.df_main,
                                                                        snippet_field=self.snippet_field,
                                                                        max_features = max_features)
        else:
            self.corpus, self.vocab = fit_transform_corpus_from_cv(cv, wfm)
            self.cv = cv


    def run_model(self, n_topics=20, passes=20, workers=2, num_words_per_topic=20):
        """
        Create the LDA model

        :param n_topics: The number of topics to find
        :param passes: The number of passes to run over the corpus
        :param workers: The number of cores to use
        :param num_words_per_topic: The number of words to return per topic (this does not affect calculations, only
        the returned df)
        """

        self.model = LdaMulticore(self.corpus, num_topics=n_topics, id2word=self.vocab, passes=passes, workers=workers)

        topics = self.model.show_topics(num_topics=-1, num_words=num_words_per_topic)
        dfs = []
        for topic in topics:
            constituents = topic[1]
            words = []
            scores = []
            for pair in constituents.split(' + '):
                pair = pair.split('*')
                words.append(pair[1])
                scores.append(float(pair[0]))
            df = pd.DataFrame(np.array([words, scores]).T, columns=['Words', str(topic[0])])
            dfs.append(df)

        self.topic_word_occurrences = functools.reduce(lambda left, right: pd.merge(left, right, how='outer'), dfs)
        self.topic_word_occurrences.fillna(0, inplace=True)
        self.topic_word_occurrences.ix[:, 1:] = self.topic_word_occurrences.ix[:, 1:].astype(float)

        def get_doc_topic(corpus, model):
            doc_topic = list()
            for doc in corpus:
                tuple_list = model.__getitem__(doc, eps=0)
                scores = [float(tuple[1]) for tuple in tuple_list]
                doc_topic.append(scores)
            return doc_topic

        matrix = get_doc_topic(self.corpus, model=self.model)
        self.document_topic_matrix = pd.DataFrame(matrix)

        return True


    def sort_topic_word_occurrences(self, topic_id):

        sub = self.topic_word_occurrences[self.topic_word_occurrences[str(topic_id)] != 0]
        indexes = sub.ix[:, 1:].sum().sort_values(ascending=False).index.tolist()
        sub = sub[['Words'] + indexes]
        sub.sort_values(by=[topic_id], ascending=False, inplace=True)

        return sub


    def find_optimal_params(self, test_df, Kstart=10, Kend=20, Kstep=1, Pstart=10, Pend=11, Pstep=1,
                                        workers=2, num_words_per_topic=20):

        test_corpus = transform_corpus_from_df(test_df, self.snippet_field, self.cv)

        bound_scores = []
        perp_scores = []
        for k in np.arange(Kstart, Kend, Kstep):
            bound_cluster_scores = []
            perp_cluster_scores =[]
            for p in np.arange(Pstart, Pend, Pstep):
                print(k)
                print(p)
                self.run_model(n_topics=k, passes=p, workers=workers, num_words_per_topic=num_words_per_topic)
                bound_cluster_scores.append(self.model.bound(test_corpus))
                perp_cluster_scores.append(self.model.log_perplexity(test_corpus))
            bound_scores.append(bound_cluster_scores)
            perp_scores.append(perp_cluster_scores)

        return bound_scores, perp_scores


def fit_transform_corpus_from_df(df, snippet_field, max_features):

    cv = CountVectorizer(max_features=max_features)
    wfm = cv.fit_transform(df[snippet_field])
    vocab = {y: x for x, y in cv.vocabulary_.items()}
    corpus = Sparse2Corpus(wfm.T)

    return corpus, cv, vocab


def fit_transform_corpus_from_cv(cv, wfm):

    vocab = {y: x for x, y in cv.vocabulary_.items()}
    corpus = Sparse2Corpus(wfm.T)

    return corpus, vocab


def transform_corpus_from_df(df, snippet_field, cv):

    wfm = cv.transform(df[snippet_field])
    corpus = Sparse2Corpus(wfm.T)

    return corpus
