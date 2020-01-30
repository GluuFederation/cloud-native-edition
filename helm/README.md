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
2. After that, install Helm by following the guide [here](https://helm.sh/docs/using_helm/) 
3. If one wants to deploy to a different namespace apart from `default`, it should be created first. 

## Instructions on installing the chart

> **_NOTE:_** If one is planning to use Couchbase as the Backend persistent storage, one should make sure to read instructions found at [Couchbase for persistent storage](#Couchbase) are read first before installing the chart.

### Deployments are of 2 types 
- `Cloud`
- `Local` 

For both deployments, different configurations needs to be changed depending on the deployment type as describe in [Deployments](#Deployments)

The recommended way to install the chart is with a custom `values.yaml` to specify the values required to install the chart. 

`helm install <release-name> -f values.yaml -n <namespace> .`  

**_NOTE_** `< . >` means that this command is run in the root directory of the helm directory.  
**_NOTE_** If default namespace is used, no need to include it in the install or upgrade commands.


Tip! One can use the default [values.yaml](values.yaml) for installation and change it accordingly.

The command deploys Gluu Server on Kubernetes cluster using the default configurations. The [Configuration](#configuration) section lists the parameters that can be configured during installation.

To install the chart on different platforms follow individual instructions.  
 - [GCP](#GCE)
 - [AWS](#AWS)
 - [Minikube](#minikube)
 - [Microk8s](#micrk8s)

## Uninstalling the Chart

To uninstall/delete `my-release` deployment:

`$ helm delete <my-release>`

If during installation the release was not defined, release name is checked by running `$ helm ls` then deleted using the previous command and the default release name.

## Configuration

|       Parameter               |      Description                                           |    Default                          |
|:------------------------------|:-----------------------------------------------------------|:------------------------------------|
| `global.cloud.enabled`        | Whether to enable cloud provisioning.                      | `false`                             |
| `global.provisioner`          | Which cloud provisioner to use when deploying              | `k8s.io/minikube-hostpath`          |
| `global.provisioner.awsLocalStorage`  | Deploy to AWS cloud but use localstorage           | `true`                              |
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
| `opendj.gluuCacheType`        | Which type of cache to use.2 options `REDIS` or `NATIVE_PERSISTENCE` If `REDIS` is used redis chart must be enabled and `gluuRedisEnabled` config set to true | `NATIVE_PERSISTENCE` |
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

## Deployments

1. ## Cloud deployments.

   ### Common instructions on all Cloud providers (Both AWS and GKE)
    - Change `global.provisioner` value in `values.yaml` to `kubernetes.io/gce-pd` 
    - Enable cloud deployment in `global.cloud.enabled` by setting it to `true`.
    - Install [nginx-ingress](https://github.com/kubernetes/ingress-nginx) Helm [Chart](https://github.com/helm/charts/tree/master/stable/nginx-ingress) 
    - Make sure to forward the FQDN to the LB address. 
    - Install the main Gluu server chart by running   
    `helm install <release-name> -f values.yaml -n <namespace> . `  

  ### GCE
  Two options from here.
  1. #### Domain Name not registred

  #### Important

  Get the `loadBalancerIP` or external IP. Wait till the loadBalancer is provisioned and get the IP address by running.  
      `kubectl get svc <release-name>-nginx-ingress-controller --output jsonpath='{.status.loadBalancer.ingress[0].ip}'`

  - Map the IP address with a domain name. One can check out this article [here](https://medium.com/@kungusamuel90/custom-domain-name-mapping-for-k8s-on-gcp-4dc263b2dabe) as a reference guide.
    - Update `loadBalancerIP` value in both `nginx-ingress` Chart's and Gluu Server Chart `values.yaml` files.  
    - In `nginx-ingress`
          - `nginx-ingress.controller.service.loadBalancerIP`  
          - `nginx-ingress.defaultBackend.service.loadBalancerIP`
    - For Gluu Server chart
          - `global.nginxIp` 

2. #### Mapped/registered FQDN
    - Update `loadBalancerIP` value in `nginx-ingress` `values.yaml`'s file with IP that is already mapped to a domain. 
          - `nginx-ingress.controller.service.loadBalancerIP`  
          - `nginx-ingress.defaultBackend.service.loadBalancerIP` 
    - Enable the services that are required then install the chart by running
    `helm upgrade --install <release-name> -f values.yaml -n <namespace> . `


  ### AWS   
  #### Domain Name not registered   

   - Change cloud provisioner to `kubernetes.io/aws-ebs` in `global.provisioner`   
   - Also define if you want to use `localstorage` or EFS by setting `global.provisioner.awsLocalStorage` to the appropriate value. Set it to true if you would    like to use localstorage and vice versa.    
   - Get the `loadBalancer` DNS hostname provisioned by the `nginx-ingress` e.g
   ```
    $ kubectl get svc | grep ingress-controller
        flippant-robin-nginx-ingress-controller        LoadBalancer   10.100.10.11     a96e6e325ee7d11e9a7510a49691a220-752226592.us-west-2.elb.amazonaws.com   80:32489/TCP,443:30276/TCP     82m
   ```
   - Update the value of `global.lbAddr` with the DNS name from the loadBalancer. i.e  
   
    ```   
      global:
        ;
        ;
        lbAddr: a96e6e325ee7d11e9xxxxx49691a220-752226592.us-west-2.elb.amazonaws.com
    ```

   - Create a `CNAME` that points to the ELB hostname (which won't change ).  
    i.e `aws.gluu.org -> a96e6e325ee7d11e9a7510a49691a220-752226592.us-west-2.elb.amazonaws.com`   
    This would allow integration of the scalable Gluu server behind the ELB with your domain.

   - Update `nginxIp` in `values.yaml` file with IP that is now mapped to your domain and also the domain.      
          - `global.nginxIp` 
          - `global.domain`

  #### Mapped/Registered FQDN   

   - Update the value of domain name in `nginx` section as shown below   
      ```
          global:
             nginx: true

          nginx:
            ingress:
              enabled: true
              path: /
              hosts:
                - demoexample.gluu.org # REPLACE THIS
              tls: 
                - secretName: tls-certificate
                  hosts:
                    - demoexample.gluu.org # REPLACE THIS
        
      ```
   - Because this chart is going to use `EFS-Provisioner` there are some preparations that are NEEDED before deploying as  described
     [here](https://github.com/helm/charts/tree/master/stable/efs-provisioner).
     Some notes on the same to keep in mind.
        - To be able to use a DNS name of the efs in the mount command, the following must be true:

        - The connecting EC2 instance must be inside a VPC and must be configured to use the DNS server provided by Amazon. ✅

        - The VPC of the connecting EC2 instance must have both DNS Resolution and DNS Hostnames enabled. ✅

        - The connecting EC2 instance must be inside the same VPC as the EFS file system. ✅ 

        - Mount targets must include the security groups that allow EFS to be connected ✅

   - After creating efs file system, update `efs-provisioner.efsProvisioner.dnsName` with the efs DNS name.
   - Enable `efs-provisioner` chart to be installed by setting `enabled` to `true` 
      ```
        efs-provisioner:
           enabled: false    -----> changed from false to true
      ```
   - Enable the services that are required then install the chart by running
    `helm upgrade --install <release-name> -f values.yaml -n <namespace>. `
    
    
2. ## Local deployments
    ### minikube
    - Most of the default args are meant to install the chart to a local environment.
    - One should not forget to add the domain to local machine in `/etc/hosts` file pointing to the minikube IP as shown below.
      ```
      ~ cat /etc/hosts
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

    ### microk8s
    - Use microk8s configfile with a local installation of `kubectl` to access the VM-k8s. For example in Mac
      `multipass exec microk8s-vm -- /snap/bin/microk8s.config > $HOME/.kube/config`
    - For microk8s there are some services we need to enable.
        - Enable Helm3    - `multipass exec microk8s-vm -- /snap/bin/microk8s.enable helm3`

        - Enable storrage - `multipass exec microk8s-vm -- /snap/bin/microk8s.enable storage`

        - Enable ingress  - `multipass exec microk8s-vm -- /snap/bin/microk8s.enable ingress`

        - Enable DNS      - `multipass exec microk8s-vm -- /snap/bin/microk8s.enable dns`

    - Get the IP of microk8s VM `multipass list` and include it in the `hosts` file.
    - From here, things are all the same.
      `helm install <release-name> -f values.yaml .`
    
**_NOTE_** Enabling support of `oxtrust API` and `oxtrust TEST_MODE`
 To enable `oxtrust API` support, user should set the variable `gluuOxtrustApiEnabled` in the persistence service to true.
  ```
  # persistence layer
  persistence:
    configmap:
       gluuOxtrustApiEnabled: true

  ```
 Consequently, to enable `oxtrust TEST_MODE` set the variable `gluuOxtrustApiTestMode` in the same persistence service to true
   ```
  # persistence layer
  persistence:
    configmap:
       gluuOxtrustApiTestMode: true

  ```

## Instructions on how to install different services

There are some services that have auto install enabled while installing the overall Gluu server Helm chart. This configuration is made on the persistence level. To enable/disable them  
one only needs to set `true` or ``false` in the persistence configs as shown below.  
  ```
  # persistence layer
  persistence:
    enabled: true
    configmap:
      # Auto install other services. If enabled the respective service chart will be installed
      gluuCasaEnabled: true 
      gluuPassportEnabled: false
      gluuRadiusEnabled: false
  ```

### OXD-server

> **_NOTE:_** When installing `oxd-server` chart/service, the user should change the value of the following two variables.   
> **_NOTE:_** If these two are not provided `oxd-server` will fail to start.   
> **_NOTE:_** For these passwords, stick to digits and numbers only.
```
oxd-server:
  configmap:
    adminKeystorePassword: admin-example-password
    applicationKeystorePassword: app-example-pass
```

### Casa

- Casa is dependant on `oxd-server`. Make sure it's enabled if one wants to use `Casa`.

### Redis

To enable usage of Redis, change the following values.

```
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

Other optional services like `key-rotation`, `cr-rotation`, and `radius` are enabled by setting their corresponding values - more like the previous 2 - to true under the global block.

For example, to enable `cr-rotate` set
```
global:
  cr-rotate:
    enabled: true

```
