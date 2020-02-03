# Install Gluu using Helm![CDNJS](https://img.shields.io/badge/BETA-red.svg?style=for-the-badge)

## Gluu Server

[Gluu server](https://www.gluu.org) is an open-source IAM server that sync backend identities, leverage external IDPs, and achieve SSO, 2FA and more.

## TL;DR;

## Introduction

This chart bootstraps a Gluu Server deployment on a Kubernetes cluster using Helm package manager.  
It also packages other components/services that makeup Gluu Server.

## Prerequisites

- Kubernetes 1.x
- PV provisioner support in the underlying infrastructure
- Helm3

### Instructions to set up Helm in a kubernetes cluster.
1. To install kubernetes follow the official guide found at [kubernetes](https://kubernetes.io/docs/setup/).  
2. Install Helm using the following [guide](https://helm.sh/docs/using_helm/)

## Quickstart
- Download [`pygluu-kubernetes.pyz`](https://github.com/GluuFederation/enterprise-edition/releases). This package can be built [manually](https://github.com/GluuFederation/enterprise-edition/tree/4.1).

- Run :

  ```bash
  ./pygluu-kubernetes.pyz helm-install
  ```

## Installing using Helm manually

1) Install [nginx-ingress](https://github.com/kubernetes/ingress-nginx) Helm [Chart](https://github.com/helm/charts/tree/master/stable/nginx-ingress).

   ```bash
   helm repo add stable https://helm.nginx.com/stable
   helm repo update
   helm install <nginx-release-name> stable/nginx-ingress --namespace=<nginx-namespace>
   ```

1)  - If the FQDN for gluu i.e `demoexample.gluu.org` is registered and globally resolvable, forward it to the loadbalancers address created in the previous step by nginx-ingress. A record can be added on most cloud providers to forward the domain to the loadbalancer. Forexample, on AWS assign a CNAME record for the LoadBalancer DNS name, or use Amazon Route 53 to create a hosted zone. More details in this [AWS guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/using-domain-names-with-elb.html?icmpid=docs_elb_console). Another example on [GCE](https://medium.com/@kungusamuel90/custom-domain-name-mapping-for-k8s-on-gcp-4dc263b2dabe).

    - If the FQDN is not registered aquire the loadbalancers ip if on **GCE**, or **Azure** using `kubectl get svc <release-name>-nginx-ingress-controller --output jsonpath='{.status.loadBalancer.ingress[0].ip}'` and if on **AWS** get the loadbalancers addresss using `kubectl -n ingress-nginx get svc ingress-nginx \--output jsonpath='{.status.loadBalancer.ingress[0].hostname}'`.

1)  - If deploying on the cloud make sure to take a look at the cloud specific notes before continuing.

      * [Amazon Web Services (AWS) - EKS](#amazon-web-services-aws---eks)
      * [GCE (Google Cloud Engine) - GKE](#gce-google-cloud-engine---gke)
      * [Azure - AKS](#azure---aks) ![CDNJS](https://img.shields.io/badge/status-pending-yellow.svg)

    - If deploying locally make sure to take a look at the specific notes bellow before continuing.

      * [Minikube](#minikube)
      * [MicroK8s](#microk8s)

1)  Make sure you are in the same directory as the `values.yaml` file and run:

   ```bash
   helm install <release-name> -f values.yaml -n <namespace> .
   ```

  ## Amazon Web Services (AWS) - EKS

  ### If using EFS make sure of the following:

  1. EFS created

  1. EFS must be inside the same region as the EKS cluster

  1. VPC of EKS and EFS are the same

  1. Security group of EFS allows all connections from EKS nodes

  ### Required changes to the `values.yaml`

  Inside the global `values.yaml` change the marked keys with `CHANGE-THIS`  to the appopriate values :

  ```yaml
  #global values to be used across charts
  global:
      awsLocalStorage: true #CHANGE-THIS if not in production ,hence not using EFS set awsLocalStorage to true to use for shared shibboleth files.
    provisioner: kubernetes.io/aws-ebs #CHANGE-THIS
    lbAddr: "" #CHANGE-THIS to the address recieved in the previous step axx-109xx52.us-west-2.elb.amazonaws.com
    domain: demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
    isDomainRegistered: "false" # CHANGE-THIS  "true" or "false" to specify if the domain above is registered or not.

  # If using EFS change the marked values from your EFS below:
  efs-provisioner:
    efsProvisioner:

      # Change the following:
      dnsName: "" #CHANGE-THIS if efs is used to fs-xxxxxx.efs.us-east-1.amazonaws.com
      efsFileSystemId: "" #CHANGE-THIS if efs is used to  fs-xxx
      awsRegion: "" #CHANGE-THIS if efs is used to us-east-1
      path: /opt/shared-shibboleth-idp
      provisionerName: example.com/gcp-efs
      storageClass:
        name: gcp-efs
        isDefault: false
      persistentVolume:
        accessModes: ReadWriteMany
        storage: 5Gi

  nginx:
    ingress:
      enabled: true
      path: /
      hosts:
        - demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
      tls:
        - secretName: tls-certificate
          hosts:
            - demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
  ```    

  Tweak the optional [parameteres](#configuration) in `values.yaml` to fit the setup needed.

  ## GCE (Google Cloud Engine) - GKE

  ### Required changes to the `values.yaml`

  Inside the global `values.yaml` change the marked keys with `CHANGE-THIS`  to the appopriate values :

  ```yaml
  #global values to be used across charts
  global:
      awsLocalStorage: true
    provisioner: kubernetes.io/gce-pd #CHANGE-THIS
    lbAddr: ""
    domain: demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
      # Networking configs
    nginxIp: "" #CHANGE-THIS  to the IP recieved from the previous step
    domain: demoexample.gluu.org
    isDomainRegistered: "false" # CHANGE-THIS  "true" or "false" to specify if the domain above is registered or not.
  nginx:
    ingress:
      enabled: true
      path: /
      hosts:
        - demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
      tls:
        - secretName: tls-certificate
          hosts:
            - demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
  nfs: 
    enabled: true
  ```

  Tweak the optional [parameteres](#configuration) in `values.yaml` to fit the setup needed.

  ## Minikube

  - Enable ingress on minikube

  ```bash
  minikube addons enable ingress
  ```

  ### Required changes to the `values.yaml`

  Inside the global `values.yaml` change the marked keys with `CHANGE-THIS`  to the appopriate values :

  ```yaml
  #global values to be used across charts
  global:
      awsLocalStorage: true
    provisioner: k8s.io/minikube-hostpath #CHANGE-THIS
    lbAddr: ""
    domain: demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
    nginxIp: "" #CHANGE-THIS  to the IP of minikube <minikube ip>

  nginx:
    ingress:
      enabled: true
      path: /
      hosts:
        - demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
      tls:
        - secretName: tls-certificate
          hosts:
            - demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
  ```

  Tweak the optional [parameteres](#configuration) in `values.yaml` to fit the setup needed.

  - Map gluus FQDN at `/etc/hosts` file  to the minikube IP as shown below.

  ```bash
  ##
  # Host Database
  #
  # localhost is used to configure the loopback interface
  # when the system is booting.  Do not change this entry.
  ##
  192.168.99.100	demoexample.gluu.org #minikube IP and example domain
  127.0.0.1	localhost
  255.255.255.255	broadcasthost
  ::1             localhost
  ```

  ## Microk8s

  - Enable `helm3`, `storage`, `ingress` and `dns`.

  ```bash
  sudo microk8s.enable helm3 storage ingress dns
  ```

  ### Required changes to the `values.yaml`

  Inside the global `values.yaml` change the marked keys with `CHANGE-THIS`  to the appopriate values :

  ```yaml
  #global values to be used across charts
  global:
      awsLocalStorage: true
    provisioner: microk8s.io/hostpath #CHANGE-THIS
    lbAddr: ""
    domain: demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
    nginxIp: "" #CHANGE-THIS  to the IP of the microk8s vm

  nginx:
    ingress:
      enabled: true
      path: /
      hosts:
        - demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
      tls:
        - secretName: tls-certificate
          hosts:
            - demoexample.gluu.org #CHANGE-THIS to the FQDN used for Gluu
  ```

  Tweak the optional [parameteres](#configuration) in `values.yaml` to fit the setup needed.

  - Map gluus FQDN at `/etc/hosts` file  to the microk8s vm IP as shown below.

  ```bash
  ##
  # Host Database
  #
  # localhost is used to configure the loopback interface
  # when the system is booting.  Do not change this entry.
  ##
  192.168.99.100	demoexample.gluu.org #microk8s IP and example domain
  127.0.0.1	localhost
  255.255.255.255	broadcasthost
  ::1             localhost
  ```

## Instructions on installing the chart

> **_NOTE:_** If Couchbase is the backend persistent storage, follow [Couchbase for persistent storage](#Couchbase).

## Uninstalling the Chart

To uninstall/delete `my-release` deployment:

`$ helm delete <my-release>`

If during installation the release was not defined, release name is checked by running `$ helm ls` then deleted using the previous command and the default release name.

## Configuration

|       Parameter               |      Description                                           |    Default                          |
|:------------------------------|:-----------------------------------------------------------|:------------------------------------|
| `global.cloud.enabled`        | Whether to enable cloud provisioning.                      | `false`                             |
| `global.provisioner`          | Which cloud provisioner to use when deploying              | `k8s.io/minikube-hostpath`          |
| `global.cloud.awsLocalStorage`  | Deploy to AWS cloud but use localstorage           | `true`                              |
| `global.namespace`            | namespace in which to deploy the server                    | `default`                           |
| `global.ldapServiceName`      | ldap service name. Used to connect other services to ldap  | `opendj`                            |
| `global.nginxIp`              | IP address to be used with a FQDN                          | `192.168.99.100` (for minikube)     |
| `global.oxAuthServiceName`    | `oxauth` service name - should not be changed              |  `oxauth`                           |
| `global.oxTrustServiceName`   | `oxtrust` service name - should not be changed             | `oxtrust`                           |
| `global.domain`               | DNS domain name                                            | `demoexample.gluu.org`              |
| `global.isDomainRegistered`   | Whether the domain to be used is registered or not         | `false`                             |
| `global.gluuLdapUrl`          | wrends/ldap server url. Port and service name of opendj server - should not be changed |  `opendj:1636` |
| `global.gluuMaxFraction`      | Controls how much of total RAM is up for grabs in containers running Java apps         |  `1`    |
| `global.configAdapterName`    | The config backend adapter                                 | `Kubernetes`                        |
| `global.configSecretAdapter`  | The secrets adapter                                        | `Kubernetes`                        |
| `global.gluuPersistenceType`  | Which database backend to use                              | `ldap`                              |
| `global.gluuCouchbaseUrl`     | Couchbase URL. Used only when `global.gluuPersistenceType` is `hybrid` or `couchbase` | `cbgluu.cbns.svc.cluster.local`   |
| `global.gluuCouchbaseUser`    | Couchbase user. Used only when `global.gluuPersistenceType` is `hybrid` or `couchbase` | `admin`       |
| `global.gluuCouchbasePassFile`    | Location of `couchbase_password` file                  | `/etc/gluu/conf/couchbase_password` |
| `global.gluuCouchbaseCertFile`    | Location of `couchbase.crt` used by cb for tls termination | `/etc/gluu/conf/couchbase.crt`  |
| `global.oxshibboleth.enabled`     | Whether to allow installation of oxshibboleth chart        | `false`                         |
| `global.key-rotation.enabled`        | Allow key rotation                                         | `false`                             |
| `global.cr-rotate.enabled`           | Allow cache rotation deployment                            | `false`                             |
| `global.radius.enabled`              | Enabled radius installation                                | `false`                             |
| `global.redis.enabled`               | Whether to allow installation of redis chart.              | `false`                             |
| `global.shared-shib.enabled`         | Allow installation of shared volumes. They are shared between `oxtrust` and `oxshibboleth` services. | `true`                             |
| `global.oxtrust.enabled`             | Allow installation of oxtrust                              |  `true`                             |
| `global.nginx.enabled`               | Allow installation of nginx. Should be allowed unless another nginx is being deployed   |  `true`|
| `global.config.enabled`              | Either to install config chart or not.                     | `true`                              |   
| `efs-provisioner.enabled`     | Enable EFS provisioning for AWS deployments ONLY           | `false`                             |
| `efs-provisioner.efsProvisioner.dnsName` | EFS DNS name. Usually, fs-xxxxxx.efs.aws-region.amazonaws.com | `" "`                 |
| `efs-provisioner.efsProvisioner.efsFileSystemId`  | EFS id        | `" "`                                                        |
| `efs-provisioner.efsProvisioner.awsRegion`        | AWS region which the deployment is taking place | `us-west-2`                |
| `config.orgName`              | Organisation Name                                          | `Gluu`                              |
| `config.email`                | Email to be registered with ssl                            | `support@gluu.org`                  |
| `config.adminPass`            | Admin password to log in to the UI                         | `P@ssw0rd`                          |
| `config.domain`               | FQDN                                                       | `demoexample.gluu.org`              |
| `config.countryCode`          | Country code of where the Org is located                   | `US`                                |
| `config.state`                | State                                                      | `TX`                                |
| `config.ldapType`             | Type of LDAP server to use.                                | `opendj`                            |
| `global.oxauth.enabled`              | Whether to allow installation of oxauth subchart. Should be left as true |  `true`        |
| `global.opendj.enabled`              | Allow installation of ldap Should left as true             | `true`                       |
| `global.gluuCacheType`        | Which type of cache to use.2 options `REDIS` or `NATIVE_PERSISTENCE` If `REDIS` is used redis chart must be enabled and `gluuRedisEnabled` config set to true | `NATIVE_PERSISTENCE` |
| `opendj.gluuRedisEnabled`     | Used if cache type is redis                                | `false`                             |
| `global.persistence.enabled`         | Whether to enable persistence layer. Must ALWAYS remain true | `true`                     |
| `persistence.configmap.gluuCasaEnabled`     | Enable auto install of casa chart/service while installing Gluu server chart | `false` |
| `persistence.configmap.gluuPassportEnabled` | Auto install passport service chart          | `false`                             |
| `persistence.configmap.gluuRadiusEnabled`   | Auto install radius service chart            | `false`                             |
| `persistence.configmap.gluuSamlEnabled`     | Auto enable SAML in oxshibboleth. This should be true whether or not `oxshibboleth` is installed or not. | `true` |
| `oxd-server.enabled`          | Enable or disable installation of OXD server               | `false`                             |
| `oxd-server.configmap.adminKeystorePassword`  | Keystore used to initialise the key manager. User should change this  | Random key used here.    |
| `oxd-server.configmap.applicationKeystorePassword` | Password used to decrypt the keystore generated above  | `example-P@ss`                       |  
| `nginx.ingress.enabled`       | Set routing rules to different services                    | `true`                              |
| `nginx.ingress.hosts`         | Domain name to be used while accessing the server          | `demoexample.gluu.org`              |

## Persistence

### couchbase
To use couchbase as the backend persistence option, please install helm using the installation script by running the command
`./pygluu-kuberenetes.pyz install-couchbase`.


**_NOTE_** Enabling support of `oxtrust API` and `oxtrust TEST_MODE`
 To enable `oxtrust API` support and or `oxtrust TEST_MODE` , set  `gluuOxtrustApiEnabled`  and `gluuOxtrustApiTestMode` true respectivley.

 ```yaml
 # persistence layer
 persistence:
   configmap:
      gluuOxtrustApiEnabled: true

 ```

 Consequently, to enable `oxtrust TEST_MODE` set the variable `gluuOxtrustApiTestMode` in the same persistence service to true

 ```yaml
# persistence layer
persistence:
  configmap:
     gluuOxtrustApiTestMode: true

```

## Instructions on how to install different services

Enabeling the following services automatically install the corespnding associated chart. To enable/disable them set `true` or `false` in the persistence configs as shown below.  

```yaml
# persistence layer
persistence:
  enabled: true
  configmap:
    # Auto install other services. If enabled the respective service chart will be installed
    gluuPassportEnabled: false
    gluuCasaEnabled: false
    gluuRadiusEnabled: false
    gluuSamlEnabled: false
```

### OXD-server

> **_NOTE:_** If these two are not provided `oxd-server` will fail to start.   
> **_NOTE:_** For these passwords, stick to digits and numbers only.

```yaml
oxd-server:
  configmap:
    adminKeystorePassword: admin-example-password
    applicationKeystorePassword: app-example-pass

```

### Casa

- Casa is dependant on `oxd-server`. To install it `oxd-server` must be enabled.

### Redis

To enable usage of Redis, change the following values.

```yaml
opendj:
  # options REDIS/NATIVE_PERSISTENCE
  gluuCacheType: REDIS
  # options true/false : must be enabled if cache type is REDIS
  gluuRedisEnabled: true

# redis should be enabled only when cacheType is REDIS
global:
  redis:
    enabled: true

```


### Other optional services

Other optional services like `key-rotation`, `cr-rotation`, and `radius` are enabled by setting their corresponding values to `true` under the global block.

For example, to enable `cr-rotate` set

```yaml
global:
  cr-rotate:
    enabled: true
```
