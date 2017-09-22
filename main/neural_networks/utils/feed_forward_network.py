#!/usr/bin/env python

"""Implementation of a feed-forward neural network"""

import pickle

import scipy.special
from numpy.linalg import pinv
import numpy as np
import pandas as pd
import progressbar

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


class NeuralNetwork:
    """
    Feedforward Neural Network, the most simple form of a neural network, it is not recurrent as data only flows forward
    """

    def __init__(self, input_nodes=10, hidden_layers=None, output_nodes=3, learning_rate=.3):
        """
        :param input_nodes: Int number of input nodes
        :param hidden_layers: Array of ints, length of array is the number of hidden layers, values are the number of nodes
        per layer
        :param output_nodes: Int number of output hidden nodes
        :param learning_rate: Float, learning rate
        """

        if not hidden_layers:
            hidden_layers = [20]

        self.inodes = input_nodes
        self.hidden_layers = len(hidden_layers)
        self.hnodes = hidden_layers
        self.onodes = output_nodes

        self.lr = learning_rate

        self.m = [np.random.normal(0, pow(self.hnodes[0], -.5), (self.hnodes[0], self.inodes))]
        for i in range(1, self.hidden_layers):
            self.m += [np.random.normal(0, pow(self.hnodes[i], -.5), (self.hnodes[i], self.hnodes[i - 1]))]
        self.m += [np.random.normal(0, pow(self.onodes, -.5), (self.onodes, self.hnodes[-1]))]

    def activation_function(self, inputs):
        output = np.array([[scipy.special.expit(value[0])] for value in inputs])
        return output

    def inverse_activation_function(self, inputs):
        output = np.array([[scipy.special.logit(value[0])] for value in inputs])
        return output

    def train_element(self, inputs_list, targets_list):
        """
        Update the NN by training it with a single record

        :param inputs_list: List of input node values (pre-scaled)
        :param targets_list: List of targets (1 per possible target outcome), with the maximum range of the activation
         function for the desired class; minimum range of the activation function for the remaining classes

        :return: Updates the model
        """

        inputs = np.array(inputs_list, ndmin=2).T
        targets = np.array(targets_list, ndmin=2).T

        # input to first hidden
        x = [np.dot(self.m[0], inputs)]
        y = [self.activation_function(x[0])]

        # between hidden layers
        for i in range(1, self.hidden_layers):
            x += [np.dot(self.m[i], y[i - 1])] # changed x to y
            y += [self.activation_function(x[i])]

        # last hidden and the output
        x += [np.dot(self.m[-1], y[-1])]
        y += [self.activation_function(x[-1])]

        errors = [targets - y[-1]]

        for i in range(0, self.hidden_layers):
            errors += [np.dot(self.m[-(1 + i)].T, errors[i])]

        # update weights for all but first hidden layer
        for i in range(0, self.hidden_layers):
            self.m[-(1 + i)] += self.lr * np.dot((errors[i] * y[-(1 + i)] * (1 - y[-(1 + i)])), y[-(2 + i)].T)

        # first hidden layer
        self.m[0] += self.lr * np.dot((errors[-1] * y[0] * (1 - y[0])), inputs.T)

    def train(self, train_X, train_Y, epochs=2):
        """
        The primary function for training the neural network

        :param train_X: Pandas df of training records, values must be between 0.01 and 0.99
        :param train_Y: Pandas df of targets, values must be between 0.01 and 0.99
        :param epochs: The number of times to iterate over the training coprus
        """

        train_X.reset_index(drop=True, inplace=True)
        train_Y.reset_index(drop=True, inplace=True)

        train_length = len(train_X)

        with progressbar.ProgressBar(max_value=train_length * epochs) as bar:
            for e in range(epochs):
                for i in range(train_length):
                    self.train_element(train_X.iloc[i], train_Y.iloc[i])
                    bar.update(i + (e * train_length))

    def back_query_element(self, output_vector):

        outputs = np.array(output_vector, ndmin=2).T
        # Takes a pseudo inverse as the matrix is not square
        m_inv = []
        for i in range(0, self.hidden_layers):
            m_inv[i] += pinv(self.m[i])

        o_x = self.inverse_activation_function(outputs)
        y1 = np.dot(m2_inv, o_x)

        minimum = np.amin(y1)
        maximum = np.amax(y1)
        y1 = ((y1 - minimum) * (0.98 / (maximum - minimum))) + 0.01

        x1 = self.inverse_activation_function(y1)
        inputs = np.dot(m1_inv, x1)

        return inputs

    def query_element(self, inputs_list):
        """
        Take a list of values for each input node and find the result

        :param inputs_list: List of input node values (pre-scaled)

        :return: Probabilities of each target class
        """

        inputs = np.array(inputs_list, ndmin=2).T

        # input to first hidden
        x = [np.dot(self.m[0], inputs)]
        y = [self.activation_function(x[0])]

        # between hidden layers
        for i in range(1, self.hidden_layers):
            x += [np.dot(self.m[i], x[i - 1])]
            y += [self.activation_function(x[i])]

        # last hidden and the output
        x += [np.dot(self.m[-1], y[-1])]
        y += [self.activation_function(x[-1])]

        return [el[0] for el in y[-1]]

    def accuracy(self, test_X, test_Y):
        """
        Calculate the accuracy on a test set (or validation set)

        :param test_X: Pandas df of features
        :param test_Y: Pandas df of targets (in dummy variable form)

        :return: The accuracy, An array of the predicted probabilities per record (for a confusion matrix),
        The score card (whether each record was correct or not)
        """

        test_X.reset_index(drop=True, inplace=True)
        test_Y.reset_index(drop=True, inplace=True)
        score_card = []
        output_arrays = []
        for i, input_list in enumerate(test_X.values):
            output_array = self.query_element(input_list)
            output_arrays.append(output_array)
            value = np.argmax(output_array)
            if value == np.argmax(test_Y.iloc[i].values):
                score_card += [1]
            else:
                score_card += [0]

        accuracy = sum(score_card) / len(test_X)

        return accuracy, output_arrays, score_card


def save_network(network, filepath):
    """
    Saves (pickles) the above class once trained

    :param network: Instance of class NeuralNetwork
    :param filepath: String filepath
    """

    with open(filepath, 'wb') as output:
        pickle.dump(network, output, pickle.HIGHEST_PROTOCOL)

    return True


def load_network(filepath):
    """
    Load a previously trained and pickled model

    :param filepath: String filepath
    :return: The saved and trained instance of the NeuralNetwork class
    """

    with open(filepath, 'rb') as input_f:
        network = pickle.load(input_f)

    return network


def scale_df_to_nn(matrix):
    """
    Scales the input df to between 0.01 and 0.99

    :param matrix: np array (matrix or pd dataframe) to be scaled

    output scaled matrix: Scaled matrix as a pd dataframe
    """

    min_val = matrix.min().min()
    max_val = matrix.max().max()

    scaled_matrix = (((matrix - min_val) / (max_val - min_val)) * .98) + 0.01

    return scaled_matrix
