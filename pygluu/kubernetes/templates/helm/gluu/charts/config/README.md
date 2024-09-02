# config

![Version: 1.8.39](https://img.shields.io/badge/Version-1.8.39-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 4.5.5](https://img.shields.io/badge/AppVersion-4.5.5-informational?style=flat-square)

Configuration parameters for setup and initial configuration secret and config layers used by Gluu services.

**Homepage:** <https://gluu.org/docs/gluu-server/reference/container-configs/>

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Mohammad Abudayyeh | <support@gluu.org> | <https://github.com/moabu> |

## Source Code

* <https://gluu.org/docs/gluu-server/reference/container-configs/>
* <https://github.com/GluuFederation/docker-config-init>
* <https://github.com/GluuFederation/cloud-native-edition/tree/4.4/pygluu/kubernetes/templates/helm/gluu/charts/config>

## Requirements

Kubernetes: `>=v1.22.0-0`

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| additionalAnnotations | object | `{}` | Additional annotations that will be added across all resources  in the format of {cert-manager.io/issuer: "letsencrypt-prod"}. key app is taken |
| additionalLabels | object | `{}` | Additional labels that will be added across all resources definitions in the format of {mylabel: "myapp"} |
| adminPass | string | `"P@ssw0rd"` | Admin password to log in to the UI. |
| affinity | object | `{}` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| city | string | `"Austin"` | City. Used for certificate creation. |
| configmap.cnAwsAccessKeyId | string | `""` |  |
| configmap.cnAwsDefaultRegion | string | `"us-west-1"` |  |
| configmap.cnAwsProfile | string | `"gluu"` |  |
| configmap.cnAwsSecretAccessKey | string | `""` |  |
| configmap.cnAwsSecretsEndpointUrl | string | `""` |  |
| configmap.cnAwsSecretsNamePrefix | string | `"gluu"` |  |
| configmap.cnAwsSecretsReplicaRegions | list | `[]` |  |
| configmap.cnGoogleProjectId | string | `"google-project-to-save-config-and-secrets-to"` | Project id of the google project the secret manager belongs to. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| configmap.cnGoogleServiceAccount | string | `"SWFtTm90YVNlcnZpY2VBY2NvdW50Q2hhbmdlTWV0b09uZQo="` | Service account with roles roles/secretmanager.admin base64 encoded string. This is used often inside the services to reach the configuration layer. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| configmap.cnGoogleSpannerDatabaseId | string | `""` | Google Spanner Database ID. Used only when global.gluuPersistenceType is spanner. |
| configmap.cnGoogleSpannerInstanceId | string | `""` | Google Spanner ID. Used only when global.gluuPersistenceType is spanner. |
| configmap.cnSecretGoogleSecretNamePrefix | string | `"gluu"` | Prefix for Gluu secret in Google Secret Manager. Defaults to gluu. If left gluu-secret secret will be created. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| configmap.cnSecretGoogleSecretVersionId | string | `"latest"` | Secret version to be used for secret configuration. Defaults to latest and should normally always stay that way. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| configmap.cnSqlDbDialect | string | `"mysql"` | SQL database dialect. `mysql` or `pgsql` |
| configmap.cnSqlDbHost | string | `"my-release-mysql.default.svc.cluster.local"` | SQL database host uri. |
| configmap.cnSqlDbName | string | `"gluu"` | SQL database username. |
| configmap.cnSqlDbPort | int | `3306` | SQL database port. |
| configmap.cnSqlDbTimezone | string | `"UTC"` | SQL database timezone. |
| configmap.cnSqlDbUser | string | `"gluu"` | SQL database username. |
| configmap.cnSqlPasswordFile | string | `"/etc/gluu/conf/sql_password"` | SQL password file holding password from config.configmap.cnSqldbUserPassword . |
| configmap.cnSqldbUserPassword | string | `"Test1234#"` | SQL password  injected as config.configmap.cnSqlPasswordFile . |
| configmap.containerMetadataName | string | `"kubernetes"` |  |
| configmap.gluuCacheType | string | `"NATIVE_PERSISTENCE"` | Cache type. `NATIVE_PERSISTENCE`, `REDIS`. or `IN_MEMORY`. Defaults to `NATIVE_PERSISTENCE` . |
| configmap.gluuCasaEnabled | bool | `false` | Enable Casa flag . |
| configmap.gluuCouchbaseBucketPrefix | string | `"gluu"` | The prefix of couchbase buckets. This helps with separation in between different environments and allows for the same couchbase cluster to be used by different setups of Gluu. |
| configmap.gluuCouchbaseCertFile | string | `"/etc/certs/couchbase.crt"` | Location of `couchbase.crt` used by Couchbase SDK for tls termination. The file path must end with couchbase.crt. In mTLS setups this is not required. |
| configmap.gluuCouchbaseCrt | string | `"LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURlakNDQW1LZ0F3SUJBZ0lKQUwyem5UWlREUHFNTUEwR0NTcUdTSWIzRFFFQkN3VUFNQzB4S3pBcEJnTlYKQkFNTUlpb3VZMkpuYkhWMUxtUmxabUYxYkhRdWMzWmpMbU5zZFhOMFpYSXViRzlqWVd3d0hoY05NakF3TWpBMQpNRGt4T1RVeFdoY05NekF3TWpBeU1Ea3hPVFV4V2pBdE1Tc3dLUVlEVlFRRERDSXFMbU5pWjJ4MWRTNWtaV1poCmRXeDBMbk4yWXk1amJIVnpkR1Z5TG14dlkyRnNNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUIKQ2dLQ0FRRUFycmQ5T3lvSnRsVzhnNW5nWlJtL2FKWjJ2eUtubGU3dVFIUEw4Q2RJa1RNdjB0eHZhR1B5UkNQQgo3RE00RTFkLzhMaU5takdZZk41QjZjWjlRUmNCaG1VNmFyUDRKZUZ3c0x0cTFGT3MxaDlmWGo3d3NzcTYrYmlkCjV6Umw3UEE0YmdvOXVkUVRzU1UrWDJUUVRDc0dxVVVPWExrZ3NCMjI0RDNsdkFCbmZOeHcvYnFQa2ZCQTFxVzYKVXpxellMdHN6WE5GY0dQMFhtU3c4WjJuaFhhUGlva2pPT2dyMkMrbVFZK0htQ2xGUWRpd2g2ZjBYR0V0STMrKwoyMStTejdXRkF6RlFBVUp2MHIvZnk4TDRXZzh1YysvalgwTGQrc2NoQTlNQjh3YmJORUp2ZjNMOGZ5QjZ0cTd2CjF4b0FnL0g0S1dJaHdqSEN0dFVnWU1oU0xWV3UrUUlEQVFBQm80R2NNSUdaTUIwR0ExVWREZ1FXQkJTWmQxWU0KVGNIRVZjSENNUmp6ejczZitEVmxxREJkQmdOVkhTTUVWakJVZ0JTWmQxWU1UY0hFVmNIQ01Sanp6NzNmK0RWbApxS0V4cEM4d0xURXJNQ2tHQTFVRUF3d2lLaTVqWW1kc2RYVXVaR1ZtWVhWc2RDNXpkbU11WTJ4MWMzUmxjaTVzCmIyTmhiSUlKQUwyem5UWlREUHFNTUF3R0ExVWRFd1FGTUFNQkFmOHdDd1lEVlIwUEJBUURBZ0VHTUEwR0NTcUcKU0liM0RRRUJDd1VBQTRJQkFRQk9meTVWSHlKZCtWUTBXaUQ1aSs2cmhidGNpSmtFN0YwWVVVZnJ6UFN2YWVFWQp2NElVWStWOC9UNnE4Mk9vVWU1eCtvS2dzbFBsL01nZEg2SW9CRnVtaUFqek14RTdUYUhHcXJ5dk13Qk5IKzB5CnhadG9mSnFXQzhGeUlwTVFHTEs0RVBGd3VHRlJnazZMRGR2ZEN5NVdxWW1MQWdBZVh5VWNaNnlHYkdMTjRPUDUKZTFiaEFiLzRXWXRxRHVydFJrWjNEejlZcis4VWNCVTRLT005OHBZN05aaXFmKzlCZVkvOEhZaVQ2Q0RRWWgyTgoyK0VWRFBHcFE4UkVsRThhN1ZLL29MemlOaXFyRjllNDV1OU1KdjM1ZktmNUJjK2FKdWduTGcwaUZUYmNaT1prCkpuYkUvUENIUDZFWmxLaEFiZUdnendtS1dDbTZTL3g0TklRK2JtMmoKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo="` | Couchbase certificate authority string. This must be encoded using base64. This can also be found in your couchbase UI Security > Root Certificate. In mTLS setups this is not required. |
| configmap.gluuCouchbaseIndexNumReplica | int | `0` | The number of replicas per index created. Please note that the number of index nodes must be one greater than the number of index replicas. That means if your couchbase cluster only has 2 index nodes you cannot place the number of replicas to be higher than 1. |
| configmap.gluuCouchbasePass | string | `"P@ssw0rd"` | Couchbase password for the restricted user config.configmap.gluuCouchbaseUser  that is often used inside the services. The password must contain one digit, one uppercase letter, one lower case letter and one symbol . |
| configmap.gluuCouchbasePassFile | string | `"/etc/gluu/conf/couchbase_password"` | The location of the Couchbase restricted user config.configmap.gluuCouchbaseUser password. The file path must end with couchbase_password |
| configmap.gluuCouchbaseSuperUser | string | `"admin"` | The Couchbase super user (admin) user name. This user is used during initialization only. |
| configmap.gluuCouchbaseSuperUserPass | string | `"P@ssw0rd"` | Couchbase password for the super user config.configmap.gluuCouchbaseSuperUser  that is used during the initialization process. The password must contain one digit, one uppercase letter, one lower case letter and one symbol |
| configmap.gluuCouchbaseSuperUserPassFile | string | `"/etc/gluu/conf/couchbase_superuser_password"` | The location of the Couchbase restricted user config.configmap.gluuCouchbaseSuperUser password. The file path must end with couchbase_superuser_password. |
| configmap.gluuCouchbaseUrl | string | `"cbgluu.default.svc.cluster.local"` | Couchbase URL. Used only when global.gluuPersistenceType is hybrid or couchbase. This should be in FQDN format for either remote or local Couchbase clusters. The address can be an internal address inside the kubernetes cluster |
| configmap.gluuCouchbaseUser | string | `"gluu"` | Couchbase restricted user. Used only when global.gluuPersistenceType is hybrid or couchbase. |
| configmap.gluuDocumentStoreType | string | `"DB"` | Document store type to use for shibboleth files DB, LOCAL, or JCA (deprecated). Note that if JCA is selected Apache Jackrabbit will be used. |
| configmap.gluuJackrabbitAdminId | string | `"admin"` | Jackrabbit admin uid. |
| configmap.gluuJackrabbitAdminIdFile | string | `"/etc/gluu/conf/jackrabbit_admin_id"` | The location of the Jackrabbit admin uid config.gluuJackrabbitAdminId. The file path must end with jackrabbit_admin_id. |
| configmap.gluuJackrabbitAdminPassFile | string | `"/etc/gluu/conf/jackrabbit_admin_password"` | The location of the Jackrabbit admin password jackrabbit.secrets.gluuJackrabbitAdminPassword. The file path must end with jackrabbit_admin_password. |
| configmap.gluuJackrabbitPostgresDatabaseName | string | `"jackrabbit"` | Jackrabbit postgres database name. |
| configmap.gluuJackrabbitPostgresHost | string | `"postgresql.postgres.svc.cluster.local"` | Postgres url |
| configmap.gluuJackrabbitPostgresPasswordFile | string | `"/etc/gluu/conf/postgres_password"` | The location of the Jackrabbit postgres password file jackrabbit.secrets.gluuJackrabbitPostgresPassword. The file path must end with postgres_password. |
| configmap.gluuJackrabbitPostgresPort | int | `5432` | Jackrabbit Postgres port |
| configmap.gluuJackrabbitPostgresUser | string | `"jackrabbit"` | Jackrabbit Postgres uid |
| configmap.gluuJackrabbitSyncInterval | int | `300` | Interval between files sync (default to 300 seconds). |
| configmap.gluuJackrabbitUrl | string | `"http://jackrabbit:8080"` | Jackrabbit internal url. Normally left as default. |
| configmap.gluuLdapUrl | string | `"opendj:1636"` | OpenDJ internal address. Leave as default. Used when `global.gluuPersistenceType` is set to `ldap`. |
| configmap.gluuMaxRamPercent | string | `"75.0"` | Value passed to Java option -XX:MaxRAMPercentage |
| configmap.gluuOxauthBackend | string | `"oxauth:8080"` | oxAuth internal address. Leave as default. |
| configmap.gluuOxdAdminCertCn | string | `"oxd-server"` | OXD serve OAuth client admin certificate common name. This should be left to the default value client-api . |
| configmap.gluuOxdApplicationCertCn | string | `"oxd-server"` | OXD server OAuth client application certificate common name. This should be left to the default value client-api. |
| configmap.gluuOxdBindIpAddresses | string | `"*"` | OXD server bind address. This limits what ip ranges can access the client-api. This should be left as * and controlled by a NetworkPolicy |
| configmap.gluuOxdServerUrl | string | `"oxd-server:8443"` | OXD server Oauth client address. This should be left intact in kubernetes as it uses the internal address format. |
| configmap.gluuOxtrustApiEnabled | bool | `false` | Enable oxTrust API |
| configmap.gluuOxtrustApiTestMode | bool | `false` | Enable oxTrust API testmode |
| configmap.gluuOxtrustBackend | string | `"oxtrust:8080"` | oxTrust internal address. Leave as default. |
| configmap.gluuOxtrustConfigGeneration | bool | `true` | Whether to generate oxShibboleth configuration or not (default to true). |
| configmap.gluuPassportEnabled | bool | `false` | Boolean flag to enable/disable passport chart |
| configmap.gluuPassportFailureRedirectUrl | string | `""` | TEMP KEY TO BE REMOVED IN 4.4 which allows passport failure redirect url to be specified. |
| configmap.gluuPersistenceLdapMapping | string | `"default"` | Specify data that should be saved in LDAP (one of default, user, cache, site, token, or session; default to default). Note this environment only takes effect when `global.gluuPersistenceType`  is set to `hybrid`. |
| configmap.gluuRedisSentinelGroup | string | `""` | Redis Sentinel Group. Often set when `config.configmap.gluuRedisType` is set to `SENTINEL`. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| configmap.gluuRedisSslTruststore | string | `""` | Redis SSL truststore. Optional. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| configmap.gluuRedisType | string | `"STANDALONE"` | Redis service type. `STANDALONE` or `CLUSTER`. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| configmap.gluuRedisUrl | string | `"redis:6379"` | Redis URL and port number <url>:<port>. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| configmap.gluuRedisUseSsl | string | `"false"` | Boolean to use SSL in Redis. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| configmap.gluuSamlEnabled | bool | `false` | Enable SAML-related features; UI menu, etc. |
| configmap.gluuScimProtectionMode | string | `"OAUTH"` | SCIM protection mode OAUTH|TEST|UMA |
| configmap.gluuSyncCasaManifests | bool | `false` | Activate manual Casa files sync - depreciated |
| configmap.gluuSyncShibManifests | bool | `false` | Activate manual Shib files sync - depreciated |
| configmap.lbAddr | string | `""` | Loadbalancer address for AWS if the FQDN is not registered. |
| countryCode | string | `"US"` | Country code. Used for certificate creation. |
| customScripts | list | `[]` | Add custom scripts that have been mounted to run before the entrypoint. |
| dnsConfig | object | `{}` | Add custom dns config |
| dnsPolicy | string | `""` | Add custom dns policy |
| email | string | `"support@gluu.com"` | Email address of the administrator usually. Used for certificate creation. |
| image.pullSecrets | list | `[]` | Image Pull Secrets |
| image.repository | string | `"gluufederation/config-init"` | Image  to use for deploying. |
| image.tag | string | `"4.5.5-1"` | Image  tag to use for deploying. |
| ldapPass | string | `"P@ssw0rd"` | LDAP admin password if OpennDJ is used for persistence. |
| lifecycle | object | `{}` |  |
| migration | object | `{"enabled":false,"migrationDataFormat":"ldif","migrationDir":"/ce-migration"}` | CE to CN Migration section |
| migration.enabled | bool | `false` | Boolean flag to enable migration from CE |
| migration.migrationDataFormat | string | `"ldif"` | migration data-format depending on persistence backend. Supported data formats are ldif, couchbase+json, spanner+avro, postgresql+json, and mysql+json. |
| migration.migrationDir | string | `"/ce-migration"` | Directory holding all migration files |
| nodeSelector | object | `{}` |  |
| orgName | string | `"Gluu"` | Organization name. Used for certificate creation. |
| redisPass | string | `"P@assw0rd"` | Redis admin password if `config.configmap.gluuCacheType` is set to `REDIS`. |
| resources | object | `{"limits":{"cpu":"300m","memory":"300Mi"},"requests":{"cpu":"300m","memory":"300Mi"}}` | Resource specs. |
| resources.limits.cpu | string | `"300m"` | CPU limit. |
| resources.limits.memory | string | `"300Mi"` | Memory limit. |
| resources.requests.cpu | string | `"300m"` | CPU request. |
| resources.requests.memory | string | `"300Mi"` | Memory request. |
| salt | string | `""` | Salt. Used for encoding/decoding sensitive data. If omitted or set to empty string, the value will be self-generated. Otherwise, a 24 alphanumeric characters are allowed as its value. |
| state | string | `"TX"` | State code. Used for certificate creation. |
| tolerations | list | `[]` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| usrEnvs | object | `{"normal":{},"secret":{}}` | Add custom normal and secret envs to the service. |
| usrEnvs.normal | object | `{}` | Add custom normal envs to the service. variable1: value1 |
| usrEnvs.secret | object | `{}` | Add custom secret envs to the service. variable1: value1 |
| volumeMounts | list | `[]` | Configure any additional volumesMounts that need to be attached to the containers |
| volumes | list | `[]` | Configure any additional volumes that need to be attached to the pod |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.13.1](https://github.com/norwoodj/helm-docs/releases/v1.13.1)
