#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 License terms and conditions:
 https://www.gluu.org/license/enterprise-edition/
"""

import codecs
import os
import re
from setuptools import setup
from setuptools import find_packages


def find_version(*file_paths):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *file_paths), 'r') as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="pygluu-kubernetes",
    version=find_version("pygluu", "kubernetes", "__init__.py"),
    url="",
    copyright="Copyright 2020, Gluu Kubernetes",
    license="Gluu Support <https://www.gluu.org/license/enterprise-edition/>",
    author="Gluu",
    author_email="mo@gluu.org",
    maintainer="Mohammad Abudayyeh",
    status="Dev",
    description="",
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "kubernetes>=11.0.0b2",
        "ruamel.yaml>=0.16.5",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": ["pygluu-kubernetes=pygluu.kubernetes.create:main"],
    },
)
