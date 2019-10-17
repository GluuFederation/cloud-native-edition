# Install Gluu using Kustomize ![CDNJS](https://img.shields.io/badge/UNDERCONSTRUCTION-red.svg?style=for-the-badge)

-   If deploying on the cloud make sure to take a look at the cloud specific notes before continuing.

    * [Amazon Web Services (AWS) - EKS](#amazon-web-services-aws---eks)
    * [GCE (Google Cloud Engine) - GKE](#gce-google-cloud-engine---gke)
    * [Azure - AKS](#azure---aks) ![CDNJS](https://img.shields.io/badge/status-pending-yellow.svg)
    
-   If deploying locally make sure to take a look at the specific notes bellow before continuing.
    * [Minikube](#minikube)
    * [MicroK8s](#microk8s)

-   If deploying with Couchbase as the persistence layer on AWS EKS take a look at the following [Couchbase notes. ](#use-couchbase-soley-as-the-persistence-layer)  ![CDNJS](https://img.shields.io/badge/AWS-supported-blue.svg)

- Get the source code:

        wget -q https://github.com/GluuFederation/enterprise-edition/archive/4.0.0.zip
        unzip 4.0.0.zip
        cd enterprise-edition-4.0.0/examples/kubernetes

- Run `bash create.sh` to initialize the installation. Prompts will ask for the rest of the information needed. An optional choice to generate the manifests (yamls) and continue to deployment or just generate the  manifests (yamls) is available during the execution of `create.sh`.


# Use Couchbase soley as the persistence layer
![CDNJS](https://img.shields.io/badge/AWS-supported-blue.svg)

    ![image](../../img/gluu_cb_installation.gif)

## Requirements
  - An m5.xlarge EKS cluster with 3 nodes at the minimum
- [Install couchbase kubernetes](https://www.couchbase.com/downloads) and place the tar.gz file inside the same directory as the `create.sh`.

- Please modify the file `couchbase/couchbase-cluster.yaml` to fit your instituional needs. Currently the file is setup with an example setup of a total of 6 nodes as seen in `spec.servers`. Each set of services is replicating in two different zones. According to your setup these zones might be different and hence should be changed. Do not change the labels of these services such as `couchbase_services: index` the setup requires these labels to track the status of the couchbase setup.Do not change the buckets as they are required for Gluu setup. More information on the properties of this file is found [here](https://docs.couchbase.com/operator/1.2/couchbase-cluster-config.html). 

> **_NOTE:_** Please note the `couchbase/couchbase-cluster.yaml` file must include at least three defined `spec.servers` with the labels `couchbase_services: index`, `couchbase_services: data` and `couchbase_services: analytics`

**If you wish to get started fast just change the values of `spec.servers.name` and `spec.servers.serverGroups` inside `couchbase/couchbase-cluster.yaml` to the zones of your EKS nodes and continue.**

- Run `create.sh` and follow the prompts to install couchbase soley with Gluu.


# Use remote Couchbase as the persistence layer

- [Install couchbase](https://docs.couchbase.com/server/current/install/install-intro.html)

- Obtain the Public DNS or FQDN of the couchbase node. 

- Head to the FQDN of the couchbase node to [setup](https://docs.couchbase.com/server/current/manage/manage-nodes/create-cluster.html) your couchbase cluster. When setting up please use the FQDN as the hostname of the new cluster.

- Couchbase URL base , user, and password will be needed for installation when running `create.sh`

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

1. Start microk8s `microk8s.start`

1. Make sure all ports are open for [microk8s](https://microk8s.io/docs/)
