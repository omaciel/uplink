#!/usr/bin/env python3
# coding=utf-8
"""A setuptools-based script for installing Uplink.

For more information, see:

* https://packaging.python.org/en/latest/index.html
* https://docs.python.org/distutils/sourcedist.html
"""
from setuptools import find_packages, setup  # prefer setuptools over distutils


with open('README.rst') as handle:
    LONG_DESCRIPTION = handle.read()


with open('VERSION') as handle:
    VERSION = handle.read().strip()


setup(
    name='uplink',
    version=VERSION,
    description='A library for testing Red Hat Satellite',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/omaciel/uplink',
    author='Og Maciel',
    author_email='omaciel@ogmaciel.com',
    license='GPLv3',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: GNU General Public License v3 or later '
         '(GPLv3+)'),
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(include=['uplink', 'uplink.*']),
    install_requires=[
        'click',
        'jsonschema',
        'packaging',
        'plumbum',
        'python-dateutil',
        'pyxdg',
        'requests',
    ],
    entry_points={
        'console_scripts': ['uplink=uplink.uplink_cli:uplink'],
    },
    test_suite='tests',
)
