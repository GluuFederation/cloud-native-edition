## Gluu Server

[Gluu server](https://www.gluu.org) is an open-source IAM server that sync backend identities, leverage external IDPs, and achieve SSO, 2FA and more.

## TL;DR;

## Introduction

This chart bootstraps a Gluu Server deployment on a Kubernetes cluster using Helm package manager.  
It also packages other components/services that makeup Gluu Server.

## Prerequisites

- Kubernetes 1.3+ 
- PV provisioner support in the underlying infrastructure
- Helm 

### Instructions to set up Helm in a kubernetes cluster.
1. To install kubernetes follow the official guide found at [kubernetes](https://kubernetes.io/docs/setup/).  
2. After that, install Helm by following the guide [here](https://helm.sh/docs/using_helm/)  
3. Once one has access to a cluster, and installed Helm. Next step is to initialize Helm.   
`$ helm init `


## Instructions on installing the chart

### Deployments are of 2 types 
- `Cloud`
- `Local` 

For both deployments, different configurations needs to be changed depending on the deployment type as describe in [Deployments](#Deployments)

The recommended way to install the chart is with a custom `values.yaml` to specify the values required to install the chart. 

`helm install --name <release-name> -f values.yaml .`  

`< . >` means that this command is run in the root directory of the helm directory.


Tip! One can use the default [values.yaml](values.yaml) for installation and change it accordingly.

The command deploys Gluu Server on Kubernetes cluster using the default configurations. The [Configuration](#configuration) section lists the parameters that can be configured during installation.

To install the chart on different platforms follow individual instructions.  
 - [GCP](#GCE)
 - [AWS](#AWS)
 - [Minikube](#minikube)

## Uninstalling the Chart

To uninstall/delete `my-release` deployment:

`$ helm delete my-release`

If during installation the release was not defined, release name is checked by running `$ helm ls` then deleted using the previous command and the default release name.

## Configuration

|       Parameter               |      Description                                           |    Default                          |
|:------------------------------|:-----------------------------------------------------------|:------------------------------------|
| `global.cloud.enabled`        | Whether to enable cloud provisioning.                      | `false`                             |
| `global.cloud.provisioner`    | Which cloud provisioner to use when deploying              | `k8s.io/minikube-hostpath`          |
| `global.namespace`            | namespace in which to deploy the server                    | `default`                           |
| `global.serviceName`          | ldap service name. Used to connect other services to ldap  | `opendj`                            |
| `global.nginxIp`              | IP address to be used with a FQDN                          | `192.168.99.100` (for minikube)     |
| `global.oxAuthServiceName`    | `oxauth` service name - should not be changed              |  `oxauth`                           |
| `global.oxTrustSeriveName`    | `oxtrust` service name - should not be changed             | `oxtrust`                           |
| `global.domain`               | DNS domain name                                            | `demoexample.gluu.org`              |
| `global.gluuLdapUrl`          | wrends/ldap server url. Port and service name of opendj server - should not be changed |  `opendj:1636` |
| `global.gluuMaxFraction`      | Controls how much of total RAM is up for grabs in containers running Java apps         |  `1`    |
| `global.configAdapterName`    | The config backend adapter                                 | `Kubernetes`                        |
| `global.configSecretAdapter`  | The secrets adapter                                        | `Kubernetes`                        |
| `global.gluuPersistenceType`  | Which database backend to use                              | `ldap`                              |
| `global.gluuCouchBaseUrl`     | Couchbase URL. Used only when `global.gluuPersistenceType` is `hybrid` or `couchbase` | `cb.demo.gluu`   |
| `global.gluuCouchBaseUser`    | Couchbase user. Used only when `global.gluuPersistenceType` is `hybrid` or `couchbase` | `cb_user`       |
| `efs-provisioner.enabled`     | Enable EFS provisioning for AWS deployments ONLY           | `false`                             |
| `efs-provisioner.efsProvisioner.dnsName` | EFS DNS name. Usually, fs-xxxxxx.efs.aws-region.amazonaws.com | `" "`                 |
| `efs-provisioner.efsProvisioner.efsFileSystemId`  | EFS id        | `" "`                                                        |
| `efs-provisioner.efsProvisioner.awsRegion`        | AWS region which the deployment is taking place | `us-west-2`                |
| `nginx-ingress.controller.service.loadBalancerIP` | This is used if cloud deployment is used. It is the IP address associated with the FQDN `global.domain` to be used | `34.70.112.93` |
| `nginx-ingress.metrics.service.loadBalancerIP`    | As described above                     | `34.70.112.93`                      |
| `nginx-ingress.service.loadBalancerIP`            | As described above                     | `34.70.112.93`                      |
| `config.enabled`              | Either to install config chart or not.                     | `true`                              |   
| `config.orgName`              | Organisation Name                                          | `Gluu`                              |
| `config.email`                | Email to be registered with ssl                            | `support@gluu.org`                  |
| `config.adminPass`            | Admin password to log in to the UI                         | `P@ssw0rd`                          |
| `config.domain`               | FQDN                                                       | `demoexample.gluu.org`              |
| `config.countryCode`          | Country code of where the Org is located                   | `US`                                |
| `config.state`                | State                                                      | `TX`                                |
| `config.ldapType`             | Type of LDAP server to use.                                | `opendj`                            |
| `oxauth.enabled`              | Whether to allow installation of oxauth subchart. Should be left as true |  `true`               |
| `opendj.enabled`              | Allow installation of ldap Should left as true             | `true`                              |
| `opendj.gluuCacheType`        | Which type of cache to use.2 options `REDIS` or `NATIVE_PERSISTENCE` If `REDIS` is used redis chart must be enabled and `gluuRedisEnabled` config set to true | `NATIVE_PERSISTENCE`                |
| `opendj.gluuRedisEnabled`     | Used if cache type is redis                                | `false`                             |
| `redis.enabled`               | Whether to allow installation of redis chart.              | `false`                             |
| `shared-shib.enabled`         | Allow installation of shared volumes. They are shared between `oxtrust` and `oxshibboleth` services. | `true`                             |
| `oxtrust.enabled`             | Allow installation of oxtrust                              |  `true`                             |
| `nginx.enabled`               | Allow installation of nginx. Should be allowed unless another nginx is being deployed   |  `true`|
| `nginx.ingress.enabled`       | Set routing rules to different services                    | `true`                              |
| `nginx.ingress.hosts`         | Domain name to be used while accessing the server          | `demoexample.gluu.org`              |
| `oxshibboleth.enabled`        | Allow oxshibboleth installation                            | `false`                             |
| `oxpassport.enabled`          | Allow oxpassport installation                              | `false`                             |
| `key-rotation.enabled`        | Allow key rotation                                         | `false`                             |
| `cr-rotate.enabled`           | Allow cache rotation deployment                            | `false`                             |
| `radius.enabled`              | Enabled radius installation                                | `false`                             |
| `rbac.enabled`                | Enable/disable tiller RBAC in the cluster. it should be disabled when deploying to cloud  | `true` |


## Deployments

1. ## Cloud deployments.

   ### Common instructions on all Cloud providers (Both AWS and GKE)
    - Enabling RBAC in the cluster before deploying the chart. This has to be done first.  
      To do this deploy the `tiller.yaml` file   
      `$ kubectl apply -f tiller.yaml`
    - Enable cloud deployment in `global.cloud.enabled` by setting it to `true`.
    - Disable `rbac` sub-chart installation. Instructions can be found in the config table above.  
      `rbac.enabled: false`
    - Disable all services except `nginx-ingress` services. For example, to disable `config` service    
      ```
        config:
          enabled: false 
      ```
      - Install the chart by running   
      `helm install --name <release-name> -f values.yaml .`  

   ### GCE

    2 Options from here.
    1. ### Domain Name not mapped to an IP
    #### Important

      Get the `loadBalancerIP` or external IP. Wait till the loadBalancer is provisioned and get the IP address by running.  
      `kubectl get svc <release-name>-nginx-ingress-controller --output jsonpath='{.status.loadBalancer.ingress[0].ip}'`

    - Map the IP address with a domain name. One can check out this article [here](https://medium.com/@kungusamuel90/custom-domain-name-mapping-for-k8s-on-gcp-4dc263b2dabe) as a reference guide.
    - Update `loadBalancerIP` value in `values.yaml` file.  
          - `nginx-ingress.controller.service.loadBalancerIP`  
          - `nginx-ingress.metrics.service.loadBalancerIP`   
          - `nginx-ingress.service.loadBalancerIP`  
          - `global.nginxIp` 
    - Enable all the required services.
    - Upgrade the chart with the new values `helm upgrade --install <release-name> -f values.yaml .` 

    2. ### Domain already mapped to an IP address  
    - Update `loadBalancerIP` value in `values.yaml` file with IP that is already mapped to a domain. 
          - `nginx-ingress.controller.service.loadBalancerIP`  
          - `nginx-ingress.metrics.service.loadBalancerIP`   
          - `nginx-ingress.service.loadBalancerIP`  
          - `global.nginxIp` 
    - Enable the services that are required then install the chart by running
    `helm upgrade --install <release-name> -f values.yaml . `

  ### AWS   
   - Change cloud provisioner to `kubernetes.io/aws-ebs` in `global.cloud.provisioner`
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
    - Update the value of domain name in `global.domain` and also in `nginx` section as shown below
      ```
      nginx:
        enabled: true
        # ingress resources
        ingress:
          enabled: true
          path: /
          hosts:
            - demoexample.gluu.org # REPLACE THIS
          tls: 
          - secretName: tls-certificate
            hosts:
              - demoexample.gluu.org #REPLACE THIS
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
           enabled: true    -----> changed from false to true
      ```
    - Enable the services that are required then install the chart by running
    `helm upgrade --install <release-name> -f values.yaml . `
    
    
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

## Instructions on how to install different services

### Passport

Because by default `oxpassport` is disabled and needs to be configured before it can be used. There are 2 different ways to enable oxpassport.
- Method 1: Setting `oxpassport.enabled` to `true` before installation, then configuring it on the UI. Kubernetes will restart the pod until the it detects that passport has been enabled. To enable it on the UI follow these instructions.

1. Login to the UI and navigate to `Configuration` -> `Organization Configuration` -> `System Configuration` and check `Scim Support` and `Passport Support` then click `Update` button on the bottom left.
2. Navigate to `Configuration` -> `Manage Custom Scripts` -> `Person Authentication` -> `passport_social`. Check enabled and click `Save` at the top right of the screen.

3. Navigate to `Configuration` -> `Manage Custom Scripts` -> `UMA RPT Policies` -> `scim_access_policy`. Enable it by checking the box and clicking `Save`.

- Method 2: Installing the required services. Enabling installation of `oxpassport` and upgrading helm installation through,  
`helm upgrade --install RELEASE-NAME .` then following the above instructions.

### Redis

To enable usage of Redis, change the following values.

```
opendj:
  enabled: true
  # options REDIS/NATIVE_PERSISTENCE
  gluuCacheType: REDIS
  # options true/false : must be enabled if cache type is REDIS
  gluuRedisEnabled: true

# redis should be enabled only when cacheType is REDIS
redis:
  enabled: true

```


### Other optional services

Other optional services like `key-rotation`, `cr-rotation`, and `radius` are enabled by setting their corresponding values - more like the previous 2 - to true.  
For example, to enable `cr-rotate` set
```
cr-rotate:
  enabled: true

```