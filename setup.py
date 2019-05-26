#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from os import path

from setuptools import find_packages, setup

README_FILE = 'README.md'

setup_requires = ['pytest-runner']

long_description = None
if path.exists(README_FILE):
    with open(README_FILE) as fh:
        long_description = fh.read()

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

with open('dev-requirements.txt', 'r') as f:
    dev_requires = f.read().splitlines()

entry_points = {
    'console_scripts': [
        'mutagen-helper = mutagen_helper.__main__:main'
    ],
}

with open('mutagen_helper/__version__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]$', f.read(), re.MULTILINE).group(1)

setup(
    name='mutagen-helper',
    version=version,
    author='Rémi Alvergnat',
    author_email='toilal.dev@gmail.com',
    description='Mutagen Helper to help you manage sessions',
    keywords="havoc mutagen sync",
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=install_requires,
    tests_require=dev_requires,
    setup_requires=setup_requires,
    entry_points=entry_points,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/gfi-centre-ouest/mutagen-helper',
    download_url='https://github.com/gfi-centre-ouest/mutagen-helper',
    license='MIT',
    zip_safe=True,
    extras_require={
        'dev': dev_requires,
        'test': dev_requires,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Networking',
        'Topic :: System :: Filesystems'
    ],
)
