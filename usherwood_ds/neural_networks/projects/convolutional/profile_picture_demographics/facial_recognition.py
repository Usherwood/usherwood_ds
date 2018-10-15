#!/usr/bin/env python

"""Application of convolution networks using Lasagne and Kerasr"""

import os
import numpy as np
import lasagne
from lasagne import layers
from lasagne.updates import nesterov_momentum
from nolearn.lasagne import NeuralNet
import progressbar

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


class AgeClassifier:
    """Train age classifier based on techniques listed in Age and Gender Classification using Convolutional
    Neural Networks"""

    def __init__(self):
        self.net = NeuralNet(
            layers=[('input', layers.InputLayer),
                    ('conv2d1', layers.Conv2DLayer),
                    ('maxpool1', layers.MaxPool2DLayer),
                    ('conv2d2', layers.Conv2DLayer),
                    ('maxpool2', layers.MaxPool2DLayer),
                    ('conv3d2', layers.Conv2DLayer),
                    ('maxpool3', layers.MaxPool2DLayer),
                    ('dropout0', layers.DropoutLayer),
                    ('dense1', layers.DenseLayer),
                    ('dropout1', layers.DropoutLayer),
                    ('dense2', layers.DenseLayer),
                    ('dropout2', layers.DropoutLayer),
                    ('output', layers.DenseLayer),
                    ],
            # input layer
            input_shape=(None, 3, 227, 227),
            # layer conv2d1
            conv2d1_num_filters=96,
            conv2d1_filter_size=(7, 7),
            conv2d1_nonlinearity=lasagne.nonlinearities.rectify,
            conv2d1_W=lasagne.init.GlorotUniform(),
            # layer maxpool1
            maxpool1_pool_size=(3, 3),
            # layer conv2d2
            conv2d2_num_filters=256,
            conv2d2_filter_size=(5, 5),
            conv2d2_nonlinearity=lasagne.nonlinearities.rectify,
            # layer maxpool2
            maxpool2_pool_size=(3, 3),
            # layer conv3d2
            conv3d2_num_filters=384,
            conv3d2_filter_size=(3, 3),
            conv3d2_nonlinearity=lasagne.nonlinearities.rectify,
            # layer maxpool3
            maxpool3_pool_size=(2, 2),
            # dropout0
            dropout0_p=0.5,
            # dense1
            dense1_num_units=512,
            dense1_nonlinearity=lasagne.nonlinearities.rectify,
            # dropout1
            dropout1_p=0.5,
            # dense2
            dense2_num_units=512,
            dense2_nonlinearity=lasagne.nonlinearities.rectify,
            # dropout2
            dropout2_p=0.5,
            # output
            output_nonlinearity=lasagne.nonlinearities.softmax,
            output_num_units=5,
            # optimization method params
            update=nesterov_momentum,
            update_learning_rate=0.01,
            update_momentum=0.9,
            max_epochs=3,
            verbose=1,
        )

    def train_from_disk(self,
                        path_to_training_data='E:/data_sets/face_ages/group_cropped_and_flipped/training_chunks/',
                        save_every_x=10,
                        n_chunks=50):
        """
        Train net in chunks using data on hdd

        :param path_to_training_data: Path to a folder containing training data named "train_Xi" and "train_Yi"
        """

        if n_chunks == -1:
            n_chunks = int(len(os.listdir(path_to_training_data)) / 2)

        with progressbar.ProgressBar(max_value=n_chunks) as bar:
            for i in range(1, n_chunks + 1):
                train_x = np.load(
                    path_to_training_data + 'train_X' + str(i) + '.npy')
                train_y = np.load(
                    path_to_training_data + 'train_Y' + str(i) + '.npy')
                nn = self.net.fit(train_x, train_y)
                if i%save_every_x == 0:
                    print('Saving')
                    nn.save_weights_to('age_model')
                bar.update(i)

        return True
