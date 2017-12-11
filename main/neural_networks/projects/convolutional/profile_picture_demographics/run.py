#!/usr/bin/env python

"""Run the age classifier (for use on AWS)"""

from main.neural_networks.projects.convolutional.profile_picture_demographics import AgeClassifier

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


classifier = AgeClassifier()
classifier.train_from_disk(path_to_training_data='E:/data_sets/face_ages/group_cropped_and_flipped/chunks/train/')