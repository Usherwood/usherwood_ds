# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='usherwood_ds',
    version='0.0.1',
    description='Peter J Usherwoods personal data science project',
    long_description=readme,
    author='Peter J Usherwood',
    author_email='peterjusherwood93@gmail.com',
    url='https://github.com/Usherwood/usherwood_ds',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

