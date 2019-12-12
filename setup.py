# coding: utf-8

# Do not import unicode_literals it generate an error when install module with pip
from __future__ import (print_function,
                        absolute_import, division)

import os
import re
import setuptools
import sys

from setuptools import Command
from setuptools.command.develop import develop


from src.install import run_install_db


def get_version(path="./VERSION"):
    """ Return the version of by with regex intead of importing it"""
    version_number = open(path, "rt").read()
    return version_number


class InstallDB(Command):
    description = """ 
        Command to install database habref schema \n
        usage: python setup.py install_db --settingspath="<FILE_PATH>"
    """

    user_options = [
        ('settingspath=', None,
         'Specify a settings path to find database connexion informations.'),
    ]

    def initialize_options(self):
        """Abstract method that is required to be overwritten"""
        self.settingspath = None

    def finalize_options(self):
        """Abstract method that is required to be overwritten"""
        assert self.settingspath is not None, 'Please provide a settings file path'

    def run(self):
        run_install_db(self.settingspath)


setuptools.setup(
    name='pypn_habref_api',
    version=get_version(),
    description="Python lib related to Habref referential (INPN)",
    long_description=open('README.md', encoding="utf-8").read().strip(),
    author="Les parcs nationaux de France",
    url='https://github.com/PnX-SI/Habref-api-module',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=list(open('requirements.txt', 'r')),
    include_package_data=True,
    cmdclass={'install_db': InstallDB},
    zip_safe=False,
    keywords='ww',
    classifiers=['Development Status :: 1 - Planning',
                 'Intended Audience :: Developers',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'License :: OSI Approved :: GNU Affero General Public License v3',
                 'Operating System :: OS Independent'],
)
