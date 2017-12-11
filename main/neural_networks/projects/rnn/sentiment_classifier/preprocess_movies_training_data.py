#!/usr/bin/env python

"""Preprocess Amazon movies data to use as training or test data in the LSTM NN"""

import pandas as pd
import numpy as np
import gc

from nltk.tokenize.casual import TweetTokenizer
import emoji

from main.nlp.processing.word_embedding import WordEmbedding


__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


def parse_big_file_to_batches(file,
                              gen_words,
                              gen_emoji,
                              sequence_length=250,
                              size=300,
                              path='E:/data_sets/sentiments/train_sets/amazon_movies_full/',
                              text_field='Cleaned',
                              score_field='Score',
                              file_n='0',
                              classes=[1, 2, 3, 4, 5],
                              return_df=False):
    for start in range(0, 500000, 100000):

        df = pd.read_csv(path + file,
                         nrows=100000,
                         header=None,
                         skiprows=1 + start)
        df.columns = columns

        # ADHOC (comment it out if you want to run it on 5 values)
        # df['Score - Binary'] = 0
        # df.ix[df['Score'] == 1, 'Score - Binary'] = 'neg'
        # df.ix[df['Score'] == 5, 'Score - Binary'] = 'pos'
        # df = df[~(df['Score - Binary'] == 0)]
        print(len(df))

        block = str(str(start)[:-5])
        if start == 0:
            block = '0'
        print(len(df))

        if return_df:
            df = turn_block_to_batches(df=df,
                                       gen_words=gen_words,
                                       gen_emoji=gen_emoji,
                                       sequence_length=sequence_length,
                                       size=size,
                                       text_field=text_field,
                                       score_field=score_field,
                                       file_n=file_n,
                                       block=block,
                                       classes=classes,
                                       return_df=return_df)
            return df
        else:
            turn_block_to_batches(df=df,
                                  gen_words=gen_words,
                                  gen_emoji=gen_emoji,
                                  sequence_length=sequence_length,
                                  size=size,
                                  text_field=text_field,
                                  score_field=score_field,
                                  file_n=file_n,
                                  block=block,
                                  classes=classes,
                                  return_df=return_df)

        df = None
        gc.collect()

    return True


def turn_block_to_batches(df,
                          gen_words,
                          gen_emoji,
                          sequence_length=250,
                          size=300,
                          text_field='Cleaned',
                          score_field='Score',
                          file_n='0',
                          block='0',
                          classes=[1, 2, 3, 4, 5],
                          return_df=False):
    n_classes = len(classes)

    df_parse = df.copy()
    df = None
    df = limit_sentence_length_and_balance_classes(df=df_parse,
                                                   sequence_length=sequence_length,
                                                   text_field=text_field,
                                                   score_field=score_field,
                                                   classes=classes)
    df_parse = None

    if return_df:
        return df
    else:
        parse_balanced_df_to_numpy_batches(df=df,
                                           gen_words=gen_words,
                                           gen_emoji=gen_emoji,
                                           sequence_length=sequence_length,
                                           size=size,
                                           text_field=text_field,
                                           score_field=score_field,
                                           n_classes=n_classes,
                                           file_n=file_n,
                                           block=block)
        return True


def limit_sentence_length_and_balance_classes(df,
                                              sequence_length=250,
                                              text_field='Cleaned',
                                              score_field='Score',
                                              classes=[1, 2, 3, 4, 5]):
    word_counts = []
    for review in df[text_field]:
        try:
            word_counts.append(len(TweetTokenizer().tokenize(review)))
        except TypeError:
            print(review)
            word_counts.append(sequence_length + 10)
    x = [True if (count <= sequence_length) and (count >= 20) else False for count in word_counts]
    df = df.iloc[x].reset_index(drop=True)
    print(len(df))

    min_class = min(df[score_field].value_counts())
    print(min_class)
    df_pred = pd.DataFrame(columns=df.columns.values.tolist())
    for cl in classes:
        df_pred = df_pred.append(df[df[score_field] == cl].sample(n=min_class))

    print(df_pred[score_field].value_counts())

    df = None
    df = df_pred
    df_pred = None

    df.reset_index(drop=True, inplace=True)
    print(len(df))

    return df


