# gluu

![Version: 1.8.39](https://img.shields.io/badge/Version-1.8.39-informational?style=flat-square) ![AppVersion: 4.5.5](https://img.shields.io/badge/AppVersion-4.5.5-informational?style=flat-square)

Gluu Access and Identity Mangement

**Homepage:** <https://www.gluu.org>

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| moabu | <support@gluu.org> |  |

## Source Code

* <https://gluu.org/docs/gluu-server>
* <https://github.com/GluuFederation/cloud-native-edition>

## Requirements

Kubernetes: `>=v1.22.0-0`

| Repository | Name | Version |
|------------|------|---------|
|  | casa | 1.8.39 |
|  | config | 1.8.39 |
|  | cr-rotate | 1.8.39 |
|  | fido2 | 1.8.39 |
|  | gluu-alb-ingress | 1.8.39 |
|  | gluu-istio-ingress | 1.8.39 |
|  | jackrabbit | 1.8.39 |
|  | nginx-ingress | 1.8.39 |
|  | opendj | 1.8.39 |
|  | oxauth | 1.8.39 |
|  | oxauth-key-rotation | 1.8.39 |
|  | oxd-server | 1.8.39 |
|  | oxpassport | 1.8.39 |
|  | oxshibboleth | 1.8.39 |
|  | oxtrust | 1.8.39 |
|  | persistence | 1.8.39 |
|  | scim | 1.8.39 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| casa | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"customScripts":[],"dnsConfig":{},"dnsPolicy":"","hpa":{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50},"image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/casa","tag":"4.5.5-1"},"istioDestinationRuleCookieTTL":"60s","lifecycle":{},"livenessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5},"nodeSelector":{},"pdb":{"enabled":true,"maxUnavailable":"90%"},"readinessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5},"replicas":1,"resources":{"limits":{"cpu":"500m","memory":"500Mi"},"requests":{"cpu":"500m","memory":"500Mi"}},"service":{"casaServiceName":"casa","name":"http-casa","port":8080},"tolerations":[],"topologySpreadConstraints":{},"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | Gluu Casa ("Casa") is a self-service web portal for end-users to manage authentication and authorization preferences for their account in a Gluu Server. |
| casa.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| casa.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| casa.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| casa.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| casa.dnsConfig | object | `{}` | Add custom dns config |
| casa.dnsPolicy | string | `""` | Add custom dns policy |
| casa.hpa | object | `{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50}` | Configure the HorizontalPodAutoscaler |
| casa.hpa.behavior | object | `{}` | Scaling Policies |
| casa.hpa.metrics | list | `[]` | metrics if targetCPUUtilizationPercentage is not set |
| casa.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| casa.image.pullSecrets | list | `[]` | Image Pull Secrets |
| casa.image.repository | string | `"gluufederation/casa"` | Image  to use for deploying. |
| casa.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| casa.istioDestinationRuleCookieTTL | string | `"60s"` | Istio Destination Rule loadBalancer.consistentHash.httpCookie.ttl if istio ingress is enabled |
| casa.livenessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5}` | Configure the liveness healthcheck for casa if needed. |
| casa.pdb | object | `{"enabled":true,"maxUnavailable":"90%"}` | Configure the PodDisruptionBudget |
| casa.readinessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5}` | Configure the readiness healthcheck for the casa if needed. |
| casa.replicas | int | `1` | Service replica number. |
| casa.resources | object | `{"limits":{"cpu":"500m","memory":"500Mi"},"requests":{"cpu":"500m","memory":"500Mi"}}` | Resource specs. |
| casa.resources.limits.cpu | string | `"500m"` | CPU limit. |
| casa.resources.limits.memory | string | `"500Mi"` | Memory limit. This value is used to calculate memory allocation for Java. Currently it only supports `Mi`. Please refrain from using other units. |
| casa.resources.requests.cpu | string | `"500m"` | CPU request. |
| casa.resources.requests.memory | string | `"500Mi"` | Memory request. |
| casa.service.casaServiceName | string | `"casa"` | Name of the casa service. Please keep it as default. |
| casa.service.name | string | `"http-casa"` | The name of the casa port within the casa service. Please keep it as default. |
| casa.service.port | int | `8080` | Port of the casa service. Please keep it as default. |
| casa.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| casa.topologySpreadConstraints | object | `{}` | Configure the topology spread constraints. Notice this is a map NOT a list as in the upstream API https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ |
| casa.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| casa.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| casa.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| casa.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| casa.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| config | object | `{"additionalAnnotations":{},"additionalLabels":{},"adminPass":"P@ssw0rd","affinity":{},"city":"Austin","configmap":{"cnAwsAccessKeyId":"","cnAwsDefaultRegion":"us-west-1","cnAwsProfile":"gluu","cnAwsSecretAccessKey":"","cnAwsSecretsEndpointUrl":"","cnAwsSecretsNamePrefix":"gluu","cnAwsSecretsReplicaRegions":[],"cnGoogleProjectId":"google-project-to-save-config-and-secrets-to","cnGoogleServiceAccount":"SWFtTm90YVNlcnZpY2VBY2NvdW50Q2hhbmdlTWV0b09uZQo=","cnGoogleSpannerDatabaseId":"","cnGoogleSpannerEmulatorHost":"","cnGoogleSpannerInstanceId":"","cnSecretGoogleSecretNamePrefix":"gluu","cnSecretGoogleSecretVersionId":"latest","cnSqlDbDialect":"mysql","cnSqlDbHost":"my-release-mysql.default.svc.cluster.local","cnSqlDbName":"gluu","cnSqlDbPort":3306,"cnSqlDbTimezone":"UTC","cnSqlDbUser":"gluu","cnSqlPasswordFile":"/etc/gluu/conf/sql_password","cnSqldbUserPassword":"Test1234#","containerMetadataName":"kubernetes","gluuCacheType":"NATIVE_PERSISTENCE","gluuCasaEnabled":false,"gluuCouchbaseBucketPrefix":"gluu","gluuCouchbaseCertFile":"/etc/certs/couchbase.crt","gluuCouchbaseCrt":"LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURlakNDQW1LZ0F3SUJBZ0lKQUwyem5UWlREUHFNTUEwR0NTcUdTSWIzRFFFQkN3VUFNQzB4S3pBcEJnTlYKQkFNTUlpb3VZMkpuYkhWMUxtUmxabUYxYkhRdWMzWmpMbU5zZFhOMFpYSXViRzlqWVd3d0hoY05NakF3TWpBMQpNRGt4T1RVeFdoY05NekF3TWpBeU1Ea3hPVFV4V2pBdE1Tc3dLUVlEVlFRRERDSXFMbU5pWjJ4MWRTNWtaV1poCmRXeDBMbk4yWXk1amJIVnpkR1Z5TG14dlkyRnNNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUIKQ2dLQ0FRRUFycmQ5T3lvSnRsVzhnNW5nWlJtL2FKWjJ2eUtubGU3dVFIUEw4Q2RJa1RNdjB0eHZhR1B5UkNQQgo3RE00RTFkLzhMaU5takdZZk41QjZjWjlRUmNCaG1VNmFyUDRKZUZ3c0x0cTFGT3MxaDlmWGo3d3NzcTYrYmlkCjV6Umw3UEE0YmdvOXVkUVRzU1UrWDJUUVRDc0dxVVVPWExrZ3NCMjI0RDNsdkFCbmZOeHcvYnFQa2ZCQTFxVzYKVXpxellMdHN6WE5GY0dQMFhtU3c4WjJuaFhhUGlva2pPT2dyMkMrbVFZK0htQ2xGUWRpd2g2ZjBYR0V0STMrKwoyMStTejdXRkF6RlFBVUp2MHIvZnk4TDRXZzh1YysvalgwTGQrc2NoQTlNQjh3YmJORUp2ZjNMOGZ5QjZ0cTd2CjF4b0FnL0g0S1dJaHdqSEN0dFVnWU1oU0xWV3UrUUlEQVFBQm80R2NNSUdaTUIwR0ExVWREZ1FXQkJTWmQxWU0KVGNIRVZjSENNUmp6ejczZitEVmxxREJkQmdOVkhTTUVWakJVZ0JTWmQxWU1UY0hFVmNIQ01Sanp6NzNmK0RWbApxS0V4cEM4d0xURXJNQ2tHQTFVRUF3d2lLaTVqWW1kc2RYVXVaR1ZtWVhWc2RDNXpkbU11WTJ4MWMzUmxjaTVzCmIyTmhiSUlKQUwyem5UWlREUHFNTUF3R0ExVWRFd1FGTUFNQkFmOHdDd1lEVlIwUEJBUURBZ0VHTUEwR0NTcUcKU0liM0RRRUJDd1VBQTRJQkFRQk9meTVWSHlKZCtWUTBXaUQ1aSs2cmhidGNpSmtFN0YwWVVVZnJ6UFN2YWVFWQp2NElVWStWOC9UNnE4Mk9vVWU1eCtvS2dzbFBsL01nZEg2SW9CRnVtaUFqek14RTdUYUhHcXJ5dk13Qk5IKzB5CnhadG9mSnFXQzhGeUlwTVFHTEs0RVBGd3VHRlJnazZMRGR2ZEN5NVdxWW1MQWdBZVh5VWNaNnlHYkdMTjRPUDUKZTFiaEFiLzRXWXRxRHVydFJrWjNEejlZcis4VWNCVTRLT005OHBZN05aaXFmKzlCZVkvOEhZaVQ2Q0RRWWgyTgoyK0VWRFBHcFE4UkVsRThhN1ZLL29MemlOaXFyRjllNDV1OU1KdjM1ZktmNUJjK2FKdWduTGcwaUZUYmNaT1prCkpuYkUvUENIUDZFWmxLaEFiZUdnendtS1dDbTZTL3g0TklRK2JtMmoKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=","gluuCouchbaseIndexNumReplica":0,"gluuCouchbasePass":"P@ssw0rd","gluuCouchbasePassFile":"/etc/gluu/conf/couchbase_password","gluuCouchbaseSuperUser":"admin","gluuCouchbaseSuperUserPass":"P@ssw0rd","gluuCouchbaseSuperUserPassFile":"/etc/gluu/conf/couchbase_superuser_password","gluuCouchbaseUrl":"cbgluu.default.svc.cluster.local","gluuCouchbaseUser":"gluu","gluuDocumentStoreType":"DB","gluuJackrabbitAdminId":"admin","gluuJackrabbitAdminIdFile":"/etc/gluu/conf/jackrabbit_admin_id","gluuJackrabbitAdminPassFile":"/etc/gluu/conf/jackrabbit_admin_password","gluuJackrabbitPostgresDatabaseName":"jackrabbit","gluuJackrabbitPostgresHost":"postgresql.postgres.svc.cluster.local","gluuJackrabbitPostgresPasswordFile":"/etc/gluu/conf/postgres_password","gluuJackrabbitPostgresPort":5432,"gluuJackrabbitPostgresUser":"jackrabbit","gluuJackrabbitSyncInterval":300,"gluuJackrabbitUrl":"http://jackrabbit:8080","gluuLdapUrl":"opendj:1636","gluuMaxRamPercent":"75.0","gluuOxauthBackend":"oxauth:8080","gluuOxdAdminCertCn":"oxd-server","gluuOxdApplicationCertCn":"oxd-server","gluuOxdBindIpAddresses":"*","gluuOxdServerUrl":"oxd-server:8443","gluuOxtrustApiEnabled":false,"gluuOxtrustApiTestMode":false,"gluuOxtrustBackend":"oxtrust:8080","gluuOxtrustConfigGeneration":true,"gluuPassportEnabled":false,"gluuPassportFailureRedirectUrl":"","gluuPersistenceLdapMapping":"default","gluuRedisSentinelGroup":"","gluuRedisSslTruststore":"","gluuRedisType":"STANDALONE","gluuRedisUrl":"redis:6379","gluuRedisUseSsl":"false","gluuSamlEnabled":false,"gluuScimProtectionMode":"OAUTH","gluuSyncCasaManifests":false,"gluuSyncShibManifests":false,"lbAddr":""},"countryCode":"US","customScripts":[],"dnsConfig":{},"dnsPolicy":"","email":"support@gluu.com","image":{"pullSecrets":[],"repository":"gluufederation/config-init","tag":"4.5.5-1"},"ldapPass":"P@ssw0rd","lifecycle":{},"migration":{"enabled":false,"migrationDataFormat":"ldif","migrationDir":"/ce-migration"},"nodeSelector":{},"orgName":"Gluu","redisPass":"P@assw0rd","resources":{"limits":{"cpu":"300m","memory":"300Mi"},"requests":{"cpu":"300m","memory":"300Mi"}},"salt":"","state":"TX","tolerations":[],"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | Configuration parameters for setup and initial configuration secret and config layers used by Gluu services. |
| config.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| config.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| config.adminPass | string | `"P@ssw0rd"` | Admin password to log in to the UI. |
| config.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| config.city | string | `"Austin"` | City. Used for certificate creation. |
| config.configmap.cnGoogleProjectId | string | `"google-project-to-save-config-and-secrets-to"` | Project id of the google project the secret manager and/or spanner instance belongs to. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| config.configmap.cnGoogleServiceAccount | string | `"SWFtTm90YVNlcnZpY2VBY2NvdW50Q2hhbmdlTWV0b09uZQo="` | Service account with roles roles/secretmanager.admin base64 encoded string. This is used often inside the services to reach the configuration layer. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| config.configmap.cnGoogleSpannerDatabaseId | string | `""` | Google Spanner Database ID. Used only when global.gluuPersistenceType is spanner. |
| config.configmap.cnGoogleSpannerEmulatorHost | string | `""` | Google Spanner Emulator Host. Used only when global.gluuPersistenceType is spanner and during testing if needed. |
| config.configmap.cnGoogleSpannerInstanceId | string | `""` | Google Spanner ID. Used only when global.gluuPersistenceType is spanner. |
| config.configmap.cnSecretGoogleSecretNamePrefix | string | `"gluu"` | Prefix for Gluu secret in Google Secret Manager. Defaults to gluu. If left gluu-secret secret will be created. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| config.configmap.cnSecretGoogleSecretVersionId | string | `"latest"` | Secret version to be used for secret configuration. Defaults to latest and should normally always stay that way. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| config.configmap.cnSqlDbDialect | string | `"mysql"` | SQL database dialect. `mysql` or `pgsql` |
| config.configmap.cnSqlDbHost | string | `"my-release-mysql.default.svc.cluster.local"` | SQL database host uri. |
| config.configmap.cnSqlDbName | string | `"gluu"` | SQL database name. |
| config.configmap.cnSqlDbPort | int | `3306` | SQL database port. |
| config.configmap.cnSqlDbTimezone | string | `"UTC"` | SQL database timezone. |
| config.configmap.cnSqlDbUser | string | `"gluu"` | SQL database username. |
| config.configmap.cnSqlPasswordFile | string | `"/etc/gluu/conf/sql_password"` | SQL password file holding password from config.configmap.cnSqldbUserPassword . |
| config.configmap.cnSqldbUserPassword | string | `"Test1234#"` | SQL password  injected as config.configmap.cnSqlPasswordFile . |
| config.configmap.gluuCacheType | string | `"NATIVE_PERSISTENCE"` | Cache type. `NATIVE_PERSISTENCE`, `REDIS`. or `IN_MEMORY`. Defaults to `NATIVE_PERSISTENCE` . |
| config.configmap.gluuCasaEnabled | bool | `false` | Enable Casa flag . |
| config.configmap.gluuCouchbaseBucketPrefix | string | `"gluu"` | The prefix of couchbase buckets. This helps with separation in between different environments and allows for the same couchbase cluster to be used by different setups of Gluu. |
| config.configmap.gluuCouchbaseCertFile | string | `"/etc/certs/couchbase.crt"` | Location of `couchbase.crt` used by Couchbase SDK for tls termination. The file path must end with couchbase.crt. In mTLS setups this is not required. |
| config.configmap.gluuCouchbaseCrt | string | `"LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURlakNDQW1LZ0F3SUJBZ0lKQUwyem5UWlREUHFNTUEwR0NTcUdTSWIzRFFFQkN3VUFNQzB4S3pBcEJnTlYKQkFNTUlpb3VZMkpuYkhWMUxtUmxabUYxYkhRdWMzWmpMbU5zZFhOMFpYSXViRzlqWVd3d0hoY05NakF3TWpBMQpNRGt4T1RVeFdoY05NekF3TWpBeU1Ea3hPVFV4V2pBdE1Tc3dLUVlEVlFRRERDSXFMbU5pWjJ4MWRTNWtaV1poCmRXeDBMbk4yWXk1amJIVnpkR1Z5TG14dlkyRnNNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUIKQ2dLQ0FRRUFycmQ5T3lvSnRsVzhnNW5nWlJtL2FKWjJ2eUtubGU3dVFIUEw4Q2RJa1RNdjB0eHZhR1B5UkNQQgo3RE00RTFkLzhMaU5takdZZk41QjZjWjlRUmNCaG1VNmFyUDRKZUZ3c0x0cTFGT3MxaDlmWGo3d3NzcTYrYmlkCjV6Umw3UEE0YmdvOXVkUVRzU1UrWDJUUVRDc0dxVVVPWExrZ3NCMjI0RDNsdkFCbmZOeHcvYnFQa2ZCQTFxVzYKVXpxellMdHN6WE5GY0dQMFhtU3c4WjJuaFhhUGlva2pPT2dyMkMrbVFZK0htQ2xGUWRpd2g2ZjBYR0V0STMrKwoyMStTejdXRkF6RlFBVUp2MHIvZnk4TDRXZzh1YysvalgwTGQrc2NoQTlNQjh3YmJORUp2ZjNMOGZ5QjZ0cTd2CjF4b0FnL0g0S1dJaHdqSEN0dFVnWU1oU0xWV3UrUUlEQVFBQm80R2NNSUdaTUIwR0ExVWREZ1FXQkJTWmQxWU0KVGNIRVZjSENNUmp6ejczZitEVmxxREJkQmdOVkhTTUVWakJVZ0JTWmQxWU1UY0hFVmNIQ01Sanp6NzNmK0RWbApxS0V4cEM4d0xURXJNQ2tHQTFVRUF3d2lLaTVqWW1kc2RYVXVaR1ZtWVhWc2RDNXpkbU11WTJ4MWMzUmxjaTVzCmIyTmhiSUlKQUwyem5UWlREUHFNTUF3R0ExVWRFd1FGTUFNQkFmOHdDd1lEVlIwUEJBUURBZ0VHTUEwR0NTcUcKU0liM0RRRUJDd1VBQTRJQkFRQk9meTVWSHlKZCtWUTBXaUQ1aSs2cmhidGNpSmtFN0YwWVVVZnJ6UFN2YWVFWQp2NElVWStWOC9UNnE4Mk9vVWU1eCtvS2dzbFBsL01nZEg2SW9CRnVtaUFqek14RTdUYUhHcXJ5dk13Qk5IKzB5CnhadG9mSnFXQzhGeUlwTVFHTEs0RVBGd3VHRlJnazZMRGR2ZEN5NVdxWW1MQWdBZVh5VWNaNnlHYkdMTjRPUDUKZTFiaEFiLzRXWXRxRHVydFJrWjNEejlZcis4VWNCVTRLT005OHBZN05aaXFmKzlCZVkvOEhZaVQ2Q0RRWWgyTgoyK0VWRFBHcFE4UkVsRThhN1ZLL29MemlOaXFyRjllNDV1OU1KdjM1ZktmNUJjK2FKdWduTGcwaUZUYmNaT1prCkpuYkUvUENIUDZFWmxLaEFiZUdnendtS1dDbTZTL3g0TklRK2JtMmoKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo="` | Couchbase certificate authority string. This must be encoded using base64. This can also be found in your couchbase UI Security > Root Certificate. In mTLS setups this is not required. |
| config.configmap.gluuCouchbaseIndexNumReplica | int | `0` | The number of replicas per index created. Please note that the number of index nodes must be one greater than the number of index replicas. That means if your couchbase cluster only has 2 index nodes you cannot place the number of replicas to be higher than 1. |
| config.configmap.gluuCouchbasePass | string | `"P@ssw0rd"` | Couchbase password for the restricted user config.configmap.gluuCouchbaseUser  that is often used inside the services. The password must contain one digit, one uppercase letter, one lower case letter and one symbol . |
| config.configmap.gluuCouchbasePassFile | string | `"/etc/gluu/conf/couchbase_password"` | The location of the Couchbase restricted user config.configmap.gluuCouchbaseUser password. The file path must end with couchbase_password |
| config.configmap.gluuCouchbaseSuperUser | string | `"admin"` | The Couchbase super user (admin) user name. This user is used during initialization only. |
| config.configmap.gluuCouchbaseSuperUserPass | string | `"P@ssw0rd"` | Couchbase password for the super user config.configmap.gluuCouchbaseSuperUser  that is used during the initialization process. The password must contain one digit, one uppercase letter, one lower case letter and one symbol |
| config.configmap.gluuCouchbaseSuperUserPassFile | string | `"/etc/gluu/conf/couchbase_superuser_password"` | The location of the Couchbase restricted user config.configmap.gluuCouchbaseSuperUser password. The file path must end with couchbase_superuser_password. |
| config.configmap.gluuCouchbaseUrl | string | `"cbgluu.default.svc.cluster.local"` | Couchbase URL. Used only when global.gluuPersistenceType is hybrid or couchbase. This should be in FQDN format for either remote or local Couchbase clusters. The address can be an internal address inside the kubernetes cluster |
| config.configmap.gluuCouchbaseUser | string | `"gluu"` | Couchbase restricted user. Used only when global.gluuPersistenceType is hybrid or couchbase. |
| config.configmap.gluuDocumentStoreType | string | `"DB"` | Document store type to use for shibboleth files DB, LOCAL, or JCA (deprecated). Note that if JCA is selected Apache Jackrabbit will be used. |
| config.configmap.gluuJackrabbitAdminId | string | `"admin"` | Jackrabbit admin uid. |
| config.configmap.gluuJackrabbitAdminIdFile | string | `"/etc/gluu/conf/jackrabbit_admin_id"` | The location of the Jackrabbit admin uid config.gluuJackrabbitAdminId. The file path must end with jackrabbit_admin_id. |
| config.configmap.gluuJackrabbitAdminPassFile | string | `"/etc/gluu/conf/jackrabbit_admin_password"` | The location of the Jackrabbit admin password jackrabbit.secrets.gluuJackrabbitAdminPassword. The file path must end with jackrabbit_admin_password. |
| config.configmap.gluuJackrabbitPostgresDatabaseName | string | `"jackrabbit"` | Jackrabbit postgres database name. |
| config.configmap.gluuJackrabbitPostgresHost | string | `"postgresql.postgres.svc.cluster.local"` | Postgres url |
| config.configmap.gluuJackrabbitPostgresPasswordFile | string | `"/etc/gluu/conf/postgres_password"` | The location of the Jackrabbit postgres password file jackrabbit.secrets.gluuJackrabbitPostgresPassword. The file path must end with postgres_password. |
| config.configmap.gluuJackrabbitPostgresPort | int | `5432` | Jackrabbit Postgres port |
| config.configmap.gluuJackrabbitPostgresUser | string | `"jackrabbit"` | Jackrabbit Postgres uid |
| config.configmap.gluuJackrabbitSyncInterval | int | `300` | Interval between files sync (default to 300 seconds). |
| config.configmap.gluuJackrabbitUrl | string | `"http://jackrabbit:8080"` | Jackrabbit internal url. Normally left as default. |
| config.configmap.gluuLdapUrl | string | `"opendj:1636"` | OpenDJ internal address. Leave as default. Used when `global.gluuPersistenceType` is set to `ldap`. |
| config.configmap.gluuMaxRamPercent | string | `"75.0"` | Value passed to Java option -XX:MaxRAMPercentage |
| config.configmap.gluuOxauthBackend | string | `"oxauth:8080"` | oxAuth internal address. Leave as default. |
| config.configmap.gluuOxdAdminCertCn | string | `"oxd-server"` | OXD serve OAuth client admin certificate common name. This should be left to the default value client-api . |
| config.configmap.gluuOxdApplicationCertCn | string | `"oxd-server"` | OXD server OAuth client application certificate common name. This should be left to the default value client-api. |
| config.configmap.gluuOxdBindIpAddresses | string | `"*"` | OXD server bind address. This limits what ip ranges can access the client-api. This should be left as * and controlled by a NetworkPolicy |
| config.configmap.gluuOxdServerUrl | string | `"oxd-server:8443"` | OXD server Oauth client address. This should be left intact in kubernetes as it uses the internal address format. |
| config.configmap.gluuOxtrustApiEnabled | bool | `false` | Enable oxTrust API |
| config.configmap.gluuOxtrustApiTestMode | bool | `false` | Enable oxTrust API testmode |
| config.configmap.gluuOxtrustBackend | string | `"oxtrust:8080"` | oxTrust internal address. Leave as default. |
| config.configmap.gluuOxtrustConfigGeneration | bool | `true` | Whether to generate oxShibboleth configuration or not (default to true). |
| config.configmap.gluuPassportEnabled | bool | `false` | Boolean flag to enable/disable passport chart |
| config.configmap.gluuPassportFailureRedirectUrl | string | `""` | TEMP KEY TO BE REMOVED IN 4.4 which allows passport failure redirect url to be specified. |
| config.configmap.gluuPersistenceLdapMapping | string | `"default"` | Specify data that should be saved in LDAP (one of default, user, cache, site, token, or session; default to default). Note this environment only takes effect when `global.gluuPersistenceType`  is set to `hybrid`. |
| config.configmap.gluuRedisSentinelGroup | string | `""` | Redis Sentinel Group. Often set when `config.configmap.gluuRedisType` is set to `SENTINEL`. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| config.configmap.gluuRedisSslTruststore | string | `""` | Redis SSL truststore. Optional. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| config.configmap.gluuRedisType | string | `"STANDALONE"` | Redis service type. `STANDALONE` or `CLUSTER`. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| config.configmap.gluuRedisUrl | string | `"redis:6379"` | Redis URL and port number <url>:<port>. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| config.configmap.gluuRedisUseSsl | string | `"false"` | Boolean to use SSL in Redis. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| config.configmap.gluuSamlEnabled | bool | `false` | Enable SAML-related features; UI menu, etc. |
| config.configmap.gluuScimProtectionMode | string | `"OAUTH"` | SCIM protection mode OAUTH|TEST|UMA |
| config.configmap.gluuSyncCasaManifests | bool | `false` | Activate manual Casa files sync - depreciated |
| config.configmap.gluuSyncShibManifests | bool | `false` | Activate manual Shib files sync - depreciated |
| config.configmap.lbAddr | string | `""` | Loadbalancer address for AWS if the FQDN is not registered. |
| config.countryCode | string | `"US"` | Country code. Used for certificate creation. |
| config.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| config.dnsConfig | object | `{}` | Add custom dns config |
| config.dnsPolicy | string | `""` | Add custom dns policy |
| config.email | string | `"support@gluu.com"` | Email address of the administrator usually. Used for certificate creation. |
| config.image.pullSecrets | list | `[]` | Image Pull Secrets |
| config.image.repository | string | `"gluufederation/config-init"` | Image  to use for deploying. |
| config.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| config.ldapPass | string | `"P@ssw0rd"` | LDAP admin password if OpenDJ is used for persistence. |
| config.migration | object | `{"enabled":false,"migrationDataFormat":"ldif","migrationDir":"/ce-migration"}` | CE to CN Migration section |
| config.migration.enabled | bool | `false` | Boolean flag to enable migration from CE |
| config.migration.migrationDataFormat | string | `"ldif"` | migration data-format depending on persistence backend. Supported data formats are ldif, couchbase+json, spanner+avro, postgresql+json, and mysql+json. |
| config.migration.migrationDir | string | `"/ce-migration"` | Directory holding all migration files |
| config.orgName | string | `"Gluu"` | Organization name. Used for certificate creation. |
| config.redisPass | string | `"P@assw0rd"` | Redis admin password if `config.configmap.gluuCacheType` is set to `REDIS`. |
| config.resources | object | `{"limits":{"cpu":"300m","memory":"300Mi"},"requests":{"cpu":"300m","memory":"300Mi"}}` | Resource specs. |
| config.resources.limits.cpu | string | `"300m"` | CPU limit. |
| config.resources.limits.memory | string | `"300Mi"` | Memory limit. |
| config.resources.requests.cpu | string | `"300m"` | CPU request. |
| config.resources.requests.memory | string | `"300Mi"` | Memory request. |
| config.salt | string | `""` | Salt. Used for encoding/decoding sensitive data. If omitted or set to empty string, the value will be self-generated. Otherwise, a 24 alphanumeric characters are allowed as its value. |
| config.state | string | `"TX"` | State code. Used for certificate creation. |
| config.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| config.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service. |
| config.usrEnvs.normal | object | `{}` | Add custom normal envs to the service. variable1: value1 |
| config.usrEnvs.secret | object | `{}` | Add custom secret envs to the service. variable1: value1 |
| config.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| config.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| cr-rotate | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"dnsConfig":{},"dnsPolicy":"","image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/cr-rotate","tag":"4.5.5-1"},"lifecycle":{},"nodeSelector":{},"resources":{"limits":{"cpu":"200m","memory":"200Mi"},"requests":{"cpu":"200m","memory":"200Mi"}},"service":{"crRotateServiceName":"cr-rotate","name":"http-cr-rotate","port":8084},"tolerations":[],"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | CacheRefreshRotation is a special container to monitor cache refresh on oxTrust containers. This may be depreciated. |
| cr-rotate.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| cr-rotate.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| cr-rotate.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| cr-rotate.dnsConfig | object | `{}` | Add custom dns config |
| cr-rotate.dnsPolicy | string | `""` | Add custom dns policy |
| cr-rotate.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| cr-rotate.image.pullSecrets | list | `[]` | Image Pull Secrets |
| cr-rotate.image.repository | string | `"gluufederation/cr-rotate"` | Image  to use for deploying. |
| cr-rotate.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| cr-rotate.resources | object | `{"limits":{"cpu":"200m","memory":"200Mi"},"requests":{"cpu":"200m","memory":"200Mi"}}` | Resource specs. |
| cr-rotate.resources.limits.cpu | string | `"200m"` | CPU limit. |
| cr-rotate.resources.limits.memory | string | `"200Mi"` | Memory limit. |
| cr-rotate.resources.requests.cpu | string | `"200m"` | CPU request. |
| cr-rotate.resources.requests.memory | string | `"200Mi"` | Memory request. |
| cr-rotate.service.crRotateServiceName | string | `"cr-rotate"` | Name of the cr-rotate service. Please keep it as default. |
| cr-rotate.service.name | string | `"http-cr-rotate"` | The name of the cr-rotate port within the cr-rotate service. Please keep it as default. |
| cr-rotate.service.port | int | `8084` | Port of the casa service. Please keep it as default. |
| cr-rotate.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| cr-rotate.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| cr-rotate.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| cr-rotate.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| cr-rotate.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| cr-rotate.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| fido2 | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"customScripts":[],"dnsConfig":{},"dnsPolicy":"","hpa":{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50},"image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/fido2","tag":"4.5.5-1"},"lifecycle":{},"livenessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5},"nodeSelector":{},"pdb":{"enabled":true,"maxUnavailable":"90%"},"readinessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5},"replicas":1,"resources":{"limits":{"cpu":"500m","memory":"500Mi"},"requests":{"cpu":"500m","memory":"500Mi"}},"service":{"fido2ServiceName":"fido2","name":"http-fido2","port":8080},"tolerations":[],"topologySpreadConstraints":{},"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | FIDO 2.0 (FIDO2) is an open authentication standard that enables leveraging common devices to authenticate to online services in both mobile and desktop environments. |
| fido2.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| fido2.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| fido2.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| fido2.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| fido2.dnsConfig | object | `{}` | Add custom dns config |
| fido2.dnsPolicy | string | `""` | Add custom dns policy |
| fido2.hpa | object | `{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50}` | Configure the HorizontalPodAutoscaler |
| fido2.hpa.behavior | object | `{}` | Scaling Policies |
| fido2.hpa.metrics | list | `[]` | metrics if targetCPUUtilizationPercentage is not set |
| fido2.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| fido2.image.pullSecrets | list | `[]` | Image Pull Secrets |
| fido2.image.repository | string | `"gluufederation/fido2"` | Image  to use for deploying. |
| fido2.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| fido2.livenessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5}` | Configure the liveness healthcheck for the fido2 if needed. |
| fido2.pdb | object | `{"enabled":true,"maxUnavailable":"90%"}` | Configure the PodDisruptionBudget |
| fido2.readinessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5}` | Configure the readiness healthcheck for the fido2 if needed. |
| fido2.replicas | int | `1` | Service replica number. |
| fido2.resources | object | `{"limits":{"cpu":"500m","memory":"500Mi"},"requests":{"cpu":"500m","memory":"500Mi"}}` | Resource specs. |
| fido2.resources.limits.cpu | string | `"500m"` | CPU limit. |
| fido2.resources.limits.memory | string | `"500Mi"` | Memory limit. This value is used to calculate memory allocation for Java. Currently it only supports `Mi`. Please refrain from using other units. |
| fido2.resources.requests.cpu | string | `"500m"` | CPU request. |
| fido2.resources.requests.memory | string | `"500Mi"` | Memory request. |
| fido2.service.fido2ServiceName | string | `"fido2"` | Name of the fido2 service. Please keep it as default. |
| fido2.service.name | string | `"http-fido2"` | The name of the fido2 port within the fido2 service. Please keep it as default. |
| fido2.service.port | int | `8080` | Port of the fido2 service. Please keep it as default. |
| fido2.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| fido2.topologySpreadConstraints | object | `{}` | Configure the topology spread constraints. Notice this is a map NOT a list as in the upstream API https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ |
| fido2.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| fido2.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| fido2.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| fido2.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| fido2.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| global | object | `{"alb":{"ingress":{"additionalAnnotations":{"alb.ingress.kubernetes.io/auth-session-cookie":"custom-cookie","alb.ingress.kubernetes.io/certificate-arn":"arn:aws:acm:us-west-2:xxxx:certificate/xxxxxx","alb.ingress.kubernetes.io/scheme":"internet-facing","kubernetes.io/ingress.class":"alb"},"additionalLabels":{},"adminUiEnabled":true,"authServerEnabled":true,"casaEnabled":false,"enabled":false,"fido2ConfigEnabled":false,"fido2Enabled":false,"openidConfigEnabled":true,"passportEnabled":false,"scimConfigEnabled":false,"scimEnabled":false,"shibEnabled":false,"u2fConfigEnabled":true,"uma2ConfigEnabled":true,"webdiscoveryEnabled":true,"webfingerEnabled":true}},"azureStorageAccountType":"Standard_LRS","azureStorageKind":"Managed","casa":{"gluuCustomJavaOptions":""},"cloud":{"testEnviroment":false},"cnAwsConfigFile":"/etc/gluu/conf/aws_config_file","cnAwsSecretsReplicaRegionsFile":"/etc/gluu/conf/aws_secrets_replica_regions","cnAwsSharedCredentialsFile":"/etc/gluu/conf/aws_shared_credential_file","cnGoogleApplicationCredentials":"/etc/gluu/conf/google-credentials.json","config":{"enabled":true},"configAdapterName":"kubernetes","configSecretAdapter":"kubernetes","cr-rotate":{"enabled":false},"domain":"demoexample.gluu.org","enableSecurityContextWithNonRegisteredDomain":"true","fido2":{"appLoggers":{"enableStdoutLogPrefix":"true","fido2LogLevel":"INFO","fido2LogTarget":"STDOUT","persistenceLogLevel":"INFO","persistenceLogTarget":"FILE"},"enabled":false,"gluuCustomJavaOptions":""},"gcePdStorageType":"pd-standard","gluuJackrabbitCluster":"true","gluuPersistenceType":"couchbase","isDomainRegistered":"false","istio":{"additionalAnnotations":{},"additionalLabels":{},"enabled":false,"gateways":[],"ingress":false,"namespace":"istio-system"},"jackrabbit":{"appLoggers":{"jackrabbitLogLevel":"INFO","jackrabbitLogTarget":"STDOUT"},"enabled":false},"jobTtlSecondsAfterFinished":300,"lbIp":"22.22.22.22","ldapServiceName":"opendj","nginx-ingress":{"enabled":true},"opendj":{"enabled":false},"oxauth":{"appLoggers":{"auditStatsLogLevel":"INFO","auditStatsLogTarget":"FILE","authLogLevel":"INFO","authLogTarget":"STDOUT","cleanerLogLevel":"INFO","cleanerLogTarget":"FILE","enableStdoutLogPrefix":"true","httpLogLevel":"INFO","httpLogTarget":"FILE","ldapStatsLogLevel":"INFO","ldapStatsLogTarget":"FILE","persistenceDurationLogLevel":"INFO","persistenceDurationLogTarget":"FILE","persistenceLogLevel":"INFO","persistenceLogTarget":"FILE","scriptLogLevel":"INFO","scriptLogTarget":"FILE"},"enabled":true,"gluuCustomJavaOptions":""},"oxauth-key-rotation":{"enabled":false},"oxd-server":{"appLoggers":{"oxdServerLogLevel":"INFO","oxdServerLogTarget":"STDOUT"},"enabled":true,"gluuCustomJavaOptions":""},"oxshibboleth":{"appLoggers":{"auditStatsLogLevel":"INFO","auditStatsLogTarget":"FILE","consentAuditLogLevel":"INFO","consentAuditLogTarget":"FILE","containerLogLevel":"","enableStdoutLogPrefix":"true","encryptionLogLevel":"","httpclientLogLevel":"","idpLogLevel":"INFO","idpLogTarget":"STDOUT","ldapLogLevel":"","messagesLogLevel":"","opensamlLogLevel":"","propsLogLevel":"","scriptLogLevel":"INFO","scriptLogTarget":"FILE","springLogLevel":"","xmlsecLogLevel":""},"enabled":false,"gluuCustomJavaOptions":""},"oxtrust":{"appLoggers":{"apachehcLogLevel":"INFO","apachehcLogTarget":"FILE","auditStatsLogLevel":"INFO","auditStatsLogTarget":"FILE","cacheRefreshLogLevel":"INFO","cacheRefreshLogTarget":"FILE","cacheRefreshPythonLogLevel":"INFO","cacheRefreshPythonLogTarget":"FILE","cleanerLogLevel":"INFO","cleanerLogTarget":"FILE","enableStdoutLogPrefix":"true","httpLogLevel":"INFO","httpLogTarget":"FILE","ldapStatsLogLevel":"INFO","ldapStatsLogTarget":"FILE","oxtrustLogLevel":"INFO","oxtrustLogTarget":"STDOUT","persistenceDurationLogLevel":"INFO","persistenceDurationLogTarget":"FILE","persistenceLogLevel":"INFO","persistenceLogTarget":"FILE","scriptLogLevel":"INFO","scriptLogTarget":"FILE","velocityLogLevel":"INFO","velocityLogTarget":"FILE"},"enabled":true,"gluuCustomJavaOptions":"-XshowSettings:vm -XX:MaxRAMPercentage=80"},"persistence":{"enabled":true},"scim":{"appLoggers":{"enableStdoutLogPrefix":"true","persistenceDurationLogLevel":"INFO","persistenceDurationLogTarget":"FILE","persistenceLogLevel":"INFO","persistenceLogTarget":"FILE","scimLogLevel":"INFO","scimLogTarget":"STDOUT","scriptLogLevel":"INFO","scriptLogTarget":"FILE"},"enabled":false,"gluuCustomJavaOptions":""},"sslCertFromDomain":"false","storageClass":{"allowVolumeExpansion":true,"allowedTopologies":[],"mountOptions":["debug"],"parameters":{},"provisioner":"microk8s.io/hostpath","reclaimPolicy":"Retain","volumeBindingMode":"WaitForFirstConsumer"},"upgrade":{"enabled":false,"image":{"repository":"gluufederation/upgrade","tag":"4.5.5-1"},"sourceVersion":"4.5","targetVersion":"4.5"},"usrEnvs":{"normal":{},"secret":{}}}` | Parameters used globally across all services helm charts. |
| global.alb.ingress.additionalAnnotations | object | `{"alb.ingress.kubernetes.io/auth-session-cookie":"custom-cookie","alb.ingress.kubernetes.io/certificate-arn":"arn:aws:acm:us-west-2:xxxx:certificate/xxxxxx","alb.ingress.kubernetes.io/scheme":"internet-facing","kubernetes.io/ingress.class":"alb"}` | Additional annotations that will be added across all ingress definitions in the format of {cert-manager.io/issuer: "letsencrypt-prod"} |
| global.alb.ingress.additionalLabels | object | `{}` | Additional labels that will be added across all ingress definitions in the format of {mylabel: "myapp"} |
| global.alb.ingress.adminUiEnabled | bool | `true` | Enable Admin UI endpoints /identity |
| global.alb.ingress.authServerEnabled | bool | `true` | Enable Auth server endpoints /oxauth |
| global.alb.ingress.casaEnabled | bool | `false` | Enable casa endpoints /casa |
| global.alb.ingress.fido2ConfigEnabled | bool | `false` | Enable endpoint /.well-known/fido2-configuration |
| global.alb.ingress.fido2Enabled | bool | `false` | Enable  all fido2 endpoints /fido2 |
| global.alb.ingress.openidConfigEnabled | bool | `true` | Enable endpoint /.well-known/openid-configuration |
| global.alb.ingress.passportEnabled | bool | `false` | Enable passport /passport |
| global.alb.ingress.scimConfigEnabled | bool | `false` | Enable endpoint /.well-known/scim-configuration |
| global.alb.ingress.scimEnabled | bool | `false` | Enable SCIM endpoints /scim |
| global.alb.ingress.shibEnabled | bool | `false` | Enable  oxshibboleth endpoints /idp |
| global.alb.ingress.u2fConfigEnabled | bool | `true` | Enable endpoint /.well-known/fido-configuration |
| global.alb.ingress.uma2ConfigEnabled | bool | `true` | Enable endpoint /.well-known/uma2-configuration |
| global.alb.ingress.webdiscoveryEnabled | bool | `true` | Enable endpoint /.well-known/simple-web-discovery |
| global.alb.ingress.webfingerEnabled | bool | `true` | Enable endpoint /.well-known/webfinger |
| global.azureStorageAccountType | string | `"Standard_LRS"` | Volume storage type if using Azure disks. |
| global.azureStorageKind | string | `"Managed"` | Azure storage kind if using Azure disks |
| global.casa.gluuCustomJavaOptions | string | `""` | passing custom  java options to casa. DO NOT PASS GLUU_JAVA_OPTIONS in envs. |
| global.cloud.testEnviroment | bool | `false` | Boolean flag if enabled will strip resources requests and limits from all services. |
| global.cnGoogleApplicationCredentials | string | `"/etc/gluu/conf/google-credentials.json"` | Base64 encoded service account. The sa must have roles/secretmanager.admin to use Google secrets and roles/spanner.databaseUser to use Spanner. Leave as this is a sensible default. |
| global.config.enabled | bool | `true` | Boolean flag to enable/disable the configuration chart. This normally should never be false |
| global.configAdapterName | string | `"kubernetes"` | The config backend adapter that will hold Gluu configuration layer. aws|google|kubernetes. OpenDJ as a persistence is restricted to kubernetes ONLY! |
| global.configSecretAdapter | string | `"kubernetes"` | The config backend adapter that will hold Gluu secret layer. aws|google|kubernetes OpenDJ as a persistence is restricted to kubernetes ONLY! |
| global.cr-rotate.enabled | bool | `false` | Boolean flag to enable/disable the cr-rotate chart. |
| global.domain | string | `"demoexample.gluu.org"` | Fully qualified domain name to be used for Gluu installation. This address will be used to reach Gluu services. |
| global.fido2.appLoggers | object | `{"enableStdoutLogPrefix":"true","fido2LogLevel":"INFO","fido2LogTarget":"STDOUT","persistenceLogLevel":"INFO","persistenceLogTarget":"FILE"}` | App loggers can be configured to define where the logs will be redirected to and the level of each in which it should be displayed. log levels are "OFF", "FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE" Targets are "STDOUT" and "FILE" |
| global.fido2.appLoggers.enableStdoutLogPrefix | string | `"true"` | Enable log prefixing which enables prepending the STDOUT logs with the file name. i.e fido2-persistence ===> 2022-12-20 17:49:55,744 INFO |
| global.fido2.appLoggers.fido2LogLevel | string | `"INFO"` | fido2.log level |
| global.fido2.appLoggers.fido2LogTarget | string | `"STDOUT"` | fido2.log target |
| global.fido2.appLoggers.persistenceLogLevel | string | `"INFO"` | fido2_persistence.log level |
| global.fido2.appLoggers.persistenceLogTarget | string | `"FILE"` | fido2_persistence.log target |
| global.fido2.enabled | bool | `false` | Boolean flag to enable/disable the fido2 chart. |
| global.fido2.gluuCustomJavaOptions | string | `""` | passing custom  java options to fido2. Notice you do not need to pass in any loggers options as they are introduced below in appLoggers. DO NOT PASS GLUU_JAVA_OPTIONS in envs. |
| global.gcePdStorageType | string | `"pd-standard"` | GCE storage kind if using Google disks |
| global.gluuJackrabbitCluster | string | `"true"` | Boolean flag if enabled will enable jackrabbit in cluster mode with Postgres. |
| global.gluuPersistenceType | string | `"couchbase"` | Persistence backend to run Gluu with ldap|couchbase|hybrid|sql|spanner. |
| global.isDomainRegistered | string | `"false"` | Boolean flag to enable mapping global.lbIp  to global.fqdn inside pods on clouds that provide static ip for loadbalancers. On cloud that provide only addresses to the LB this flag will enable a script to actively scan config.configmap.lbAddr and update the hosts file inside the pods automatically. This flag also runs containers in root. Please be advised as your setup should have the domain registered. |
| global.istio.additionalAnnotations | object | `{}` | Additional annotations that will be added across the gateway in the format of {cert-manager.io/issuer: "letsencrypt-prod"} |
| global.istio.additionalLabels | object | `{}` | Additional labels that will be added across the gateway in the format of {mylabel: "myapp"} |
| global.istio.enabled | bool | `false` | Boolean flag that enables using istio gateway for Gluu. This assumes istio ingress is installed and hence the LB is available. |
| global.istio.gateways | list | `[]` | Custom istio gateways name to be used for Gluu. This is only used when global.istio.enabled is set to true and a gateway has been created in the environment outside this helm chart lifecycle. gateways:  - "gluu-gateway" |
| global.istio.ingress | bool | `false` | Boolean flag that enables using istio side cars with Gluu services. |
| global.istio.namespace | string | `"istio-system"` | The namespace istio is deployed in. The is normally istio-system. |
| global.jackrabbit.appLoggers | object | `{"jackrabbitLogLevel":"INFO","jackrabbitLogTarget":"STDOUT"}` | App loggers can be configured to define where the logs will be redirected to and the level of each in which it should be displayed. log levels are "OFF", "FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE" Targets are "STDOUT" and "FILE" |
| global.jackrabbit.appLoggers.jackrabbitLogLevel | string | `"INFO"` | jackrabbit.log level |
| global.jackrabbit.appLoggers.jackrabbitLogTarget | string | `"STDOUT"` | jackrabbit.log target |
| global.jackrabbit.enabled | bool | `false` | Boolean flag to enable/disable the jackrabbit chart. For more information on how it is used inside Gluu https://gluu.org/docs/gluu-server/4.2/installation-guide/install-kubernetes/#working-with-jackrabbit. |
| global.jobTtlSecondsAfterFinished | int | `300` | https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/ |
| global.lbIp | string | `"22.22.22.22"` | The Loadbalancer IP created by nginx or istio on clouds that provide static IPs. This is not needed if `global.domain` is globally resolvable. |
| global.ldapServiceName | string | `"opendj"` | Name of the OpenDJ service. Please keep it as default. |
| global.nginx-ingress.enabled | bool | `true` | Boolean flag to enable/disable the nginx-ingress definitions chart. |
| global.opendj.enabled | bool | `false` | Boolean flag to enable/disable the OpenDJ  chart. |
| global.oxauth-key-rotation.enabled | bool | `false` | Boolean flag to enable/disable the oxauth-server-key rotation cronjob chart. |
| global.oxauth.appLoggers | object | `{"auditStatsLogLevel":"INFO","auditStatsLogTarget":"FILE","authLogLevel":"INFO","authLogTarget":"STDOUT","cleanerLogLevel":"INFO","cleanerLogTarget":"FILE","enableStdoutLogPrefix":"true","httpLogLevel":"INFO","httpLogTarget":"FILE","ldapStatsLogLevel":"INFO","ldapStatsLogTarget":"FILE","persistenceDurationLogLevel":"INFO","persistenceDurationLogTarget":"FILE","persistenceLogLevel":"INFO","persistenceLogTarget":"FILE","scriptLogLevel":"INFO","scriptLogTarget":"FILE"}` | App loggers can be configured to define where the logs will be redirected to and the level of each in which it should be displayed. log levels are "OFF", "FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE" Targets are "STDOUT" and "FILE" |
| global.oxauth.appLoggers.auditStatsLogLevel | string | `"INFO"` | oxauth_audit.log level |
| global.oxauth.appLoggers.auditStatsLogTarget | string | `"FILE"` | oxauth_script.log target |
| global.oxauth.appLoggers.authLogLevel | string | `"INFO"` | oxauth.log level |
| global.oxauth.appLoggers.authLogTarget | string | `"STDOUT"` | oxauth.log target |
| global.oxauth.appLoggers.cleanerLogLevel | string | `"INFO"` | cleaner log level |
| global.oxauth.appLoggers.cleanerLogTarget | string | `"FILE"` | cleaner log target |
| global.oxauth.appLoggers.enableStdoutLogPrefix | string | `"true"` | Enable log prefixing which enables prepending the STDOUT logs with the file name. i.e oxauth-script ===> 2022-12-20 17:49:55,744 INFO |
| global.oxauth.appLoggers.httpLogLevel | string | `"INFO"` | http_request_response.log level |
| global.oxauth.appLoggers.httpLogTarget | string | `"FILE"` | http_request_response.log target |
| global.oxauth.appLoggers.ldapStatsLogLevel | string | `"INFO"` | oxauth_persistence_ldap_statistics.log level |
| global.oxauth.appLoggers.ldapStatsLogTarget | string | `"FILE"` | oxauth_persistence_ldap_statistics.log target |
| global.oxauth.appLoggers.persistenceDurationLogLevel | string | `"INFO"` | oxauth_persistence_duration.log level |
| global.oxauth.appLoggers.persistenceDurationLogTarget | string | `"FILE"` | oxauth_persistence_duration.log target |
| global.oxauth.appLoggers.persistenceLogLevel | string | `"INFO"` | oxauth_persistence.log level |
| global.oxauth.appLoggers.persistenceLogTarget | string | `"FILE"` | oxauth_persistence.log target |
| global.oxauth.appLoggers.scriptLogLevel | string | `"INFO"` | oxauth_script.log level |
| global.oxauth.appLoggers.scriptLogTarget | string | `"FILE"` | oxauth_script.log target |
| global.oxauth.enabled | bool | `true` | Boolean flag to enable/disable oxauth chart. You should never set this to false. |
| global.oxauth.gluuCustomJavaOptions | string | `""` | passing custom  java options to oxauth. Notice you do not need to pass in any loggers options as they are introduced below in appLoggers. DO NOT PASS GLUU_JAVA_OPTIONS in envs. |
| global.oxd-server.appLoggers | object | `{"oxdServerLogLevel":"INFO","oxdServerLogTarget":"STDOUT"}` | App loggers can be configured to define where the logs will be redirected to and the level of each in which it should be displayed. log levels are "OFF", "FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE" Targets are "STDOUT" and "FILE" |
| global.oxd-server.appLoggers.oxdServerLogLevel | string | `"INFO"` | oxd-server.log level |
| global.oxd-server.appLoggers.oxdServerLogTarget | string | `"STDOUT"` | oxd-server.log target |
| global.oxd-server.enabled | bool | `true` | Boolean flag to enable/disable the oxd-server chart. |
| global.oxd-server.gluuCustomJavaOptions | string | `""` | passing custom  java options to oxShibboleth. Notice you do not need to pass in any loggers options as they are introduced below in appLoggers. DO NOT PASS GLUU_JAVA_OPTIONS in envs. |
| global.oxshibboleth.appLoggers | object | `{"auditStatsLogLevel":"INFO","auditStatsLogTarget":"FILE","consentAuditLogLevel":"INFO","consentAuditLogTarget":"FILE","containerLogLevel":"","enableStdoutLogPrefix":"true","encryptionLogLevel":"","httpclientLogLevel":"","idpLogLevel":"INFO","idpLogTarget":"STDOUT","ldapLogLevel":"","messagesLogLevel":"","opensamlLogLevel":"","propsLogLevel":"","scriptLogLevel":"INFO","scriptLogTarget":"FILE","springLogLevel":"","xmlsecLogLevel":""}` | App loggers can be configured to define where the logs will be redirected to and the level of each in which it should be displayed. log levels are "OFF", "FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE" Targets are "STDOUT" and "FILE" |
| global.oxshibboleth.appLoggers.auditStatsLogLevel | string | `"INFO"` | idp-audit.log level |
| global.oxshibboleth.appLoggers.auditStatsLogTarget | string | `"FILE"` | idp-audit.log target |
| global.oxshibboleth.appLoggers.consentAuditLogLevel | string | `"INFO"` | idp-consent-audit.log level |
| global.oxshibboleth.appLoggers.consentAuditLogTarget | string | `"FILE"` | idp-consent-audit.log target |
| global.oxshibboleth.appLoggers.enableStdoutLogPrefix | string | `"true"` | Enable log prefixing which enables prepending the STDOUT logs with the file name. i.e idp-script ===> 2022-12-20 17:49:55,744 INFO |
| global.oxshibboleth.appLoggers.idpLogLevel | string | `"INFO"` | idp-process.log level |
| global.oxshibboleth.appLoggers.idpLogTarget | string | `"STDOUT"` | idp-process.log target |
| global.oxshibboleth.appLoggers.ldapLogLevel | string | `""` | https://github.com/GluuFederation/docker-oxshibboleth#additional-logger-configuration The below are very noisy logs and are better left untouched |
| global.oxshibboleth.appLoggers.scriptLogLevel | string | `"INFO"` | idp-script.log level |
| global.oxshibboleth.appLoggers.scriptLogTarget | string | `"FILE"` | idp-script.log target |
| global.oxshibboleth.enabled | bool | `false` | Boolean flag to enable/disable the oxShibbboleth chart. |
| global.oxshibboleth.gluuCustomJavaOptions | string | `""` | passing custom  java options to oxShibboleth. Notice you do not need to pass in any loggers options as they are introduced below in appLoggers. DO NOT PASS GLUU_JAVA_OPTIONS in envs. |
| global.oxtrust.appLoggers | object | `{"apachehcLogLevel":"INFO","apachehcLogTarget":"FILE","auditStatsLogLevel":"INFO","auditStatsLogTarget":"FILE","cacheRefreshLogLevel":"INFO","cacheRefreshLogTarget":"FILE","cacheRefreshPythonLogLevel":"INFO","cacheRefreshPythonLogTarget":"FILE","cleanerLogLevel":"INFO","cleanerLogTarget":"FILE","enableStdoutLogPrefix":"true","httpLogLevel":"INFO","httpLogTarget":"FILE","ldapStatsLogLevel":"INFO","ldapStatsLogTarget":"FILE","oxtrustLogLevel":"INFO","oxtrustLogTarget":"STDOUT","persistenceDurationLogLevel":"INFO","persistenceDurationLogTarget":"FILE","persistenceLogLevel":"INFO","persistenceLogTarget":"FILE","scriptLogLevel":"INFO","scriptLogTarget":"FILE","velocityLogLevel":"INFO","velocityLogTarget":"FILE"}` | App loggers can be configured to define where the logs will be redirected to and the level of each in which it should be displayed. log levels are "OFF", "FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE" Targets are "STDOUT" and "FILE" |
| global.oxtrust.appLoggers.apachehcLogLevel | string | `"INFO"` | apachehc log level |
| global.oxtrust.appLoggers.apachehcLogTarget | string | `"FILE"` | apachehc log target |
| global.oxtrust.appLoggers.auditStatsLogLevel | string | `"INFO"` | oxtrust_audit.log level |
| global.oxtrust.appLoggers.auditStatsLogTarget | string | `"FILE"` | oxtrust_script.log target |
| global.oxtrust.appLoggers.cacheRefreshLogLevel | string | `"INFO"` | cache refresh log level |
| global.oxtrust.appLoggers.cacheRefreshLogTarget | string | `"FILE"` | cache refresh log target |
| global.oxtrust.appLoggers.cacheRefreshPythonLogLevel | string | `"INFO"` | cleaner log level |
| global.oxtrust.appLoggers.cacheRefreshPythonLogTarget | string | `"FILE"` | cache refresh python log target |
| global.oxtrust.appLoggers.cleanerLogLevel | string | `"INFO"` | cleaner log target |
| global.oxtrust.appLoggers.cleanerLogTarget | string | `"FILE"` | cleaner log target |
| global.oxtrust.appLoggers.enableStdoutLogPrefix | string | `"true"` | Enable log prefixing which enables prepending the STDOUT logs with the file name. i.e oxtrust-script ===> 2022-12-20 17:49:55,744 INFO |
| global.oxtrust.appLoggers.httpLogLevel | string | `"INFO"` | http_request_response.log level |
| global.oxtrust.appLoggers.httpLogTarget | string | `"FILE"` | http_request_response.log target |
| global.oxtrust.appLoggers.ldapStatsLogLevel | string | `"INFO"` | oxtrust_persistence_ldap_statistics.log level |
| global.oxtrust.appLoggers.ldapStatsLogTarget | string | `"FILE"` | oxtrust_persistence_ldap_statistics.log target |
| global.oxtrust.appLoggers.oxtrustLogLevel | string | `"INFO"` | oxtrust.log level |
| global.oxtrust.appLoggers.oxtrustLogTarget | string | `"STDOUT"` | oxtrust.log target |
| global.oxtrust.appLoggers.persistenceDurationLogLevel | string | `"INFO"` | oxtrust_persistence_duration.log level |
| global.oxtrust.appLoggers.persistenceDurationLogTarget | string | `"FILE"` | oxtrust_persistence_duration.log target |
| global.oxtrust.appLoggers.persistenceLogLevel | string | `"INFO"` | oxtrust_persistence.log level |
| global.oxtrust.appLoggers.persistenceLogTarget | string | `"FILE"` | oxtrust_persistence.log target |
| global.oxtrust.appLoggers.scriptLogLevel | string | `"INFO"` | oxtrust_script.log level |
| global.oxtrust.appLoggers.scriptLogTarget | string | `"FILE"` | oxtrust_script.log target |
| global.oxtrust.appLoggers.velocityLogLevel | string | `"INFO"` | velocity log level |
| global.oxtrust.appLoggers.velocityLogTarget | string | `"FILE"` | velocity log target |
| global.oxtrust.enabled | bool | `true` | Boolean flag to enable/disable the oxtrust chart. |
| global.oxtrust.gluuCustomJavaOptions | string | `"-XshowSettings:vm -XX:MaxRAMPercentage=80"` | passing custom  java options to oxTrust. Notice you do not need to pass in any loggers options as they are introduced below in appLoggers. DO NOT PASS GLUU_JAVA_OPTIONS in envs. |
| global.persistence.enabled | bool | `true` | Boolean flag to enable/disable the persistence chart. |
| global.scim.appLoggers | object | `{"enableStdoutLogPrefix":"true","persistenceDurationLogLevel":"INFO","persistenceDurationLogTarget":"FILE","persistenceLogLevel":"INFO","persistenceLogTarget":"FILE","scimLogLevel":"INFO","scimLogTarget":"STDOUT","scriptLogLevel":"INFO","scriptLogTarget":"FILE"}` | App loggers can be configured to define where the logs will be redirected to and the level of each in which it should be displayed. log levels are "OFF", "FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE" Targets are "STDOUT" and "FILE" |
| global.scim.appLoggers.enableStdoutLogPrefix | string | `"true"` | Enable log prefixing which enables prepending the STDOUT logs with the file name. i.e scim-script ===> 2022-12-20 17:49:55,744 INFO |
| global.scim.appLoggers.persistenceDurationLogLevel | string | `"INFO"` | scim_persistence_duration.log level |
| global.scim.appLoggers.persistenceDurationLogTarget | string | `"FILE"` | scim_persistence_duration.log target |
| global.scim.appLoggers.persistenceLogLevel | string | `"INFO"` | scim_persistence.log level |
| global.scim.appLoggers.persistenceLogTarget | string | `"FILE"` | scim_persistence.log target |
| global.scim.appLoggers.scimLogLevel | string | `"INFO"` | scim.log level |
| global.scim.appLoggers.scimLogTarget | string | `"STDOUT"` | scim.log target |
| global.scim.appLoggers.scriptLogLevel | string | `"INFO"` | scim_script.log level |
| global.scim.appLoggers.scriptLogTarget | string | `"FILE"` | scim_script.log target |
| global.scim.enabled | bool | `false` | Boolean flag to enable/disable the SCIM chart. |
| global.scim.gluuCustomJavaOptions | string | `""` | passing custom  java options to scim. Notice you do not need to pass in any loggers options as they are introduced below in appLoggers. DO NOT PASS GLUU_JAVA_OPTIONS in envs. |
| global.sslCertFromDomain | string | `"false"` | Validate certificate is downloaded from given domain. If set to true (default to false), raise an error if cert is not downloaded. Note that the flag is ignored if mounted SSL cert and key files exist |
| global.storageClass | object | `{"allowVolumeExpansion":true,"allowedTopologies":[],"mountOptions":["debug"],"parameters":{},"provisioner":"microk8s.io/hostpath","reclaimPolicy":"Retain","volumeBindingMode":"WaitForFirstConsumer"}` | StorageClass section for Jackrabbit and OpenDJ charts. This is not currently used by the openbanking distribution. You may specify custom parameters as needed. |
| global.storageClass.parameters | object | `{}` | parameters: fsType: "" kind: "" pool: "" storageAccountType: "" type: "" |
| global.upgrade.enabled | bool | `false` | Boolean flag used when running upgrading through versions command. |
| global.upgrade.image.repository | string | `"gluufederation/upgrade"` | Image  to use for deploying. |
| global.upgrade.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| global.upgrade.sourceVersion | string | `"4.5"` | Source version currently running. This is normally one minor version down. The step should only be one minor version per upgrade |
| global.upgrade.targetVersion | string | `"4.5"` | Target version currently running. This is normally one minor version up. The step should only be one minor version per upgrade |
| global.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service. Envs defined in global.userEnvs will be globally available to all services |
| global.usrEnvs.normal | object | `{}` | Add custom normal envs to the service. variable1: value1 |
| global.usrEnvs.secret | object | `{}` | Add custom secret envs to the service. variable1: value1 |
| jackrabbit | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"clusterId":"","customScripts":[],"dnsConfig":{},"dnsPolicy":"","hpa":{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50},"image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/jackrabbit","tag":"4.5.5-1"},"lifecycle":{},"livenessProbe":{"initialDelaySeconds":25,"periodSeconds":25,"tcpSocket":{"port":"http-jackrabbit"},"timeoutSeconds":5},"nodeSelector":{},"pdb":{"enabled":true,"maxUnavailable":1},"readinessProbe":{"initialDelaySeconds":30,"periodSeconds":30,"tcpSocket":{"port":"http-jackrabbit"},"timeoutSeconds":5},"replicas":1,"resources":{"limits":{"cpu":"1500m","memory":"1000Mi"},"requests":{"cpu":"1500m","memory":"1000Mi"}},"secrets":{"gluuJackrabbitAdminPass":"Test1234#","gluuJackrabbitPostgresPass":"P@ssw0rd"},"service":{"jackRabbitServiceName":"jackrabbit","name":"http-jackrabbit","port":8080},"storage":{"size":"5Gi"},"tolerations":[],"topologySpreadConstraints":{},"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | Jackrabbit Oak is a complementary implementation of the JCR specification. It is an effort to implement a scalable and performant hierarchical content repository for use as the foundation of modern world-class web sites and other demanding content applications https://jackrabbit.apache.org/jcr/index.html |
| jackrabbit.additionalAnnotations | object | `{}` | Additional annotations that will be added across the gateway in the format of {cert-manager.io/issuer: "letsencrypt-prod"} |
| jackrabbit.additionalLabels | object | `{}` | Additional labels that will be added across the gateway in the format of {mylabel: "myapp"} |
| jackrabbit.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| jackrabbit.clusterId | string | `""` | This id needs to be unique to each kubernetes cluster in a multi cluster setup west, east, south, north, region ...etc If left empty it will be randomly generated. |
| jackrabbit.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| jackrabbit.dnsConfig | object | `{}` | Add custom dns config |
| jackrabbit.dnsPolicy | string | `""` | Add custom dns policy |
| jackrabbit.hpa | object | `{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50}` | Configure the HorizontalPodAutoscaler |
| jackrabbit.hpa.behavior | object | `{}` | Scaling Policies |
| jackrabbit.hpa.metrics | list | `[]` | metrics if targetCPUUtilizationPercentage is not set |
| jackrabbit.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| jackrabbit.image.pullSecrets | list | `[]` | Image Pull Secrets |
| jackrabbit.image.repository | string | `"gluufederation/jackrabbit"` | Image  to use for deploying. |
| jackrabbit.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| jackrabbit.livenessProbe | object | `{"initialDelaySeconds":25,"periodSeconds":25,"tcpSocket":{"port":"http-jackrabbit"},"timeoutSeconds":5}` | Configure the liveness healthcheck for the Jackrabbit if needed. |
| jackrabbit.livenessProbe.tcpSocket | object | `{"port":"http-jackrabbit"}` | Executes tcp healthcheck. |
| jackrabbit.pdb | object | `{"enabled":true,"maxUnavailable":1}` | Configure the PodDisruptionBudget |
| jackrabbit.readinessProbe | object | `{"initialDelaySeconds":30,"periodSeconds":30,"tcpSocket":{"port":"http-jackrabbit"},"timeoutSeconds":5}` | Configure the readiness healthcheck for the Jackrabbit if needed. |
| jackrabbit.readinessProbe.tcpSocket | object | `{"port":"http-jackrabbit"}` | Executes tcp healthcheck. |
| jackrabbit.replicas | int | `1` | Service replica number. |
| jackrabbit.resources | object | `{"limits":{"cpu":"1500m","memory":"1000Mi"},"requests":{"cpu":"1500m","memory":"1000Mi"}}` | Resource specs. |
| jackrabbit.resources.limits.cpu | string | `"1500m"` | CPU limit. |
| jackrabbit.resources.limits.memory | string | `"1000Mi"` | Memory limit. |
| jackrabbit.resources.requests.cpu | string | `"1500m"` | CPU request. |
| jackrabbit.resources.requests.memory | string | `"1000Mi"` | Memory request. |
| jackrabbit.secrets.gluuJackrabbitAdminPass | string | `"Test1234#"` | Jackrabbit admin uid password |
| jackrabbit.secrets.gluuJackrabbitPostgresPass | string | `"P@ssw0rd"` | Jackrabbit Postgres uid password |
| jackrabbit.service.jackRabbitServiceName | string | `"jackrabbit"` | Name of the Jackrabbit service. Please keep it as default. |
| jackrabbit.service.name | string | `"http-jackrabbit"` | The name of the jackrabbit port within the jackrabbit service. Please keep it as default. |
| jackrabbit.service.port | int | `8080` | Port of the jackrabbit service. Please keep it as default. |
| jackrabbit.storage.size | string | `"5Gi"` | Jackrabbit volume size |
| jackrabbit.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| jackrabbit.topologySpreadConstraints | object | `{}` | Configure the topology spread constraints. Notice this is a map NOT a list as in the upstream API https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ |
| jackrabbit.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| jackrabbit.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| jackrabbit.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| jackrabbit.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| jackrabbit.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| nginx-ingress | object | `{"certManager":{"certificate":{"enabled":false,"issuerGroup":"cert-manager.io","issuerKind":"ClusterIssuer","issuerName":""}},"ingress":{"additionalAnnotations":{},"additionalLabels":{},"adminUiAdditionalAnnotations":{},"adminUiEnabled":true,"adminUiLabels":{},"authServerAdditionalAnnotations":{},"authServerEnabled":true,"authServerLabels":{},"casaAdditionalAnnotations":{},"casaEnabled":false,"casaLabels":{},"deviceCodeAdditionalAnnotations":{},"deviceCodeEnabled":true,"deviceCodeLabels":{},"enabled":true,"fido2ConfigAdditionalAnnotations":{},"fido2ConfigEnabled":false,"fido2ConfigLabels":{},"fido2Enabled":false,"fido2Labels":{},"firebaseMessagingAdditionalAnnotations":{},"firebaseMessagingEnabled":true,"firebaseMessagingLabels":{},"hosts":["demoexample.gluu.org"],"ingressClassName":"nginx","legacy":false,"openidAdditionalAnnotations":{},"openidConfigEnabled":true,"openidConfigLabels":{},"passportAdditionalAnnotations":{},"passportEnabled":false,"passportLabels":{},"path":"/","scimAdditionalAnnotations":{},"scimConfigAdditionalAnnotations":{},"scimConfigEnabled":false,"scimConfigLabels":{},"scimEnabled":false,"scimLabels":{},"shibAdditionalAnnotations":{},"shibEnabled":false,"shibLabels":{},"tls":[{"hosts":["demoexample.gluu.org"],"secretName":"tls-certificate"}],"u2fAdditionalAnnotations":{},"u2fConfigEnabled":true,"u2fConfigLabels":{},"uma2AdditionalAnnotations":{},"uma2ConfigEnabled":true,"uma2ConfigLabels":{},"webdiscoveryAdditionalAnnotations":{},"webdiscoveryEnabled":true,"webdiscoveryLabels":{},"webfingerAdditionalAnnotations":{},"webfingerEnabled":true,"webfingerLabels":{}}}` | Nginx ingress definitions chart |
| nginx-ingress.ingress.additionalAnnotations | object | `{}` | Additional annotations that will be added across all ingress definitions in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken Enable client certificate authentication nginx.ingress.kubernetes.io/auth-tls-verify-client: "optional" Create the secret containing the trusted ca certificates nginx.ingress.kubernetes.io/auth-tls-secret: "gluu/tls-certificate" Specify the verification depth in the client certificates chain nginx.ingress.kubernetes.io/auth-tls-verify-depth: "1" Specify if certificates are passed to upstream server nginx.ingress.kubernetes.io/auth-tls-pass-certificate-to-upstream: "true" |
| nginx-ingress.ingress.additionalLabels | object | `{}` | Additional labels that will be added across all ingress definitions in the format of {mylabel: "myapp"} |
| nginx-ingress.ingress.adminUiAdditionalAnnotations | object | `{}` | Admin UI ingress resource additional annotations. |
| nginx-ingress.ingress.adminUiEnabled | bool | `true` | Enable Admin UI endpoints /identity |
| nginx-ingress.ingress.adminUiLabels | object | `{}` | Admin UI ingress resource labels. key app is taken. |
| nginx-ingress.ingress.authServerAdditionalAnnotations | object | `{}` | Auth server ingress resource additional annotations. |
| nginx-ingress.ingress.authServerEnabled | bool | `true` | Enable Auth server endpoints /oxauth |
| nginx-ingress.ingress.authServerLabels | object | `{}` | Auth server config ingress resource labels. key app is taken |
| nginx-ingress.ingress.casaAdditionalAnnotations | object | `{}` | Casa ingress resource additional annotations. |
| nginx-ingress.ingress.casaEnabled | bool | `false` | Enable casa endpoints /casa |
| nginx-ingress.ingress.casaLabels | object | `{}` | Casa ingress resource labels. key app is taken |
| nginx-ingress.ingress.deviceCodeAdditionalAnnotations | object | `{}` | device-code ingress resource additional annotations. |
| nginx-ingress.ingress.deviceCodeEnabled | bool | `true` | Enable endpoint /device-code |
| nginx-ingress.ingress.deviceCodeLabels | object | `{}` | device-code ingress resource labels. key app is taken |
| nginx-ingress.ingress.fido2ConfigAdditionalAnnotations | object | `{}` | fido2 config ingress resource additional annotations. |
| nginx-ingress.ingress.fido2ConfigEnabled | bool | `false` | Enable endpoint /.well-known/fido2-configuration |
| nginx-ingress.ingress.fido2ConfigLabels | object | `{}` | fido2 config ingress resource labels. key app is taken |
| nginx-ingress.ingress.fido2Enabled | bool | `false` | Enable all fido2 endpoints |
| nginx-ingress.ingress.fido2Labels | object | `{}` | fido2 ingress resource labels. key app is taken |
| nginx-ingress.ingress.firebaseMessagingAdditionalAnnotations | object | `{}` | Firebase Messaging ingress resource additional annotations. |
| nginx-ingress.ingress.firebaseMessagingEnabled | bool | `true` | Enable endpoint /firebase-messaging-sw.js |
| nginx-ingress.ingress.firebaseMessagingLabels | object | `{}` | Firebase Messaging ingress resource labels. key app is taken |
| nginx-ingress.ingress.legacy | bool | `false` | Enable use of legacy API version networking.k8s.io/v1beta1 to support kubernetes 1.18. This flag should be removed next version release along with nginx-ingress/templates/ingress-legacy.yaml. |
| nginx-ingress.ingress.openidAdditionalAnnotations | object | `{}` | openid-configuration ingress resource additional annotations. |
| nginx-ingress.ingress.openidConfigEnabled | bool | `true` | Enable endpoint /.well-known/openid-configuration |
| nginx-ingress.ingress.openidConfigLabels | object | `{}` | openid-configuration ingress resource labels. key app is taken |
| nginx-ingress.ingress.passportAdditionalAnnotations | object | `{}` | passport ingress resource additional annotations. |
| nginx-ingress.ingress.passportEnabled | bool | `false` | Enable passport endpoints /idp |
| nginx-ingress.ingress.passportLabels | object | `{}` | passport ingress resource labels. key app is taken. |
| nginx-ingress.ingress.scimAdditionalAnnotations | object | `{}` | SCIM ingress resource additional annotations. |
| nginx-ingress.ingress.scimConfigAdditionalAnnotations | object | `{}` | SCIM config ingress resource additional annotations. |
| nginx-ingress.ingress.scimConfigEnabled | bool | `false` | Enable endpoint /.well-known/scim-configuration |
| nginx-ingress.ingress.scimConfigLabels | object | `{}` | webdiscovery ingress resource labels. key app is taken |
| nginx-ingress.ingress.scimEnabled | bool | `false` | Enable SCIM endpoints /scim |
| nginx-ingress.ingress.scimLabels | object | `{}` | scim config ingress resource labels. key app is taken |
| nginx-ingress.ingress.shibAdditionalAnnotations | object | `{}` | shibboleth ingress resource additional annotations. |
| nginx-ingress.ingress.shibEnabled | bool | `false` | Enable shibboleth endpoints /idp |
| nginx-ingress.ingress.shibLabels | object | `{}` | shibboleth ingress resource labels. key app is taken. |
| nginx-ingress.ingress.u2fAdditionalAnnotations | object | `{}` | u2f config ingress resource additional annotations. |
| nginx-ingress.ingress.u2fConfigEnabled | bool | `true` | Enable endpoint /.well-known/fido-configuration |
| nginx-ingress.ingress.u2fConfigLabels | object | `{}` | u2f config ingress resource labels. key app is taken |
| nginx-ingress.ingress.uma2AdditionalAnnotations | object | `{}` | uma2 config ingress resource additional annotations. |
| nginx-ingress.ingress.uma2ConfigEnabled | bool | `true` | Enable endpoint /.well-known/uma2-configuration |
| nginx-ingress.ingress.uma2ConfigLabels | object | `{}` | uma 2 config ingress resource labels. key app is taken |
| nginx-ingress.ingress.webdiscoveryAdditionalAnnotations | object | `{}` | webdiscovery ingress resource additional annotations. |
| nginx-ingress.ingress.webdiscoveryEnabled | bool | `true` | Enable endpoint /.well-known/simple-web-discovery |
| nginx-ingress.ingress.webdiscoveryLabels | object | `{}` | webdiscovery ingress resource labels. key app is taken |
| nginx-ingress.ingress.webfingerAdditionalAnnotations | object | `{}` | webfinger ingress resource additional annotations. |
| nginx-ingress.ingress.webfingerEnabled | bool | `true` | Enable endpoint /.well-known/webfinger |
| nginx-ingress.ingress.webfingerLabels | object | `{}` | webfinger ingress resource labels. key app is taken |
| opendj | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"backup":{"cronJobSchedule":"*/59 * * * *","enabled":true},"customScripts":[],"dnsConfig":{},"dnsPolicy":"","hpa":{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50},"image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/opendj","tag":"4.5.5-1"},"lifecycle":{"preStop":{"exec":{"command":["/bin/sh","-c","python3 /app/scripts/deregister_peer.py 1>&/proc/1/fd/1"]}}},"livenessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"failureThreshold":20,"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5},"nodeSelector":{},"pdb":{"enabled":true,"maxUnavailable":1},"persistence":{"size":"5Gi"},"ports":{"tcp-admin":{"nodePort":"","port":4444,"protocol":"TCP","targetPort":4444},"tcp-ldap":{"nodePort":"","port":1389,"protocol":"TCP","targetPort":1389},"tcp-ldaps":{"nodePort":"","port":1636,"protocol":"TCP","targetPort":1636},"tcp-repl":{"nodePort":"","port":8989,"protocol":"TCP","targetPort":8989},"tcp-serf":{"nodePort":"","port":7946,"protocol":"TCP","targetPort":7946},"udp-serf":{"nodePort":"","port":7946,"protocol":"UDP","targetPort":7946}},"readinessProbe":{"failureThreshold":20,"initialDelaySeconds":60,"periodSeconds":25,"tcpSocket":{"port":1636},"timeoutSeconds":5},"replicas":1,"resources":{"limits":{"cpu":"1500m","memory":"2000Mi"},"requests":{"cpu":"1500m","memory":"2000Mi"}},"tolerations":[],"topologySpreadConstraints":{},"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | OpenDJ is a directory server which implements a wide range of Lightweight Directory Access Protocol and related standards, including full compliance with LDAPv3 but also support for Directory Service Markup Language (DSMLv2).Written in Java, OpenDJ offers multi-master replication, access control, and many extensions. |
| opendj.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| opendj.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| opendj.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| opendj.backup | object | `{"cronJobSchedule":"*/59 * * * *","enabled":true}` | Configure ldap backup cronjob |
| opendj.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| opendj.dnsConfig | object | `{}` | Add custom dns config |
| opendj.dnsPolicy | string | `""` | Add custom dns policy |
| opendj.hpa | object | `{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50}` | Configure the HorizontalPodAutoscaler |
| opendj.hpa.behavior | object | `{}` | Scaling Policies |
| opendj.hpa.metrics | list | `[]` | metrics if targetCPUUtilizationPercentage is not set |
| opendj.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| opendj.image.pullSecrets | list | `[]` | Image Pull Secrets |
| opendj.image.repository | string | `"gluufederation/opendj"` | Image  to use for deploying. |
| opendj.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| opendj.livenessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"failureThreshold":20,"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5}` | Configure the liveness healthcheck for OpenDJ if needed. |
| opendj.livenessProbe.exec | object | `{"command":["python3","/app/scripts/healthcheck.py"]}` | Executes the python3 healthcheck. |
| opendj.pdb | object | `{"enabled":true,"maxUnavailable":1}` | Configure the PodDisruptionBudget |
| opendj.persistence.size | string | `"5Gi"` | OpenDJ volume size |
| opendj.ports | object | `{"tcp-admin":{"nodePort":"","port":4444,"protocol":"TCP","targetPort":4444},"tcp-ldap":{"nodePort":"","port":1389,"protocol":"TCP","targetPort":1389},"tcp-ldaps":{"nodePort":"","port":1636,"protocol":"TCP","targetPort":1636},"tcp-repl":{"nodePort":"","port":8989,"protocol":"TCP","targetPort":8989},"tcp-serf":{"nodePort":"","port":7946,"protocol":"TCP","targetPort":7946},"udp-serf":{"nodePort":"","port":7946,"protocol":"UDP","targetPort":7946}}` | servicePorts values used in StatefulSet container |
| opendj.readinessProbe | object | `{"failureThreshold":20,"initialDelaySeconds":60,"periodSeconds":25,"tcpSocket":{"port":1636},"timeoutSeconds":5}` | Configure the readiness healthcheck for OpenDJ if needed. |
| opendj.replicas | int | `1` | Service replica number. |
| opendj.resources | object | `{"limits":{"cpu":"1500m","memory":"2000Mi"},"requests":{"cpu":"1500m","memory":"2000Mi"}}` | Resource specs. |
| opendj.resources.limits.cpu | string | `"1500m"` | CPU limit. |
| opendj.resources.limits.memory | string | `"2000Mi"` | Memory limit. |
| opendj.resources.requests.cpu | string | `"1500m"` | CPU request. |
| opendj.resources.requests.memory | string | `"2000Mi"` | Memory request. |
| opendj.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| opendj.topologySpreadConstraints | object | `{}` | Configure the topology spread constraints. Notice this is a map NOT a list as in the upstream API https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ |
| opendj.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| opendj.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| opendj.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| opendj.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| opendj.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| oxauth | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"customScripts":[],"dnsConfig":{},"dnsPolicy":"","hpa":{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50},"image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/oxauth","tag":"4.5.5-1"},"lifecycle":{},"livenessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5},"nodeSelector":{},"pdb":{"enabled":true,"maxUnavailable":"90%"},"readinessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5},"replicas":1,"resources":{"limits":{"cpu":"2500m","memory":"2500Mi"},"requests":{"cpu":"2500m","memory":"2500Mi"}},"service":{"name":"http-oxauth","oxAuthServiceName":"oxauth","port":8080},"tolerations":[],"topologySpreadConstraints":{},"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | OAuth Authorization Server, the OpenID Connect Provider, the UMA Authorization Server--this is the main Internet facing component of Gluu. It's the service that returns tokens, JWT's and identity assertions. This service must be Internet facing. |
| oxauth-key-rotation | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"cronJobSchedule":"","customScripts":[],"dnsConfig":{},"dnsPolicy":"","image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/certmanager","tag":"4.5.5-1"},"keysLife":48,"keysPushDelay":0,"keysPushStrategy":"NEWER","keysStrategy":"NEWER","lifecycle":{},"nodeSelector":{},"resources":{"limits":{"cpu":"300m","memory":"300Mi"},"requests":{"cpu":"300m","memory":"300Mi"}},"tolerations":[],"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | Responsible for regenerating auth-keys per x hours |
| oxauth-key-rotation.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| oxauth-key-rotation.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| oxauth-key-rotation.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| oxauth-key-rotation.cronJobSchedule | string | `""` | Auth server key rotation job schedule. It accepts any Cron syntax supported by Kubernetes. If empty, the schedule will run based on keysLife value. |
| oxauth-key-rotation.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| oxauth-key-rotation.dnsConfig | object | `{}` | Add custom dns config |
| oxauth-key-rotation.dnsPolicy | string | `""` | Add custom dns policy |
| oxauth-key-rotation.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| oxauth-key-rotation.image.pullSecrets | list | `[]` | Image Pull Secrets |
| oxauth-key-rotation.image.repository | string | `"gluufederation/certmanager"` | Image  to use for deploying. |
| oxauth-key-rotation.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| oxauth-key-rotation.keysLife | int | `48` | Auth server key rotation keys life in hours. |
| oxauth-key-rotation.keysPushDelay | int | `0` | Delay (in seconds) before pushing private keys to Auth server |
| oxauth-key-rotation.keysPushStrategy | string | `"NEWER"` | Set key selection strategy after pushing private keys to Auth server (only takes effect when keysPushDelay value is greater than 0) |
| oxauth-key-rotation.keysStrategy | string | `"NEWER"` | Set key selection strategy used by Auth server |
| oxauth-key-rotation.resources | object | `{"limits":{"cpu":"300m","memory":"300Mi"},"requests":{"cpu":"300m","memory":"300Mi"}}` | Resource specs. |
| oxauth-key-rotation.resources.limits.cpu | string | `"300m"` | CPU limit. |
| oxauth-key-rotation.resources.limits.memory | string | `"300Mi"` | Memory limit. |
| oxauth-key-rotation.resources.requests.cpu | string | `"300m"` | CPU request. |
| oxauth-key-rotation.resources.requests.memory | string | `"300Mi"` | Memory request. |
| oxauth-key-rotation.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| oxauth-key-rotation.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| oxauth-key-rotation.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| oxauth-key-rotation.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| oxauth-key-rotation.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| oxauth-key-rotation.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| oxauth.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| oxauth.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| oxauth.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| oxauth.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| oxauth.dnsConfig | object | `{}` | Add custom dns config |
| oxauth.dnsPolicy | string | `""` | Add custom dns policy |
| oxauth.hpa | object | `{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50}` | Configure the HorizontalPodAutoscaler |
| oxauth.hpa.behavior | object | `{}` | Scaling Policies |
| oxauth.hpa.metrics | list | `[]` | metrics if targetCPUUtilizationPercentage is not set |
| oxauth.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| oxauth.image.pullSecrets | list | `[]` | Image Pull Secrets |
| oxauth.image.repository | string | `"gluufederation/oxauth"` | Image  to use for deploying. |
| oxauth.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| oxauth.livenessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5}` | Configure the liveness healthcheck for the auth server if needed. |
| oxauth.livenessProbe.exec | object | `{"command":["python3","/app/scripts/healthcheck.py"]}` | Executes the python3 healthcheck. |
| oxauth.pdb | object | `{"enabled":true,"maxUnavailable":"90%"}` | Configure the PodDisruptionBudget |
| oxauth.readinessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5}` | Configure the readiness healthcheck for the auth server if needed. |
| oxauth.replicas | int | `1` | Service replica number. |
| oxauth.resources | object | `{"limits":{"cpu":"2500m","memory":"2500Mi"},"requests":{"cpu":"2500m","memory":"2500Mi"}}` | Resource specs. |
| oxauth.resources.limits.cpu | string | `"2500m"` | CPU limit. |
| oxauth.resources.limits.memory | string | `"2500Mi"` | Memory limit. This value is used to calculate memory allocation for Java. Currently it only supports `Mi`. Please refrain from using other units. |
| oxauth.resources.requests.cpu | string | `"2500m"` | CPU request. |
| oxauth.resources.requests.memory | string | `"2500Mi"` | Memory request. |
| oxauth.service.name | string | `"http-oxauth"` | The name of the oxauth port within the oxauth service. Please keep it as default. |
| oxauth.service.oxAuthServiceName | string | `"oxauth"` | Name of the oxauth service. Please keep it as default. |
| oxauth.service.port | int | `8080` | Port of the oxauth service. Please keep it as default. |
| oxauth.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| oxauth.topologySpreadConstraints | object | `{}` | Configure the topology spread constraints. Notice this is a map NOT a list as in the upstream API https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ |
| oxauth.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| oxauth.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| oxauth.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| oxauth.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| oxauth.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| oxd-server | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"customScripts":[],"dnsConfig":{},"dnsPolicy":"","hpa":{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50},"image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/oxd-server","tag":"4.5.5-1"},"lifecycle":{},"livenessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5},"nodeSelector":{},"pdb":{"enabled":true,"maxUnavailable":"90%"},"readinessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5},"replicas":1,"resources":{"limits":{"cpu":"1000m","memory":"400Mi"},"requests":{"cpu":"1000m","memory":"400Mi"}},"service":{"oxdServerServiceName":"oxd-server"},"tolerations":[],"topologySpreadConstraints":{},"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | Middleware API to help application developers call an OAuth, OpenID or UMA server. You may wonder why this is necessary. It makes it easier for client developers to use OpenID signing and encryption features, without becoming crypto experts. This API provides some high level endpoints to do some of the heavy lifting. |
| oxd-server.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| oxd-server.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| oxd-server.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| oxd-server.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| oxd-server.dnsConfig | object | `{}` | Add custom dns config |
| oxd-server.dnsPolicy | string | `""` | Add custom dns policy |
| oxd-server.hpa | object | `{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50}` | Configure the HorizontalPodAutoscaler |
| oxd-server.hpa.behavior | object | `{}` | Scaling Policies |
| oxd-server.hpa.metrics | list | `[]` | metrics if targetCPUUtilizationPercentage is not set |
| oxd-server.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| oxd-server.image.pullSecrets | list | `[]` | Image Pull Secrets |
| oxd-server.image.repository | string | `"gluufederation/oxd-server"` | Image  to use for deploying. |
| oxd-server.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| oxd-server.livenessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5}` | Configure the liveness healthcheck for the auth server if needed. |
| oxd-server.livenessProbe.exec | object | `{"command":["python3","/app/scripts/healthcheck.py"]}` | Executes the python3 healthcheck. |
| oxd-server.pdb | object | `{"enabled":true,"maxUnavailable":"90%"}` | Configure the PodDisruptionBudget |
| oxd-server.readinessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5}` | Configure the readiness healthcheck for the auth server if needed. |
| oxd-server.replicas | int | `1` | Service replica number. |
| oxd-server.resources | object | `{"limits":{"cpu":"1000m","memory":"400Mi"},"requests":{"cpu":"1000m","memory":"400Mi"}}` | Resource specs. |
| oxd-server.resources.limits.cpu | string | `"1000m"` | CPU limit. |
| oxd-server.resources.limits.memory | string | `"400Mi"` | Memory limit. This value is used to calculate memory allocation for Java. Currently it only supports `Mi`. Please refrain from using other units. |
| oxd-server.resources.requests.cpu | string | `"1000m"` | CPU request. |
| oxd-server.resources.requests.memory | string | `"400Mi"` | Memory request. |
| oxd-server.service.oxdServerServiceName | string | `"oxd-server"` | Name of the OXD server service. This must match config.configMap.gluuOxdApplicationCertCn. Please keep it as default. |
| oxd-server.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| oxd-server.topologySpreadConstraints | object | `{}` | Configure the topology spread constraints. Notice this is a map NOT a list as in the upstream API https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ |
| oxd-server.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| oxd-server.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| oxd-server.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| oxd-server.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| oxd-server.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| oxpassport | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"customScripts":[],"dnsConfig":{},"dnsPolicy":"","hpa":{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50},"image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/oxpassport","tag":"4.5.5-2"},"istioDestinationRuleCookieTTL":"60s","lifecycle":{},"livenessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"failureThreshold":20,"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5},"nodeSelector":{},"pdb":{"enabled":true,"maxUnavailable":"90%"},"readinessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"failureThreshold":20,"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5},"replicas":1,"resources":{"limits":{"cpu":"700m","memory":"900Mi"},"requests":{"cpu":"700m","memory":"900Mi"}},"service":{"name":"http-passport","oxPassportServiceName":"oxpassport","port":8090},"tolerations":[],"topologySpreadConstraints":{},"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | Gluu interface to Passport.js to support social login and inbound identity. |
| oxpassport.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| oxpassport.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| oxpassport.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| oxpassport.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| oxpassport.dnsConfig | object | `{}` | Add custom dns config |
| oxpassport.dnsPolicy | string | `""` | Add custom dns policy |
| oxpassport.hpa | object | `{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50}` | Configure the HorizontalPodAutoscaler |
| oxpassport.hpa.behavior | object | `{}` | Scaling Policies |
| oxpassport.hpa.metrics | list | `[]` | metrics if targetCPUUtilizationPercentage is not set |
| oxpassport.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| oxpassport.image.pullSecrets | list | `[]` | Image Pull Secrets |
| oxpassport.image.repository | string | `"gluufederation/oxpassport"` | Image  to use for deploying. |
| oxpassport.image.tag | string | `"4.5.5-2"` | Image  tag to use for deploying. |
| oxpassport.istioDestinationRuleCookieTTL | string | `"60s"` | Istio Destination Rule loadBalancer.consistentHash.httpCookie.ttl if istio ingress is enabled |
| oxpassport.livenessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"failureThreshold":20,"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5}` | Configure the liveness healthcheck for oxPassport if needed. |
| oxpassport.pdb | object | `{"enabled":true,"maxUnavailable":"90%"}` | Configure the PodDisruptionBudget |
| oxpassport.readinessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"failureThreshold":20,"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5}` | Configure the readiness healthcheck for the oxPassport if needed. |
| oxpassport.replicas | int | `1` | Service replica number |
| oxpassport.resources | object | `{"limits":{"cpu":"700m","memory":"900Mi"},"requests":{"cpu":"700m","memory":"900Mi"}}` | Resource specs. |
| oxpassport.resources.limits.cpu | string | `"700m"` | CPU limit. |
| oxpassport.resources.limits.memory | string | `"900Mi"` | Memory limit. |
| oxpassport.resources.requests.cpu | string | `"700m"` | CPU request. |
| oxpassport.resources.requests.memory | string | `"900Mi"` | Memory request. |
| oxpassport.service.name | string | `"http-passport"` | The name of the oxPassport port within the oxPassport service. Please keep it as default. |
| oxpassport.service.oxPassportServiceName | string | `"oxpassport"` | Name of the oxPassport service. Please keep it as default. |
| oxpassport.service.port | int | `8090` | Port of the oxPassport service. Please keep it as default. |
| oxpassport.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| oxpassport.topologySpreadConstraints | object | `{}` | Configure the topology spread constraints. Notice this is a map NOT a list as in the upstream API https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ |
| oxpassport.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| oxpassport.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| oxpassport.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| oxpassport.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| oxpassport.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| oxshibboleth | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"customScripts":[],"dnsConfig":{},"dnsPolicy":"","hpa":{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50},"image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/oxshibboleth","tag":"4.5.5-1"},"istioDestinationRuleCookieTTL":"60s","lifecycle":{},"livenessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5},"nodeSelector":{},"pdb":{"enabled":true,"maxUnavailable":1},"readinessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5},"replicas":1,"resources":{"limits":{"cpu":"1000m","memory":"1000Mi"},"requests":{"cpu":"1000m","memory":"1000Mi"}},"service":{"name":"http-oxshib","oxShibbolethServiceName":"oxshibboleth","port":8080,"sessionAffinity":"ClientIP"},"tolerations":[],"topologySpreadConstraints":{},"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | Shibboleth project for the Gluu Server's SAML IDP functionality. |
| oxshibboleth.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| oxshibboleth.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| oxshibboleth.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| oxshibboleth.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| oxshibboleth.dnsConfig | object | `{}` | Add custom dns config |
| oxshibboleth.dnsPolicy | string | `""` | Add custom dns policy |
| oxshibboleth.hpa | object | `{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50}` | Configure the HorizontalPodAutoscaler |
| oxshibboleth.hpa.behavior | object | `{}` | Scaling Policies |
| oxshibboleth.hpa.metrics | list | `[]` | metrics if targetCPUUtilizationPercentage is not set |
| oxshibboleth.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| oxshibboleth.image.pullSecrets | list | `[]` | Image Pull Secrets |
| oxshibboleth.image.repository | string | `"gluufederation/oxshibboleth"` | Image  to use for deploying. |
| oxshibboleth.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| oxshibboleth.istioDestinationRuleCookieTTL | string | `"60s"` | Istio Destination Rule loadBalancer.consistentHash.httpCookie.ttl if istio ingress is enabled |
| oxshibboleth.livenessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5}` | Configure the liveness healthcheck for the oxshibboleth if needed. |
| oxshibboleth.livenessProbe.exec | object | `{"command":["python3","/app/scripts/healthcheck.py"]}` | Executes the python3 healthcheck. |
| oxshibboleth.pdb | object | `{"enabled":true,"maxUnavailable":1}` | Configure the PodDisruptionBudget |
| oxshibboleth.readinessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5}` | Configure the readiness healthcheck for the oxshibboleth if needed. |
| oxshibboleth.replicas | int | `1` | Service replica number. |
| oxshibboleth.resources | object | `{"limits":{"cpu":"1000m","memory":"1000Mi"},"requests":{"cpu":"1000m","memory":"1000Mi"}}` | Resource specs. |
| oxshibboleth.resources.limits.cpu | string | `"1000m"` | CPU limit. |
| oxshibboleth.resources.limits.memory | string | `"1000Mi"` | Memory limit. This value is used to calculate memory allocation for Java. Currently it only supports `Mi`. Please refrain from using other units. |
| oxshibboleth.resources.requests.cpu | string | `"1000m"` | CPU request. |
| oxshibboleth.resources.requests.memory | string | `"1000Mi"` | Memory request. |
| oxshibboleth.service.name | string | `"http-oxshib"` | Port of the oxShibboleth service. Please keep it as default. |
| oxshibboleth.service.oxShibbolethServiceName | string | `"oxshibboleth"` | Name of the oxShibboleth service. Please keep it as default. |
| oxshibboleth.service.port | int | `8080` | The name of the oxPassport port within the oxPassport service. Please keep it as default. |
| oxshibboleth.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| oxshibboleth.topologySpreadConstraints | object | `{}` | Configure the topology spread constraints. Notice this is a map NOT a list as in the upstream API https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ |
| oxshibboleth.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| oxshibboleth.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| oxshibboleth.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| oxshibboleth.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| oxshibboleth.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| oxtrust | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"customScripts":[],"dnsConfig":{},"dnsPolicy":"","hpa":{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50},"image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/oxtrust","tag":"4.5.5-2"},"istioDestinationRuleCookieTTL":"60s","lifecycle":{},"livenessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5},"nodeSelector":{},"pdb":{"enabled":true,"maxUnavailable":1},"readinessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5},"replicas":1,"resources":{"limits":{"cpu":"2500m","memory":"2500Mi"},"requests":{"cpu":"2500m","memory":"2500Mi"}},"service":{"clusterIp":"None","name":"http-oxtrust","oxTrustServiceName":"oxtrust","port":8080},"tolerations":[],"topologySpreadConstraints":{},"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | Gluu Admin UI. This shouldn't be internet facing. |
| oxtrust.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| oxtrust.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| oxtrust.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| oxtrust.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| oxtrust.dnsConfig | object | `{}` | Add custom dns config |
| oxtrust.dnsPolicy | string | `""` | Add custom dns policy |
| oxtrust.hpa | object | `{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50}` | Configure the HorizontalPodAutoscaler |
| oxtrust.hpa.behavior | object | `{}` | Scaling Policies |
| oxtrust.hpa.metrics | list | `[]` | metrics if targetCPUUtilizationPercentage is not set |
| oxtrust.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| oxtrust.image.pullSecrets | list | `[]` | Image Pull Secrets |
| oxtrust.image.repository | string | `"gluufederation/oxtrust"` | Image  to use for deploying. |
| oxtrust.image.tag | string | `"4.5.5-2"` | Image  tag to use for deploying. |
| oxtrust.istioDestinationRuleCookieTTL | string | `"60s"` | Istio Destination Rule loadBalancer.consistentHash.httpCookie.ttl if istio ingress is enabled |
| oxtrust.livenessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5}` | Configure the liveness healthcheck for the auth server if needed. |
| oxtrust.livenessProbe.exec | object | `{"command":["python3","/app/scripts/healthcheck.py"]}` | Executes the python3 healthcheck. |
| oxtrust.pdb | object | `{"enabled":true,"maxUnavailable":1}` | Configure the PodDisruptionBudget |
| oxtrust.readinessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5}` | Configure the readiness healthcheck for the auth server if needed. |
| oxtrust.replicas | int | `1` | Service replica number. |
| oxtrust.resources | object | `{"limits":{"cpu":"2500m","memory":"2500Mi"},"requests":{"cpu":"2500m","memory":"2500Mi"}}` | Resource specs. |
| oxtrust.resources.limits.cpu | string | `"2500m"` | CPU limit. |
| oxtrust.resources.limits.memory | string | `"2500Mi"` | Memory limit. This value is used to calculate memory allocation for Java. Currently it only supports `Mi`. Please refrain from using other units. |
| oxtrust.resources.requests.cpu | string | `"2500m"` | CPU request. |
| oxtrust.resources.requests.memory | string | `"2500Mi"` | Memory request. |
| oxtrust.service.name | string | `"http-oxtrust"` | The name of the oxtrust port within the oxtrust service. Please keep it as default. |
| oxtrust.service.oxTrustServiceName | string | `"oxtrust"` | Name of the oxtrust service. Please keep it as default. |
| oxtrust.service.port | int | `8080` | Port of the oxtrust service. Please keep it as default. |
| oxtrust.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| oxtrust.topologySpreadConstraints | object | `{}` | Configure the topology spread constraints. Notice this is a map NOT a list as in the upstream API https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ |
| oxtrust.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| oxtrust.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| oxtrust.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| oxtrust.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| oxtrust.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| persistence | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"customScripts":[],"dnsConfig":{},"dnsPolicy":"","image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/persistence","tag":"4.5.5-1"},"lifecycle":{},"nodeSelector":{},"resources":{"limits":{"cpu":"300m","memory":"300Mi"},"requests":{"cpu":"300m","memory":"300Mi"}},"tolerations":[],"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | Job to generate data and initial config for Gluu Server persistence layer. |
| persistence.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| persistence.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| persistence.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| persistence.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| persistence.dnsConfig | object | `{}` | Add custom dns config |
| persistence.dnsPolicy | string | `""` | Add custom dns policy |
| persistence.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| persistence.image.pullSecrets | list | `[]` | Image Pull Secrets |
| persistence.image.repository | string | `"gluufederation/persistence"` | Image  to use for deploying. |
| persistence.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| persistence.resources | object | `{"limits":{"cpu":"300m","memory":"300Mi"},"requests":{"cpu":"300m","memory":"300Mi"}}` | Resource specs. |
| persistence.resources.limits.cpu | string | `"300m"` | CPU limit |
| persistence.resources.limits.memory | string | `"300Mi"` | Memory limit. |
| persistence.resources.requests.cpu | string | `"300m"` | CPU request. |
| persistence.resources.requests.memory | string | `"300Mi"` | Memory request. |
| persistence.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| persistence.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| persistence.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| persistence.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| persistence.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| persistence.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |
| scim | object | `{"additionalAnnotations":{},"additionalLabels":{},"affinity":{},"customScripts":[],"dnsConfig":{},"dnsPolicy":"","hpa":{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50},"image":{"pullPolicy":"IfNotPresent","pullSecrets":[],"repository":"gluufederation/scim","tag":"4.5.5-1"},"lifecycle":{},"livenessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5},"nodeSelector":{},"pdb":{"enabled":true,"maxUnavailable":"90%"},"readinessProbe":{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5},"replicas":1,"resources":{"limits":{"cpu":"1000m","memory":"1000Mi"},"requests":{"cpu":"1000m","memory":"1000Mi"}},"service":{"name":"http-scim","port":8080,"scimServiceName":"scim"},"tolerations":[],"topologySpreadConstraints":{},"usrEnvs":{"normal":{},"secret":{}},"volumeMounts":[],"volumes":[]}` | System for Cross-domain Identity Management (SCIM) version 2.0 |
| scim.additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| scim.additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| scim.affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| scim.customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. - /tmp/custom.sh - /tmp/custom2.sh |
| scim.dnsConfig | object | `{}` | Add custom dns config |
| scim.dnsPolicy | string | `""` | Add custom dns policy |
| scim.hpa | object | `{"behavior":{},"enabled":true,"maxReplicas":10,"metrics":[],"minReplicas":1,"targetCPUUtilizationPercentage":50}` | Configure the HorizontalPodAutoscaler |
| scim.hpa.behavior | object | `{}` | Scaling Policies |
| scim.hpa.metrics | list | `[]` | metrics if targetCPUUtilizationPercentage is not set |
| scim.image.pullPolicy | string | `"IfNotPresent"` | Image pullPolicy to use for deploying. |
| scim.image.pullSecrets | list | `[]` | Image Pull Secrets |
| scim.image.repository | string | `"gluufederation/scim"` | Image  to use for deploying. |
| scim.image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| scim.livenessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":30,"periodSeconds":30,"timeoutSeconds":5}` | Configure the liveness healthcheck for SCIM if needed. |
| scim.pdb | object | `{"enabled":true,"maxUnavailable":"90%"}` | Configure the PodDisruptionBudget |
| scim.readinessProbe | object | `{"exec":{"command":["python3","/app/scripts/healthcheck.py"]},"initialDelaySeconds":25,"periodSeconds":25,"timeoutSeconds":5}` | Configure the readiness healthcheck for the SCIM if needed. |
| scim.replicas | int | `1` | Service replica number. |
| scim.resources.limits.cpu | string | `"1000m"` | CPU limit. |
| scim.resources.limits.memory | string | `"1000Mi"` | Memory limit. This value is used to calculate memory allocation for Java. Currently it only supports `Mi`. Please refrain from using other units. |
| scim.resources.requests.cpu | string | `"1000m"` | CPU request. |
| scim.resources.requests.memory | string | `"1000Mi"` | Memory request. |
| scim.service.name | string | `"http-scim"` | The name of the scim port within the scim service. Please keep it as default. |
| scim.service.port | int | `8080` | Port of the scim service. Please keep it as default. |
| scim.service.scimServiceName | string | `"scim"` | Name of the scim service. Please keep it as default. |
| scim.tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| scim.topologySpreadConstraints | object | `{}` | Configure the topology spread constraints. Notice this is a map NOT a list as in the upstream API https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ |
| scim.usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service |
| scim.usrEnvs.normal | object | `{}` | Add custom normal envs to the service variable1: value1 |
| scim.usrEnvs.secret | object | `{}` | Add custom secret envs to the service variable1: value1 |
| scim.volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| scim.volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.13.1](https://github.com/norwoodj/helm-docs/releases/v1.13.1)
