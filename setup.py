"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
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


def get_k8s_pkg():
    # get local version (forked) kubernetes version
    # see Local version segments https://www.python.org/dev/peps/pep-0440/#id43
    here = os.path.abspath(os.path.dirname(__file__))
    k8s_pkg = os.path.join(here, "pygluu", "kubernetes", "templates", "kubernetesv11.0.0.tar.gz")
    return f"file:///{k8s_pkg}#egg=kubernetes-11.0.0"


setup(
    name="pygluu-kubernetes",
    version=find_version("pygluu", "kubernetes", "version.py"),
    url="",
    copyright="Copyright 2020, Gluu Cloud Native Edition",
    license="Apache 2.0 <https://www.apache.org/licenses/LICENSE-2.0>",
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
        "requests>=2.24.0",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "google-api-python-client>=1.8.0",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "requests_oauthlib>=1.3.0",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "certifi>=14.05.14",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "six>=1.9.0",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "python-dateutil>=2.5.3",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "setuptools>=46.1.3",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "pyyaml>=3.12",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "google-auth>=1.0.1",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "ipaddress>=1.0.17;python_version=='2.7'",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "websocket-client>=0.32.0,!=0.40.0,!=0.41.*,!=0.42.*",  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
        "certifi>=2020.6.20",  # TODO: May be removed, required by requests package.
        "kubernetes==11.0.0",
        "Flask==1.1.2",
        "Click!=7.0,>=6.7",
        "Flask-WTF >= 0.14.2",
        "email_validator >= 1.1.0",
        "Flask-SocketIO == 4.3.1",
        "python-engineio == 3.13.2",
        "python-socketio == 4.6.0",
        "Pygtail >= 0.11.1",
        "PyYAML >= 5.4.1",
        "gunicorn >= 20.0.4",
        "gevent >= 20.9.0"
    ],
    dependency_links=[
        get_k8s_pkg(),  # TODO: Remove the following as soon as the kubernetes python client is fixed upstream
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache 2.0 License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3s",
        "Programming Language :: Python :: 3.6",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pygluu-kubernetes=pygluu.kubernetes.create:main",
            "pygluu-kubernetes-gui=pygluu.kubernetes.gui.server:run",
        ],
    },
)
