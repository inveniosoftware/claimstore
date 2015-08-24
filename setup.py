# -*- coding: utf-8 -*-
#
# This file is part of ClaimStore.
# Copyright (C) 2015 CERN.
#
# ClaimStore is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ClaimStore is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ClaimStore; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307,
# USA.

"""ClaimStore."""

import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand  # noqa


class PyTest(TestCommand):

    """pytest runner."""

    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        """Initialise options."""
        TestCommand.initialize_options(self)
        try:
            from ConfigParser import ConfigParser
        except ImportError:
            from configparser import ConfigParser
        config = ConfigParser()
        config.read("pytest.ini")
        self.pytest_args = config.get("pytest", "addopts").split(" ")

    def finalize_options(self):
        """Finalise options."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Run tests."""
        # import here, cause outside the eggs aren't loaded
        import pytest
        import _pytest.config
        pm = _pytest.config.get_plugin_manager()
        pm.consider_setuptools_entrypoints()
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

# Load __version__, should not be done using import.
# https://packaging.python.org/en/latest/single_source_version.html
g = {}
with open(os.path.join('claimstore', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
version = g['__version__']

tests_require = [
    'pytest-cache',
    'pytest-cov',
    'pytest-isort',
    'pytest-pep8',
    'pytest-pep257',
    'pytest',
    'coverage',
]

setup(
    name='claimstore',
    version=version,
    url='https://github.com/inveniosoftware/claimstore',
    license='GPLv2',
    author='CERN',
    author_email='info@invenio-software.org',
    description=__doc__,
    long_description=open('README.rst', 'rt').read(),
    packages=['claimstore'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'isodate',
        'jsonschema',
        'psycopg2',
        'pytz',
    ],
    extras_require={
        'development': ['Flask-DebugToolbar'],
        'docs': ['shpinx'],
    },
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
)
