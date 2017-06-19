#!/usr/bin/env python
# coding: utf-8
from setuptools import setup, find_packages

__author__  = 'miettal'
__version__ = '0.0.1'
__license__ = 'MIT'


setup(
    name             = 'pyfiap',
    version          = __version__,
    description      = 'FIAP library for python',
    license          = __license__,
    author           = __author__,
    author_email     = 'none',
    url              = 'https://github.com/PlantFactory/pyfiap',
    keywords         = 'python fiap ieee1888',
    packages         = find_packages(),
    install_requires = ['suds-jurko'],
)
