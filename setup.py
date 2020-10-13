#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


# Add your dependencies in requirements.txt
# Note: you can add test-specific requirements in tox.ini
requirements = []
with open('requirements.txt') as f:
    for line in f:
        stripped = line.split("#")[0].strip()
        if len(stripped) > 0:
            requirements.append(stripped)


# https://github.com/pypa/setuptools_scm
def local_scheme(version):
    return ""

use_scm = {"write_to": "napari_manual_classifier/_version.py",
    "local_scheme":local_scheme}

setup(
    name='napari-manual-classifier',
    author='Luke Funk',
    author_email='lukefunk@broadinstitute.org',
    license='MIT',
    url='https://github.com/lukebfunk/napari-manual-classifier',
    description='Simple napari widget for manually annotating classes for each slice (last 2 dimensions) of ND-image',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=requirements,
    use_scm_version=use_scm,
    setup_requires=['setuptools_scm'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'napari.plugin': [
            'classifier = napari_manual_classifier',
        ],
    },
)
