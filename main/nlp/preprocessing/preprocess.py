#!/usr/bin/env python

"""Standard text cleaning for pandas, used by many other functions, for more granularity use the composite
functions separately"""

from main.nlp.processing.stopwords import stopword_removal
from main.nlp.preprocessing.cleaning import clean_text
from main.nlp.preprocessing.stemming import stem_text

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


def preprocess_df(data,
                  text_field_key ='Snippet',
                  language='english',
                  additional_list=[],
                  adhoc_stopwords=[],
                  stopped_not_stemmed=False,
                  pos_tuples=False):
    """
    Basic wrapper for cleaning text data in a pandas dataframe column

    :param data: Pandas dataframe
    :param text_field_key: The field name of the text to be cleaned
    :param language: Primary language (see stopwords/stemming)
    :param additional_list: List of additional pre set stopwords (see stopwords)
    :param adhoc_stopwords: List of adhoc stopwords (see stopwords)
    :param stopped_not_stemmed: Return a field of cleaned and stopword removed text, useful for the categorizer
    :param pos_tuples: Bool, if tokens are a list of pos_tuples set this to true

    :return: data with additional text/pos_tuple columns showing the cleaning process
    """

    if not pos_tuples:
        data['Original'] = data.ix[:, text_field_key]
        print('Loaded')
        data['Cleaned'] = data.ix[:, text_field_key].apply(lambda e: clean_text(text_string=e))
        print('Cleaned Text')
        data['Stemmed'] = data.ix[:, 'Cleaned'].apply(lambda e: stem_text(text_string=e, language=language))
        print('Stemmed Text')
        data[text_field_key] = data.ix[:, 'Stemmed'].apply(lambda e: stopword_removal(text_string=e,
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
        data['Original'] = data.ix[:, text_field_key]
        print('Loaded')
        data['Cleaned'] = data.ix[:, text_field_key].apply(lambda e: clean_text(tokens=e, pos_tuples=True))
        print('Cleaned Text')
        data['Stemmed'] = data.ix[:, 'Cleaned'].apply(lambda e: stem_text(tokens=e, language=language, pos_tuples=True))
        print('Stemmed Text')
        data[text_field_key] = data.ix[:, 'Stemmed'].apply(lambda e: stopword_removal(tokens=e,
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

    if text_string:
        text = clean_text(text_string=text_string)
        text = stem_text(text_string=text, language=language)
        text = stopword_removal(text_string=text,
                                language=language,
                                additional_list=additional_list,
                                adhoc_stopwords=adhoc_stopwords)
        preped = text
    else:
        tokens = clean_text(tokens=tokens, pos_tuples=pos_tuples)
        tokens = stem_text(tokens=tokens, pos_tuples=pos_tuples, language=language)
        tokens = stopword_removal(tokens=tokens,
                                  pos_tuples=pos_tuples,
                                  language=language,
                                  additional_list=additional_list,
                                  adhoc_stopwords=adhoc_stopwords)

        preped = tokens

    return preped
