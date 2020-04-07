![microk8s](https://github.com/GluuFederation/enterprise-edition/workflows/microk8s/badge.svg?branch=4.1)
![minikube](https://github.com/GluuFederation/enterprise-edition/workflows/minikube/badge.svg?branch=4.1)
![awseks](https://github.com/GluuFederation/enterprise-edition/workflows/awseks/badge.svg?branch=4.1)
![googlegke](https://github.com/GluuFederation/enterprise-edition/workflows/googlegke/badge.svg?branch=4.1)


# pygluu-kubernetes![CDNJS](https://img.shields.io/badge/Release-v1.0.3-green.svg?style=for-the-badge)

## Kubernetes recipes

- Install [Gluu](https://github.com/GluuFederation/enterprise-edition/tree/4.1/pygluu/kubernetes/templates/)

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

    This command will install executable called `pygluu-kubernetes` available in virtual environment `PATH`.

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

### Known bug

- Bug in line 101   File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/kubernetes/client/models/v1beta1_custom_resource_definition_status.py", line 101, in conditions.
  The error will look similar to the following :
  ```bash
    File "/root/.shiv/pygluu-kubernetes_3e5bddf4d309be28790a1b035ab5d72d0b9f33dfaade59da1bb9ec0bcd0165a4/site-packages/kubernetes/client/models/v1beta1_custom_resource_definition_status.py", line 54, in __init__
    self.conditions = conditions
  File "/root/.shiv/pygluu-kubernetes_3e5bddf4d309be28790a1b035ab5d72d0b9f33dfaade59da1bb9ec0bcd0165a4/site-packages/kubernetes/client/models/v1beta1_custom_resource_definition_status.py", line 101, in conditions
    ValueError: Invalid value for `conditions`, must not be `None`
  ```
  To fix this error just rerun the installation command `./pygluu-kubernetes.pyz <command>` again.

!!!note
    Another process to circumvent this bug is to build python-kubernetes-client manually detailed below.
    
```bash
    git clone --recursive https://github.com/kubernetes-client/python.git
    cd python
    git checkout release-11.0
    sed 's/raise ValueError("Invalid value for `conditions`, must not be `None`")/pass/g' ./kubernetes/client/models/v1beta1_custom_resource_definition_status.py > tmpfile.py && mv tmpfile.py ./kubernetes/client/models/v1beta1_custom_resource_definition_status.py
    sudo python3 setup.py install
``` 

Now remove the line requiring python client in pygluu-kubernetes `setup.py` file.

```bash
sed '/kubernetes>=11.0.0b2/d' ./setup.py > tmpfile.py && mv tmpfile.py setup.py
```

Build pygluu-kubernets [manually](#build-pygluu-kubernetespyz-manually).
    
 