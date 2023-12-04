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

import terseparse, terseparse.__version__

needs_pytest = set(['pytest', 'test', 'ptr']).intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

test_deps = [
    'pytest'
]

extras = {
    'test': test_deps
}

METADATA = dict(
      name='terseparse',
      description='A minimal boilerplate, composeable wrapper for argument parsing',
      version=terseparse.__version__.version_str,
      packages=['terseparse'],
      url='https://github.com/jthacker/terseparse',
      download_url='https://github.com/jthacker/terseparse/archive/v{}.tar.gz'.format(__version__),
      author='jthacker',
      author_email='thacker.jon@gmail.com',
      url='https://gitlab.com/sparkmeter/terseparse',
      keywords='Argument Parsing',
      license='MIT',
      classifiers = [],
      install_requires=[
          'six >= 1.16'
          ],
      tests_require=test_deps,
      setup_requires=pytest_runner,
      extras_require=extras,
      long_description="""
How to Install
--------------

.. code:: bash

    pip install terseparse

"""
)

def main():
    metadata = METADATA.copy()
    return setup(**metadata)

if __name__ == '__main__':
    main()
