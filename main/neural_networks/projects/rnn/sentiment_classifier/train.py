#!/usr/bin/env python

"""Train an LSTM NN sentiment classifier"""

import numpy as np
import datetime
import progressbar
import random
import os
import tensorflow as tf

__author__ = "Peter J Usherwood"
__python_version__ = "3.5"


class NNSentimentTrain:

    def __init__(self,
                 sequence_length=250,
                 batch_size=20,
                 n_classes=5,
                 size=300,
                 model_savepath='models/'):

        self.sequence_length = 0
        self.batch_size = 0
        self.n_classes = 0
        self.size = 0
        self.graph = None
        self.saver = None
        self.lstm_units = 0
        self.X = None
        self.Y = None
        self.prediction = None
        self.prediction_softmax = None
        self.correctPred = None
        self.accuracy = None
        self.optimizer = None
        self.loss = None
        self.model_savepath = model_savepath

        self.set_up_net(sequence_length=sequence_length,
                        batch_size=batch_size,
                        n_classes=n_classes,
                        size=size)

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
            self.X = tf.placeholder(tf.float32, [self.batch_size, self.sequence_length, self.size])

            self.lstm_units = 64

            lstmCell = tf.contrib.rnn.BasicLSTMCell(self.lstm_units)
            lstmCell = tf.contrib.rnn.DropoutWrapper(cell=lstmCell, output_keep_prob=.5)
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

            self.loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.prediction, labels=self.Y))
            self.optimizer = tf.train.AdamOptimizer().minimize(self.loss)

    def train_model(self,
                    x_train_path='E:/data_sets/sentiments/train_sets/amazon_movies_we_balanced_chunks/X/',
                    y_train_path='E:/data_sets/sentiments/train_sets/amazon_movies_we_balanced_chunks/Y/',
                    epochs=5):

        model_name = 'sentiment-' + str(self.batch_size) + '_epochs-' + str(epochs) + '_lstm'
        print('model saved as:', model_name)

        # WATCH OUT: sawi changes: saver needs to be loaded after initialising variables! (I think)
        with tf.Session(graph=self.graph) as sess:

            tf.summary.scalar('Loss', self.loss)
            tf.summary.scalar('Accuracy', self.accuracy)
            merged = tf.summary.merge_all()
            logdir = "tensorboard/" + model_name + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "/"

            tf.global_variables_initializer().run()
            saver = tf.train.Saver(keep_checkpoint_every_n_hours=1,
                                   max_to_keep=15)

            i = 0
            for e in range(epochs):
                print('in epoch', e)
                local_i = 0
                with progressbar.ProgressBar(max_value=len(os.listdir(x_train_path))) as bar:

                    # randomizing file list
                    listzip = list(zip(os.listdir(x_train_path),
                                       os.listdir(y_train_path)))
                    random.shuffle(listzip)

                    for x_file, y_file in listzip:

                        # Next Batch of reviews
                        next_batch_x = np.load(x_train_path + x_file)
                        next_batch_y = np.load(y_train_path + y_file)

                        # randomizing/shuffling batches
                        batch_pairs_list = list(zip(next_batch_x, next_batch_y))
                        random.shuffle(batch_pairs_list)

                        # extract the two things into two arrays again
                        next_batch_x, next_batch_y = zip(*batch_pairs_list)
                        next_batch_x = np.array(next_batch_x)
                        next_batch_y = np.array(next_batch_y)

                        sess.run(self.optimizer, {self.X: next_batch_x, self.Y: next_batch_y})

                        # Write summary to Tensorboard
                        if i % 200 == 0:
                            writer = tf.summary.FileWriter(logdir, sess.graph)

                            summary = sess.run(merged, {self.X: next_batch_x, self.Y: next_batch_y})
                            writer.add_summary(summary, i)

                        # Save the network
                        if i % 1000 == 0 and i != 0:
                            save_path = saver.save(sess, "models/" + model_name + ".ckpt", global_step=i)
                            print("saved to %s" % save_path)

                        i += 1
                        local_i += 1
                        bar.update(local_i)

            writer.close()

        print('Done')
