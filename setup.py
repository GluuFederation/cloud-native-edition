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
        "ruamel.yaml>=0.16.5",
        "pyOpenSSL>=19.1.0",
        "cryptography>=2.8",
        "pyDes>=2.0.0",  # TODO: Remove the following as soon as the update secret is moved to backend
        "google-api-python-client>=1.8.0", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "requests_oauthlib>=1.3.0", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "certifi>=14.05.14", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "six>=1.9.0", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "python-dateutil>=2.5.3", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "setuptools>=46.1.3", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "pyyaml>=3.12", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "google-auth>=1.0.1", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "ipaddress>=1.0.17;python_version=='2.7'", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "websocket-client>=0.32.0,!=0.40.0,!=0.41.*,!=0.42.*", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "requests", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "requests-oauthlib", # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "urllib3>=1.24.2" # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
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
