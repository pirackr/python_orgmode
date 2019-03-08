#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup

setup(
    name='python_orgmode',
    version='1.1.2',
    description='Org file (orgmode.org) parser',
    long_description='A small lib which parse org file',
    author='Pirackr',
    author_email='pirackr.inbox@gmail.com',
    url='https://github.com/pirackr/python_orgmode',
    packages=[
        'python_orgmode',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'pyparsing'
    ],
    tests_require=[
        'pytest',
        'robber'
    ],
)
