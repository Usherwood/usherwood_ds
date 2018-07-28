#!/usr/bin/env python

"""Standard text cleaning for pandas, used by many other functions, for more granularity use the composite
functions separately"""

from main.nlp.processing.stopwords import stopword_removal
from main.nlp.preprocessing.cleaning import clean_text
from main.nlp.preprocessing.stemming import Stemmer
from main.nlp.preprocessing.social_feature_extraction import extract_hashtags, \
    extract_mentioned_users, extract_urls

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


def preprocess_df(data,
                  text_field_key ='Snippet',
                  language='english',
                  additional_list=[],
                  adhoc_stopwords=[],
                  remove_hashtag_words=False,
                  remove_mentioned_authors=True,
                  remove_urls=True,
                  stopped_not_stemmed=False,
                  pos_tuples=False):
    """
    Basic wrapper for cleaning text data in a pandas dataframe column

    :param data: Pandas dataframe
    :param text_field_key: The field name of the text to be cleaned
    :param language: Primary language (see stopwords/stemming)
    :param additional_list: List of additional pre set stopwords (see stopwords)
    :param adhoc_stopwords: List of adhoc stopwords (see stopwords)
    :param remove_hashtag_words: Bool, remove the words that appear as hashtags
    :param remove_mentioned_authors: Bool, remove the at mentioned authors
    :param remove_urls: Bool, remove urls
    :param stopped_not_stemmed: Return a field of cleaned and stopword removed text, useful for the categorizer
    :param pos_tuples: Bool, if tokens are a list of pos_tuples set this to true

    :return: data with additional text/pos_tuple columns showing the cleaning process
    """
    stemmer = Stemmer(language=language)

    if not pos_tuples:
        data['Cleaned'] = data.ix[:, text_field_key]
        print('Loaded')

        if remove_hashtag_words:
            data['Cleaned'] = data.ix[:, 'Cleaned'].apply(lambda e: extract_hashtags(text_string=e,
                                                                                     remove_hashtags=True)[0])
        if remove_mentioned_authors:
            data['Cleaned'] = data.ix[:, 'Cleaned'].apply(lambda e: extract_mentioned_users(text_string=e,
                                                                                            remove_users=True)[0])
        if remove_urls:
            print('url remover not built')
            remove_urls=False

        data['Hashtags'] = data.ix[:, 'Cleaned'].apply(lambda e: extract_hashtags(text_string=e,
                                                                                 remove_hashtags=False)[1])
        data['At Mentions'] = data.ix[:, 'Cleaned'].apply(lambda e: extract_mentioned_users(text_string=e,
                                                                                        remove_users=False)[1])

        print('Removed social features. Hashtags:', str(remove_hashtag_words),
              'At Mentions:', str(remove_mentioned_authors),
              'URLs:', str(remove_urls))

        data['Cleaned'] = data.ix[:, 'Cleaned'].apply(lambda e: clean_text(text_string=e))
        print('Cleaned Text')

        data['Stemmed'] = data.ix[:, 'Cleaned'].apply(lambda e: stemmer.stem_text(text_string=e))
        print('Stemmed Text')

        data['Preprocessed'] = data.ix[:, 'Stemmed'].apply(lambda e: stopword_removal(text_string=e,
                                                                                      language=language,
                                                                                      additional_language_list=
                                                                                      additional_list,
                                                                                      adhoc_list=adhoc_stopwords))
        print('Removed Stopwords')

        if stopped_not_stemmed:
            data['Stopped'] = data.ix[:, 'Cleaned'].apply(lambda e: stopword_removal(text_string=e,
                                                                                     language=language,
                                                                                     additional_language_list=
                                                                                     additional_list,
                                                                                     adhoc_list=adhoc_stopwords))
            print('Stopped not Stemmed')
    else:
        print('Loaded')

        data['Cleaned'] = data.ix[:, text_field_key].apply(lambda e: clean_text(tokens=e, pos_tuples=True))
        print('Cleaned Text')

        data['Stemmed'] = data.ix[:, 'Cleaned'].apply(lambda e: stemmer.stem_text(tokens=e,
                                                                                  pos_tuples=True))
        print('Stemmed Text')

        data['Preprocessed'] = data.ix[:, 'Stemmed'].apply(lambda e: stopword_removal(tokens=e,
                                                                                      pos_tuples=True,
                                                                                      language=language,
                                                                                      additional_language_list=
                                                                                      additional_list,
                                                                                      adhoc_list=adhoc_stopwords))
        print('Removed Stopwords')

        if stopped_not_stemmed:
            data['Stopped'] = data.ix[:, 'Cleaned'].apply(lambda e: stopword_removal(tokens=e,
                                                                                     pos_tuples=True,
                                                                                     language=language,
                                                                                     additional_language_list=
                                                                                     additional_list,
                                                                                     adhoc_list=adhoc_stopwords))
    return data


def preprocess_string(text_string=None,
                      tokens=None,
                      pos_tuples=False,
                      language='english',
                      additional_list = [],
                      adhoc_stopwords = []):
    """
    Function that carries out all standard preprocessing on a tring or list of tokens (normal or pos)

    :param text_string: text string to be preprocessed (only give one of this and tokens)
    :param tokens: list of tokens (normal or pos) to be preprocessed (only give one of this and text_string)
    :param language: Primary language (see stopwords/stemming)
    :param additional_list: List of additional pre set stopwords (see stopwords)
    :param adhoc_stopwords: List of adhoc stopwords (see stopwords)

    :return: preprocessed text in either string or list depending on (and matching) input
    """

    stemmer = Stemmer(language=language)

    if text_string:
        text = clean_text(text_string=text_string)
        text = stemmer.stem_text(text_string=text, language=language)
        text = stopword_removal(text_string=text,
                                language=language,
                                additional_list=additional_list,
                                adhoc_stopwords=adhoc_stopwords)
        preped = text
    else:
        tokens = clean_text(tokens=tokens, pos_tuples=pos_tuples)
        tokens = stemmer.stem_text(tokens=tokens, pos_tuples=pos_tuples, language=language)
        tokens = stopword_removal(tokens=tokens,
                                  pos_tuples=pos_tuples,
                                  language=language,
                                  additional_list=additional_list,
                                  adhoc_stopwords=adhoc_stopwords)

        preped = tokens

    return preped
