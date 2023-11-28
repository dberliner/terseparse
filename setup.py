#!/usr/bin/python

# Copyright (c) 2023, Sparkmeter Inc
# All rights reserved.
#

"""Setup script for IntelHex."""

import sys, glob
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.core import Command

import terseparse, terseparse.version

LONG_DESCRIPTION = open('README.rst', 'r').read()

METADATA = dict(
      name='terseparse',
      version=__version__,
      scripts=glob.glob('scripts/*'),
      packages=['terseparse'],
      author='Jon Thacker',
      author_email='thacker.jon@gmail.com',
      maintainer='Daniel Berliner',
      maintainer_email='dan.berliner@sparkmeter.io',
      url='https://github.com/jthacker/terseparse',
      description='A minimal boilerplate, composeable wrapper for argument parsing',
      long_description=LONG_DESCRIPTION,
      keywords='Argument Parsing',
      license='MIT',
      classifiers = [],
      install_requires=[
          'six >= 1.16'
          ],
)

def main():
    metadata = METADATA.copy()
    return setup(**metadata)

if __name__ == '__main__':
    main()
