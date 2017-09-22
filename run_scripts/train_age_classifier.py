#!/usr/bin/env python

"""Run the age classifier (for use on AWS)"""

from main.neural_networks.run_script_examples.conv_net_applications import AgeClassifier

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


classifier = AgeClassifier()
classifier.train_from_disk(path_to_training_data='../../data_sets/face_ages/group_cropped_and_flipped/training_chunks/')