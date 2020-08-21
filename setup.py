# -*- coding: utf-8 -*-
# Copyright (C) 2016-2020 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-postgresql.

# pytest-postgresql is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-postgresql is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-postgresql. If not, see <http://www.gnu.org/licenses/>.
"""pytest-postgresql setup.py module."""

import os
from setuptools import setup, find_packages

here = os.path.dirname(__file__)


def read(fname):
    """
    Read given file's content.

    :param str fname: file name
    :returns: file contents
    :rtype: str
    """
    return open(os.path.join(here, fname)).read()


requirements = [
    'pytest>=3.0.0',
    'port-for',
    'mirakuru>=2.3.0'
]

test_requires = [
    'pytest-cov',
    'pytest-xdist',
]

extras_require = {
    'docs': ['sphinx'],
    'tests': test_requires,
}

setup_requires = [
    'setuptools>=21',
    'pip>=9'
]


setup(
    name='pytest-postgresql',
    version='2.4.1',
    description='Postgresql fixtures and fixture factories for Pytest.',
    long_description=(
        read('README.rst') + '\n\n' + read('CHANGES.rst')
    ),
    keywords='tests py.test pytest fixture postgresql',
    author='Clearcode - The A Room',
    author_email='thearoom@clearcode.cc',
    url='https://github.com/ClearcodeHQ/pytest-postgresql',
    license='LGPLv3+',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=requirements,
    tests_require=test_requires,
    setup_requires=setup_requires,
    test_suite='tests',
    entry_points={
        'pytest11': [
            'pytest_postgresql = pytest_postgresql.plugin'
        ]},
    include_package_data=True,
    zip_safe=False,
    extras_require=extras_require,
)
