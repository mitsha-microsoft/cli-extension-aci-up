#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from codecs import open
from setuptools import setup, find_packages

# TODO: Confirm this is the right version number you want and it matches your
# HISTORY.rst entry.
VERSION = '0.0.1b'

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License',
]

# TODO: Add any additional SDK dependencies here
DEPENDENCIES = [
    'azure-cli-core'
]

with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='aci',
    version=VERSION,
    description='Extension to deploy to Azure Container Instances.',
    author='Mitesh Shah',
    author_email='mitsha@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    classifiers=CLASSIFIERS,
    package_data={'azext_aci': ['azext_metadata.json']},
    packages=find_packages(exclude=["*.test","*.test.*","test.*","test"]),
    include_package_data=True,
    install_requires=DEPENDENCIES,
)