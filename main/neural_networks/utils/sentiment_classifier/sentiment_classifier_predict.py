#!/usr/bin/env python

"""Make predictions using a pre-trained LSTM NN"""

import numpy as np
import tensorflow as tf

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


class NNSentiment:

    def __init__(self,
                 sequence_length=250,
                 batch_size=500,
                 n_classes=5,
                 size=300,
                 model_filepath='models/sawi_movie_bs-20_epochs-10_lstm.ckpt-14000'):

        self.sequence_length = 0
        self.batch_size = 0
        self.n_classes = 0
        self.size = 0
        self.sess = None
        self.graph = None
        self.saver = None
        self.lstm_units = 0
        self.X = None
        self.Y = None
        self.prediction = None
        self.prediction_softmax = None
        self.correctPred = None
        self.accuracy = None
        self.model_filepath = model_filepath

        self.set_up_net(sequence_length=sequence_length,
                        batch_size=batch_size,
                        n_classes=n_classes,
                        size=size)

        self.load_model(model_filepath=self.model_filepath)

    def set_up_net(self,
                   sequence_length=250,
                   batch_size=500,
                   n_classes=5,
                   size=300):

        self.sequence_length = sequence_length
        self.batch_size = batch_size
        self.n_classes = n_classes
        self.size = size

        self.graph = tf.Graph()

        with self.graph.as_default():
            self.Y = tf.placeholder(tf.float32, [self.batch_size, self.n_classes])
            self.X = tf.placeholder(tf.float32, [self.batch_size, self.sequence_length,
                                                 self.size])

            self.lstm_units = 64

            lstmCell = tf.contrib.rnn.BasicLSTMCell(self.lstm_units)
            lstmCell = tf.contrib.rnn.DropoutWrapper(cell=lstmCell, output_keep_prob=1)
            value, _ = tf.nn.dynamic_rnn(lstmCell, self.X, dtype=tf.float32)

            weight = tf.Variable(tf.truncated_normal([self.lstm_units, self.n_classes]))
            bias = tf.Variable(tf.constant(0.1, shape=[self.n_classes]))
            value = tf.transpose(value, [1, 0, 2])
            last = tf.gather(value, int(value.get_shape()[0]) - 1)

            # raw prediction value
            self.prediction = (tf.matmul(last, weight) + bias)

            # added softmax layer to be able to think of the result as probabilities and use confidence thresholds
            self.prediction_softmax = tf.nn.softmax(tf.matmul(last, weight) + bias)

            self.correctPred = tf.equal(tf.argmax(self.prediction, 1), tf.argmax(self.Y, 1))
            self.accuracy = tf.reduce_mean(tf.cast(self.correctPred, tf.float32))

            self.saver = tf.train.Saver()

    def load_model(self,
                   model_filepath='models/sawi_movie_bs-20_epochs-10_lstm.ckpt-14000'):

        self.sess = tf.Session(graph=self.graph)

        saver = tf.train.import_meta_graph(model_filepath + '.meta')

        saver.restore(self.sess, model_filepath)

    def test_accuracy(self,
                      test_x_filepath='E:/data_sets/sentiments/test_sets/nn/X/test_Xf=0b=0i=0.npy',
                      test_y_filepath='E:/data_sets/sentiments/test_sets/nn/Y/test_Yf=0b=0i=0.npy'):

        file_x_content = np.load(test_x_filepath)
        file_y_content = np.load(test_y_filepath)

        final_accuracy_arr = []
        for i in range(0, (len(file_x_content) // self.batch_size) + 1):

            next_batch_x = file_x_content[i * self.batch_size:(i + 1) * self.batch_size]
            next_batch_y = file_y_content[i * self.batch_size:(i + 1) * self.batch_size]

            if len(next_batch_x) == self.batch_size:
                acc = (self.sess.run(self.accuracy, {self.X: next_batch_x, self.Y: next_batch_y})) * 100
                final_accuracy_arr.append(acc)

        print('average accuracy for this file comprising ', i, 'batches: ',
              sum(final_accuracy_arr) / len(final_accuracy_arr))
        print('max accuracy for a batch:', max(final_accuracy_arr), 'min accuracy for a batch:',
              min(final_accuracy_arr))

    def predict_phrase(self,
                       phrase):

        self.set_up_net(sequence_length=self.sequence_length,
                        batch_size=1,
                        n_classes=self.n_classes,
                        size=self.size)
        self.load_model()

        probabilities = self.sess.run(self.prediction_softmax, {self.X: phrase})
        sent = np.argmax(probabilities)

        return sent, probabilities
