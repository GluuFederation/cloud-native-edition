![microk8s](https://github.com/GluuFederation/cloud-native-edition/workflows/microk8s/badge.svg?branch=4.5)
![minikube](https://github.com/GluuFederation/cloud-native-edition/workflows/minikube/badge.svg?branch=4.5)
![awseks](https://github.com/GluuFederation/cloud-native-edition/workflows/awseks/badge.svg?branch=4.5)
![googlegke](https://github.com/GluuFederation/cloud-native-edition/workflows/googlegke/badge.svg?branch=4.5)
![testcases](https://github.com/GluuFederation/cloud-native-edition/workflows/testcases/badge.svg?branch=4.5)

# pygluu-kubernetes

## Kubernetes recipes

- Install [Gluu](https://github.com/GluuFederation/cloud-native-edition/tree/4.5/pygluu/kubernetes/templates/)

## Build `pygluu-kubernetes.pyz` manually

## Prerequisites

1.  Python 3.6+.
1.  Python `pip3` package.

## Installation

### Standard Python package

1.  Create virtual environment and activate:

    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

1.  Install the package:

    ```
    make install
    ```

    This command will install executable called `pygluu-kubernetes` and `pygluu-kubernetes-gui` available in virtual environment `PATH`.

### Python zipapp

1.  Install [shiv](https://shiv.readthedocs.io/) using `pip3`:

    ```sh
    pip3 install shiv
    ```

1.  Install the package:

    ```sh
    make zipapp
    ```

    This command will generate executable called `pygluu-kubernetes.pyz` under the same directory.

    ```sh
    make guizipapp
    ```

    This command will generate executable called `pygluu-kubernetes-gui.pyz` under the same directory.

