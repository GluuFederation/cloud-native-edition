# pygluu-kuberenets

## Gluu Installation

- Install Using [kustomize](https://github.com/GluuFederation/enterprise-edition/tree/4.1/pygluu/kubernetes/templates)

- Install Using [helm](https://github.com/GluuFederation/enterprise-edition/tree/4.1/pygluu/kubernetes/templates/helm)


## To build `pygluu-kubernetes.pyz` manually.

## Prerequisites

1.  Python 3.6+.
1.  Python `pip` package.

## Installation

### Standard Python package

1.  Create virtual environment and activate:

    ```sh
    python -m venv .venv
    source ./venv/bin/activate
    ```

1.  Install the package:

    ```
    make install
    ```

    This command will install executable called `pygluu-compose` available in virtual environment `PATH`.

### Python zipapp

1.  Install [shiv](https://shiv.readthedocs.io/) using `pip`:

    ```sh
    pip install shiv
    ```

1.  Install the package:

    ```sh
    make zipapp
    ```

    This command will generate executable called `pygluu-compose.pyz` under the same directory.