def parse_balanced_df_to_numpy_batches(df,
                                       gen_words,
                                       gen_emoji,
                                       sequence_length=250,
                                       size=300,
                                       text_field='Cleaned',
                                       score_field='Score',
                                       n_classes=5,
                                       file_n='0',
                                       block='0'):
    df.reset_index(drop=True, inplace=True)

    data_Y = pd.get_dummies(df[score_field]).reset_index(drop=True).values
    data_X = np.zeros((len(df), sequence_length, size), dtype=np.float32)

    invalids = []
    for ri, snippet in enumerate(df[text_field]):

        invalid = 0
        words = TweetTokenizer().tokenize(snippet)
        for wi, word in enumerate(words):
            try:
                if word in emoji.UNICODE_EMOJI:
                    data_X[ri, wi] = gen_emoji.model[word]
                else:
                    data_X[ri, wi] = gen_words.model[word]
            except KeyError:
                data_X[ri, wi] = np.zeros(size)
                invalid += 1
        invalids += [1 - (invalid / len(words))]

    print(np.array(invalids).mean())

    for i in range(int(len(data_Y) / (batch_size))):
        size_per_class = int(len(data_Y) / n_classes)

        batch_size_per_class = int(batch_size / n_classes)

        start = i * batch_size_per_class
        stop = (i + 1) * batch_size_per_class

        ids = []
        for j in range(n_classes):
            ids += [a for a in range((start + (j * size_per_class)), (stop + (j * size_per_class)))]

        train_X = data_X[ids, :, :]
        train_Y = data_Y[ids, :]

        permutation = np.random.permutation(train_Y.shape[0])
        train_X = train_X[permutation, :, :]
        train_Y = train_Y[permutation, :]

        np.save(
            'E:/data_sets/sentiments/train_sets/amazon_movies_we_balanced_chunks/X/train_Xf=' + file_n + 'b=' + block + 'i=' + str(
                i), train_X)
        np.save(
            'E:/data_sets/sentiments/train_sets/amazon_movies_we_balanced_chunks/Y/train_Yf=' + file_n + 'b=' + block + 'i=' + str(
                i), train_Y)

    gc.collect()
    return True


if __name__ == "__main__":
    file_n = '3'
    file = 'en_amazon_movies_1p5Mto2M.csv'
    path = 'E:/data_sets/sentiments/train_sets/amazon_movies_full/'

    # Limit to reviews under 250 chars
    sequence_length = 250
    batch_size = 20
    size = 300  # sze of word embeddings
    classes = [1, 2, 3, 4, 5]
    score_field = 'Score'  # change to Score if you want to run on 5 values and change the classes to 1-5
    text_field = 'Cleaned'

    if batch_size % len(classes) != 0:
        raise Exception('the number of classes must be a fac tor of the batch size so that even chunks can be made')

    gen_words = WordEmbedding()
    gen_words.load_word2vec_model('E:/data_sets/word2vec_embeddings/GoogleNews-vectors-negative300.bin')

    gen_emoji = WordEmbedding()
    gen_emoji.load_word2vec_model('E:/data_sets/word2vec_embeddings/emoji2vec.bin')

    df = pd.read_csv('E:/data_sets/sentiments/train_sets/amazon_movies_full/en_amazon_movies_0to500k.csv', nrows=10)
    columns = df.columns
    df = None

    parse_big_file_to_batches(file=file,
                              gen_words=gen_words,
                              gen_emoji=gen_emoji,
                              sequence_length=sequence_length,
                              size=size,
                              path=path,
                              text_field='Cleaned',
                              score_field='Score',
                              file_n=file_n,
                              classes=classes)
