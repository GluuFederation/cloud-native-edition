# gluu-upgrade

![Version: 1.6.11](https://img.shields.io/badge/Version-1.6.11-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 4.3.0](https://img.shields.io/badge/AppVersion-4.3.0-informational?style=flat-square)

A Helm chart for upgrading gluu server

**Homepage:** <https://gluu.org/docs/gluu-server>

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Mohammad Abudayyeh | support@gluu.org | https://github.com/moabu |

## Source Code

* <https://gluu.org/docs/gluu-server/upgrade/>
* <https://github.com/GluuFederation/docker-upgrade>
* <https://github.com/GluuFederation/cloud-native-edition/tree/4.3/pygluu/kubernetes/templates/helm/gluu-upgrade>

## Requirements

Kubernetes: `>=v1.18.0-0`

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| cnConfigGoogleSecretNamePrefix | string | `"gluu"` | Prefix for Gluu configuration secret in Google Secret Manager. Defaults to gluu. If left intact gluu-configuration secret will be created. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| cnConfigGoogleSecretVersionId | string | `"latest"` | Secret version to be used for configuration. Defaults to latest and should normally always stay that way. Used only when global.configAdapterName and global.configSecretAdapter is set to google. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| cnGoogleApplicationCredentials | string | `"/etc/gluu/conf/google-credentials.json"` |  |
| cnGoogleProjectId | string | `"google-project-to-save-config-and-secrets-to"` | Project id of the google project the secret manager belongs to. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| cnGoogleSecretManagerPassPhrase | string | `"Test1234#"` | Passphrase for Gluu secret in Google Secret Manager. This is used for encrypting and decrypting data from the Google Secret Manager. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| cnGoogleServiceAccount | string | `"SWFtTm90YVNlcnZpY2VBY2NvdW50Q2hhbmdlTWV0b09uZQo="` | Service account with roles roles/secretmanager.admin base64 encoded string. This is used often inside the services to reach the configuration layer. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| cnGoogleSpannerDatabaseId | string | `""` | Google Spanner Database ID. Used only when global.gluuPersistenceType is spanner. |
| cnGoogleSpannerInstanceId | string | `""` | Google Spanner ID. Used only when global.gluuPersistenceType is spanner. |
| cnSecretGoogleSecretNamePrefix | string | `"gluu"` | Prefix for Gluu secret in Google Secret Manager. Defaults to gluu. If left gluu-secret secret will be created. Used only when global.configAdapterName and global.configSecretAdapter is set to google. |
| cnSecretGoogleSecretVersionId | string | `"latest"` |  |
| cnSqlDbDialect | string | `"mysql"` |  |
| cnSqlDbHost | string | `"my-release-mysql.default.svc.cluster.local"` | SQL database host uri. |
| cnSqlDbName | string | `"gluu"` | SQL database username. |
| cnSqlDbPort | int | `3306` | SQL database port. |
| cnSqlDbTimezone | string | `"UTC"` | SQL database timezone. |
| cnSqlDbUser | string | `"gluu"` | SQL database username. |
| cnSqlPasswordFile | string | `"/etc/gluu/conf/sql_password"` | SQL password file holding password from cnSqldbUserPassword . |
| cnSqldbUserPassword | string | `"Test1234#"` | SQL password  injected as cnSqlPasswordFile . |
| configAdapterName | string | `"kubernetes"` | The config backend adapter that will hold Gluu configuration layer. google|kubernetes |
| configSecretAdapter | string | `"kubernetes"` | The config backend adapter that will hold Gluu secret layer. google|kubernetes |
| domain | string | `"demoexample.gluu.org"` | Fully qualified domain name to be used for Gluu installation. This address will be used to reach Gluu services. |
| fullnameOverride | string | `""` |  |
| gluuCouchbaseBucketPrefix | string | `"gluu"` | The prefix of couchbase buckets. This helps with separation in between different environments and allows for the same couchbase cluster to be used by different setups of Gluu. |
| gluuCouchbaseCertFile | string | `"/etc/certs/couchbase.crt"` | Location of `couchbase.crt` used by Couchbase SDK for tls termination. The file path must end with couchbase.crt. In mTLS setups this is not required. |
| gluuCouchbaseCrt | string | `"LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURlakNDQW1LZ0F3SUJBZ0lKQUwyem5UWlREUHFNTUEwR0NTcUdTSWIzRFFFQkN3VUFNQzB4S3pBcEJnTlYKQkFNTUlpb3VZMkpuYkhWMUxtUmxabUYxYkhRdWMzWmpMbU5zZFhOMFpYSXViRzlqWVd3d0hoY05NakF3TWpBMQpNRGt4T1RVeFdoY05NekF3TWpBeU1Ea3hPVFV4V2pBdE1Tc3dLUVlEVlFRRERDSXFMbU5pWjJ4MWRTNWtaV1poCmRXeDBMbk4yWXk1amJIVnpkR1Z5TG14dlkyRnNNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUIKQ2dLQ0FRRUFycmQ5T3lvSnRsVzhnNW5nWlJtL2FKWjJ2eUtubGU3dVFIUEw4Q2RJa1RNdjB0eHZhR1B5UkNQQgo3RE00RTFkLzhMaU5takdZZk41QjZjWjlRUmNCaG1VNmFyUDRKZUZ3c0x0cTFGT3MxaDlmWGo3d3NzcTYrYmlkCjV6Umw3UEE0YmdvOXVkUVRzU1UrWDJUUVRDc0dxVVVPWExrZ3NCMjI0RDNsdkFCbmZOeHcvYnFQa2ZCQTFxVzYKVXpxellMdHN6WE5GY0dQMFhtU3c4WjJuaFhhUGlva2pPT2dyMkMrbVFZK0htQ2xGUWRpd2g2ZjBYR0V0STMrKwoyMStTejdXRkF6RlFBVUp2MHIvZnk4TDRXZzh1YysvalgwTGQrc2NoQTlNQjh3YmJORUp2ZjNMOGZ5QjZ0cTd2CjF4b0FnL0g0S1dJaHdqSEN0dFVnWU1oU0xWV3UrUUlEQVFBQm80R2NNSUdaTUIwR0ExVWREZ1FXQkJTWmQxWU0KVGNIRVZjSENNUmp6ejczZitEVmxxREJkQmdOVkhTTUVWakJVZ0JTWmQxWU1UY0hFVmNIQ01Sanp6NzNmK0RWbApxS0V4cEM4d0xURXJNQ2tHQTFVRUF3d2lLaTVqWW1kc2RYVXVaR1ZtWVhWc2RDNXpkbU11WTJ4MWMzUmxjaTVzCmIyTmhiSUlKQUwyem5UWlREUHFNTUF3R0ExVWRFd1FGTUFNQkFmOHdDd1lEVlIwUEJBUURBZ0VHTUEwR0NTcUcKU0liM0RRRUJDd1VBQTRJQkFRQk9meTVWSHlKZCtWUTBXaUQ1aSs2cmhidGNpSmtFN0YwWVVVZnJ6UFN2YWVFWQp2NElVWStWOC9UNnE4Mk9vVWU1eCtvS2dzbFBsL01nZEg2SW9CRnVtaUFqek14RTdUYUhHcXJ5dk13Qk5IKzB5CnhadG9mSnFXQzhGeUlwTVFHTEs0RVBGd3VHRlJnazZMRGR2ZEN5NVdxWW1MQWdBZVh5VWNaNnlHYkdMTjRPUDUKZTFiaEFiLzRXWXRxRHVydFJrWjNEejlZcis4VWNCVTRLT005OHBZN05aaXFmKzlCZVkvOEhZaVQ2Q0RRWWgyTgoyK0VWRFBHcFE4UkVsRThhN1ZLL29MemlOaXFyRjllNDV1OU1KdjM1ZktmNUJjK2FKdWduTGcwaUZUYmNaT1prCkpuYkUvUENIUDZFWmxLaEFiZUdnendtS1dDbTZTL3g0TklRK2JtMmoKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo="` | Couchbase certificate authority string. This must be encoded using base64. This can also be found in your couchbase UI Security > Root Certificate. In mTLS setups this is not required. |
| gluuCouchbaseSuperUser | string | `"admin"` | The Couchbase super user (admin) user name. This user is used during initialization only. |
| gluuCouchbaseSuperUserPass | string | `"P@ssw0rd"` | Couchbase password for the super user gluuCouchbaseSuperUser  that is used during the initialization process. The password must contain one digit, one uppercase letter, one lower case letter and one symbol |
| gluuCouchbaseSuperUserPassFile | string | `"/etc/gluu/conf/couchbase_superuser_password"` | The location of the Couchbase restricted user gluuCouchbaseSuperUser password. The file path must end with couchbase_superuser_password. |
| gluuCouchbaseUrl | string | `"cbgluu.default.svc.cluster.local"` | Couchbase URL. Used only when gluuPersistenceType is hybrid or couchbase. This should be in FQDN format for either remote or local Couchbase clusters. The address can be an internal address inside the kubernetes cluster |
| gluuLdapUrl | string | `"opendj:1636"` | OpenDJ internal address. Leave as default. Used when `global.gluuPersistenceType` is set to `ldap`. |
| gluuPersistenceLdapMapping | string | `"default"` | Specify data that should be saved in LDAP (one of default, user, cache, site, token, or session; default to default). Note this environment only takes effect when `gluuPersistenceType`  is set to `hybrid`. |
| gluuPersistenceType | string | `"ldap"` | Persistence backend to run Gluu with ldap|couchbase|hybrid|sql|spanner. |
| gluuReleaseName | string | `"gluu"` |  |
| image.repository | string | `"gluufederation/upgrade"` | Image  to use for deploying. |
| image.tag | string | `"4.3.0_01"` | Image  tag to use for deploying. |
| nameOverride | string | `""` |  |
| resources.limits.cpu | string | `"100m"` | CPU limit. |
| resources.limits.memory | string | `"100Mi"` | Memory limit. |
| resources.requests.cpu | string | `"100m"` | CPU request. |
| resources.requests.memory | string | `"100Mi"` | Memory request. |
| source | string | `"4.2"` | Gluu main version currently installed. |
| target | string | `"4.3"` | Gluu target version to upgrade to. |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.5.0](https://github.com/norwoodj/helm-docs/releases/v1.5.0)
