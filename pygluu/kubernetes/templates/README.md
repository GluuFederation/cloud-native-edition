# Install Gluu using Kustomize ![CDNJS](https://img.shields.io/badge/UNDERCONSTRUCTION-red.svg?style=for-the-badge)

-   If deploying on the cloud make sure to take a look at the cloud specific notes before continuing.

    * [Amazon Web Services (AWS) - EKS](#amazon-web-services-aws---eks)
    * [GCE (Google Cloud Engine) - GKE](#gce-google-cloud-engine---gke)
    * [Azure - AKS](#azure---aks) ![CDNJS](https://img.shields.io/badge/status-pending-yellow.svg)

-   If deploying locally make sure to take a look at the specific notes bellow before continuing.
    * [Minikube](#minikube)
    * [MicroK8s](#microk8s)

-   If deploying with Couchbase as the persistence layer on AWS EKS or GCE GKE take a look at the following [Couchbase notes. ](#use-couchbase-soley-as-the-persistence-layer)  ![CDNJS](https://img.shields.io/badge/AWS-supported-green.svg) ![CDNJS](https://img.shields.io/badge/GKE-supported-green.svg)![CDNJS](https://img.shields.io/badge/microk8s-supported-green.svg)![CDNJS](https://img.shields.io/badge/minikube-supported-green.svg)


- Download [`pygluu-kubernetes.pyz`](https://github.com/GluuFederation/enterprise-edition/releases). This package can be built [manually](https://github.com/GluuFederation/enterprise-edition/blob/4.1/README.md#build-pygluu-kubernetespyz-manually).

- Run :

  ```bash
  ./pygluu-kubernetes.pyz install
  ```

Prompts will ask for the rest of the information needed. You may generate the manifests (yamls) and continue to deployment or just generate the  manifests (yamls) during the execution of `pygluu-kubernetes.pyz`. `pygluu-kubernetes.pyz` will output a file called `settings.json` holding all the parameters and can be used for a non-interactive setup. More information about this file and the vars it holds is [below](#previous-installation-variables-file-contents) but you shouldn't have to manually create this file as the script generates it for you. 

## Previous installation variables file contents

| Variable                                   | Description                                                                      | Options                                                                                     |
| ------------------------------------------ | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `NODE_SSH_KEY`                             | nodes ssh key path location                                                      | `"<pathtosshkey>"`                                                                          |
| `HOST_EXT_IP`                              | External IP of the machine                                                       |  `""` or If using Microk8s or Minikube `<ip>`                                               |
| `VERIFY_EXT_IP`                            | Verify the external IP placed                                                    | `Y` or `N`                                                                                  |
| `DEPLOYMENT_ARCH`                          | Deployment architecture                                                          | `1`=Microk8s `2`=Minikube `3`=EKS `4`=GKE `5=AKS                                            |
| `PERSISTENCE_BACKEND`                      | Backend persistence type                                                         | `0`=WrenDS `1`=Couchbase `2`=Hybrid                                                         |
| `DEPLOY_MULTI_CLUSTER`                     | Deploying a Multi-cluster [alpha]                                                | `Y` or `N`                                                                                  |
| `LDAP_VOLUME_TYPE`                         | Volume type for LDAP persistence                                                 | [options](#ldap_volume_type-options)                                                        |
| `ACCEPT_EFS_NOTES`                         | Auto accept EFS [notes](#efs-notes)                                              |  `""` or if EFS is used `Y` or `N`                                                          |
| `CACHE_TYPE`                               | Cache type to be used                                                            | `0`=Native persistence `1`=In Memory `2`=Redis                                              |
| `HYBRID_LDAP_HELD_DATA`                    | Type of data to be held in LDAP with a hybrid installation of couchbase and LDAP | `""` or if `PERSISTENCE_BACKEND`is Hybrid `0`=Default `1`=User `2`=Site `3`=Cache `4`=token |
| `AWS_LB_TYPE`                              | AWS loadbalancer type                                                            | `""` or if `DEPLOYMENT_ARCH`is AWS EKS `0`=clb `1` nlb                                      |
| `USE_ARN`                                  | Use ssl provided from ACM AWS                                                    | `""` or if `DEPLOYMENT_ARCH` is AWS EKS `Y` or `N`                                          |
| `ARN_AWS_IAM`                              | The arn string                                                                   | `""` or if `DEPLOYMENT_ARCH` is AWS EKS and using ssl the string value `arn:aws:acm:us-wes` |
| `INSTALL_COUCHBASE`                        | Install couchbase                                                                | `Y` or `N`                                                                                  |
| `VOLUME_TYPE`                              | Persistence Volume type                                                          | `io1`,`ps-ssd`, `Premium_LRS`                                                               |
| `COUCHBASE_NAMESPACE`                      | Couchbase namespace                                                              | `""` If installed `<name>`                                                                  |
| `COUCHBASE_CLUSTER_NAME`                   | Couchbase cluster name                                                           | `""` If installed `<name>`                                                                  |
| `COUCHBASE_FQDN`                           | couchbase FQDN                                                                   | `""` If installed can be `<clustername>.<namespace>.gluu.org`                               |
| `COUCHBASE_URL`                            | couchbase URL                                                                    | `""` if installed can be `<clustername>.<namespace>.cluster.local`                          |
| `COUCHBASE_USER`                           | couchbase username                                                               | `""` if installed can be `admin`                                                            |
| `ENABLE_CACHE_REFRESH`                     | Enable cache refresh installation                                                | `Y` or `N`                                                                                  |
| `ENABLE_KEY_ROTATE`                        | Enable key rotate installation                                                   | `Y` or `N`                                                                                  |
| `ENABLE_RADIUS`                            | Enable radius installation                                                       | `Y` or `N`                                                                                  |
| `ENABLE_OXPASSPORT`                        | Enable oxPassport installation                                                   | `Y` or `N`                                                                                  |
| `ENABLE_OXSHIBBOLETH`                      | Enable oxShibboleth installation                                                 | `Y` or `N`                                                                                  |
| `ENABLE_CASA`                              | Enable casa installation [alpha]                                                 | `Y` or `N`                                                                                  |
| `ENABLE_OXTRUST_API`                       | Enable oxTrust-api                                                               | `Y` or `N`                                                                                  |
| `ENABLE_OXTRUST_TEST_MODE`                 | Enable oxTrust Test Mode                                                         | `Y` or `N`                                                                                  |
| `OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE`  | Volume type for oxShibboleth and oxTrust shared volume                           | `io1`,`ps-ssd`, `Premium_LRS`                                                               |
| `EFS_FILE_SYSTEM_ID`                       | EFS file system id                                                               | `""` if EFS is used the `<id>`                                                              |
| `EFS_AWS_REGION`                           | EFS aws region                                                                   | `""` if EFS is used the `<aws-region>`                                                      |
| `EFS_DNS`                                  | EFS DNS                                                                          | `""` if EFS is used the `<efs-dns>`                                                         |
| `LOAD_PREVIOUS_PARAMS`                     | Enable using installation_variables file                                         | `Y` or `N`                                                                                  |
| `GLUU_FQDN`                                | Gluu FQDN                                                                        | `<FQDN>` i.e `demoexample.gluu.org`                                                         |
| `COUNTRY_CODE`                             | Gluu country code                                                                | `<country code>` i.e `US`                                                                   |
| `STATE`                                    | Gluu state                                                                       | `<state>` i.e `Texas`                                                                       |
| `CITY`                                     | Gluu city                                                                        | `<city>` i.e `Austin`                                                                       |
| `EMAIL`                                    | Gluu email                                                                       | `<email>` i.e `support@gluu.org`                                                            |
| `ORG_NAME`                                 | Gluu orginization name                                                           | `<org-name>` i.e `Gluu`                                                                     |
| `CONFIRM_PARAMS`                           | Confirm using above options                                                      | `Y` or `N`                                                                                  |
| `OXAUTH_REPLICAS`                          | Number of oxAuth replicas                                                        | Min `1`                                                                                     |
| `OXTRUST_REPLICAS`                         | Number of oxTrust replicas                                                       | Min `1`                                                                                     |
| `LDAP_REPLICAS`                            | Number of LDAP replicas                                                          | Min `1` if used                                                                             |
| `OXSHIBBOLETH_REPLICAS`                    | Number of oxShibboleth replicas                                                  | Min `1` if used                                                                             |
| `OXPASSPORT_REPLICAS`                      | Number of oxPassport replicas                                                    | Min `1` if used                                                                             |
| `OXD_SERVER_REPLICAS`                      | Number of oxdServer replicas                                                     | Min `1` if used                                                                             |
| `CASA_REPLICAS`                            | Number of casa replicas [alpha]                                                  | Min `1` if used                                                                             |
| `RADIUS_REPLICAS`                          | Number of radius replica                                                         | Min `1` if used                                                                             |
| `LDAP_STORAGE_SIZE`                        | LDAP volume storage size                                                         | `""` or Min `4Gi` if used                                                                   |
| `OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE` | oxShibboleth and oxTrust shared volume storage size                              | `""` or Min `4Gi` if used                                                                   |
| `CASA_STORAGE_SIZE`                        | Casa volume storage size                                                         | `""` or Min `4Gi` if used                                                                   |
| `GMAIL_ACCOUNT`                            | Gmail account for GKE installation                                               | `""` or if `DEPLOYMENT_ARCH`is GKE `<gmail>` i.e `demoexample@gmail.com` if GKE setup       |
| `LDAP_STATIC_VOLUME_ID`                    | LDAP static volume id (AWS EKS)                                                  | `""` or if used <static-volume-id>                                                          |
| `LDAP_STATIC_DISK_URI`                     | LDAP static disk uri (GCE GKE or Azure)                                           | `""` or if used <disk-uri>                                                                  |
| `IS_GLUU_FQDN_REGISTERED`                  | Is Gluu FQDN globally resolvable                                                 | `Y` or `N`                                                                                  |
| `DEPLOY_GENERATED_YAMLS`                   | Deploy the generated yamls                                                       | `Y` or `N`                                                                                  |

### EFS-Notes
 
1. EFS created

1. EFS must be inside the same region as the EKS cluster

1. VPC of EKS and EFS are the same

1. Security group of EFS allows all connections from EKS nodes

### `LDAP_VOLUME_TYPE`-Options

`LDAP_VOLUME_TYPE=""` but if `PERSISTENCE_BACKEND` is `WrenDS` options are :

| Options  | Deployemnt Architecture  | Volume Type                                   |
| -------- | ------------------------ | --------------------------------------------- |
| `1`      | Microk8s                 | LDAP volumes on host                          |
| `2`      | Minikube                 | LDAP volumes on host                          |
| `6`      | EKS                      | LDAP volumes on host                          |
| `7`      | EKS                      | LDAP EBS volumes dynamically provisioned      |
| `8`      | EKS                      | LDAP EBS volumes statically provisioned       |
| `9`      | EKS                      | LDAP EFS volume                               |
| `11`     | GKE                      | LDAP volumes on host                          |
| `12`     | GKE                      | LDAP Persistent Disk  dynamically provisioned |
| `13`     | GKE                      | LDAP Persistent Disk  statically provisioned  |
| `16`     | Azure                    | LDAP volumes on host                          |
| `17`     | Azure                    | LDAP Persistent Disk  dynamically provisioned |
| `18`     | Azure                    | LDAP Persistent Disk  statically provisioned  |



# Use Couchbase soley as the persistence layer
![CDNJS](https://img.shields.io/badge/AWS-supported-green.svg)
![CDNJS](https://img.shields.io/badge/GKE-supported-green.svg)
![CDNJS](https://img.shields.io/badge/microk8s-supported-green.svg)
![CDNJS](https://img.shields.io/badge/minikube-supported-green.svg)
![image](../../img/gluu_cb_installation.gif)

## Requirements
  - If you are installing on microk8s or minikube please ignore the below notes as a low resource `couchbase-cluster.yaml` will be applied automatically, however the VM being used must at least have 8GB RAM available.
  
  - An `m5.xlarge` EKS cluster with 3 nodes at the minimum or `n2-standard-4` GKE cluster with 3 nodes. We advice contacting Gluu regarding in production setups.

- [Install couchbase kubernetes](https://www.couchbase.com/downloads) and place the tar.gz file inside the same directory as the `pygluu-kubernetes.pyz`.

- Please modify the file `couchbase/couchbase-cluster.yaml` to fit your instituional needs. Currently the file is setup with an example setup of a total of 6 nodes as seen in `spec.servers`. Each set of services is replicating in two different zones. According to your setup these zones might be different and hence should be changed. Do not change the labels of these services such as `couchbase_services: index` the setup requires these labels to track the status of the couchbase setup.Do not change the buckets as they are required for Gluu setup. More information on the properties of this file is found [here](https://docs.couchbase.com/operator/1.2/couchbase-cluster-config.html).

> **_NOTE:_** Please note the `couchbase/couchbase-cluster.yaml` file must include at least three defined `spec.servers` with the labels `couchbase_services: index`, `couchbase_services: data` and `couchbase_services: analytics`

**If you wish to get started fast just change the values of `spec.servers.name` and `spec.servers.serverGroups` inside `couchbase/couchbase-cluster.yaml` to the zones of your EKS nodes and continue.**

- Run `./pygluu-kubernetes.pyz install-couchbase` and follow the prompts to install couchbase soley with Gluu.


# Use remote Couchbase as the persistence layer

- [Install couchbase](https://docs.couchbase.com/server/current/install/install-intro.html)

- Obtain the Public DNS or FQDN of the couchbase node.

- Head to the FQDN of the couchbase node to [setup](https://docs.couchbase.com/server/current/manage/manage-nodes/create-cluster.html) your couchbase cluster. When setting up please use the FQDN as the hostname of the new cluster.

- Couchbase URL base , user, and password will be needed for installation when running `pygluu-kubernetes.pyz`

## Scaling pods

> **_NOTE:_** When using Mircok8s substitute  `kubectl` with `microk8s.kubectl` in the below commands.

To scale pods, run the following command:

```
kubectl scale --replicas=<number> <resource> <name>
```

In this case, `<resource>` could be Deployment or Statefulset and `<name>` is the resource name.

Examples:

-   Scaling oxAuth:

    ```
    kubectl scale --replicas=2 deployment oxauth
    ```

-   Scaling oxTrust:

    ```
    kubectl scale --replicas=2 statefulset oxtrust
    ```

# Amazon Web Services (AWS) - EKS

## Setup Cluster

-  Follow this [guide](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html)
 to install a cluster with worker nodes. Please make sure that you have all the `IAM` policies for the AWS user that will be creating the cluster and volumes.

## Requirements

-   The above guide should also walk you through installing `kubectl` , `aws-iam-authenticator` and `aws cli` on the VM you will be managing your cluster and nodes from. Check to make sure.

        aws-iam-authenticator help
        aws-cli
        kubectl version

> **_NOTE:_**  ![CDNJS](https://img.shields.io/badge/CLB--green.svg) Following any AWS deployment will install a classic load balancer with an `IP` that is not static. Don't worry about the `IP` changing. All pods will be updated automatically with our script when a change in the `IP` of the load balancer occurs. However, when deploying in production, **DO NOT** use our script. Instead, assign a CNAME record for the LoadBalancer DNS name, or use Amazon Route 53 to create a hosted zone. More details in this [AWS guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/using-domain-names-with-elb.html?icmpid=docs_elb_console).

## How to expand EBS volumes

1. Make sure the `StorageClass` used in your deployment has the `allowVolumeExpansion` set to true. If you have used our EBS volume deployment strategy then you will find that this property has already been set for you.

1. Edit your persistent volume claim using `kubectl edit pvc <claim-name> -n <namespace> ` and increase the value found for `storage:` to the value needed. Make sure the volumes expand by checking the `kubectl get pvc <claim-name> -n <namespace> `.

1. Restart the associated services


# GCE (Google Cloud Engine) - GKE

## Setup Cluster

1.  Install [gcloud](https://cloud.google.com/sdk/docs/quickstarts)

1.  Install kubectl using `gcloud components install kubectl` command

1.  Create cluster:

        gcloud container clusters create CLUSTER_NAME --zone ZONE_NAME

    where `CLUSTER_NAME` is the name you choose for the cluster and `ZONE_NAME` is the name of [zone](https://cloud.google.com/compute/docs/regions-zones/) where the cluster resources live in.

1.  Configure `kubectl` to use the cluster:

        gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE_NAME

    where `CLUSTER_NAME` is the name you choose for the cluster and `ZONE_NAME` is the name of [zone](https://cloud.google.com/compute/docs/regions-zones/) where the cluster resources live in.

    Afterwards run `kubectl cluster-info` to check whether `kubectl` is ready to interact with the cluster.

# Azure - AKS
![CDNJS](https://img.shields.io/badge/status-pending-yellow.svg)

## Requirements

-   Follow this [guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) to install Azure CLI on the VM that will be managing the cluster and nodes. Check to make sure.

-   Follow this [section](https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough#create-a-resource-group) to create the resource group for the AKS setup.

-   Follow this [section](https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough#create-aks-cluster) to create the AKS cluster

-   Follow this [section](https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough#connect-to-the-cluster) to connect to the AKS cluster

# Minikube

## Requirements

1.  Install [minikube](https://github.com/kubernetes/minikube/releases).

2.  Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/).

3.  Create cluster:

        minikube start

4.  Configure `kubectl` to use the cluster:

        kubectl config use-context minikube


# MicroK8s

## Requirements

1. Install [MicroK8s](https://microk8s.io/)

1. Make sure all ports are open for [microk8s](https://microk8s.io/docs/)
