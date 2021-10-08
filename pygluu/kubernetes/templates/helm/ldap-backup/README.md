# ldap-backup

![Version: 1.6.11](https://img.shields.io/badge/Version-1.6.11-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 4.3.0](https://img.shields.io/badge/AppVersion-4.3.0-informational?style=flat-square)

A backup strategy for LDAP

**Homepage:** <https://gluu.org/docs/gluu-server>

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Mohammad Abudayyeh | support@gluu.org | https://github.com/moabu |

## Source Code

* <https://github.com/GluuFederation/docker-opendj>
* <https://github.com/GluuFederation/cloud-native-edition/tree/4.3/pygluu/kubernetes/templates/helm/ldap-backup>

## Requirements

Kubernetes: `>=v1.18.0-0`

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| concurrencyPolicy | string | `"Forbid"` | CronJobb concurrencyPolicy. Leave as default. |
| configAdapterName | string | `"kubernetes"` | The config backend adapter that will hold Gluu configuration layer. google|kubernetes |
| configSecretAdapter | string | `"kubernetes"` | The config backend adapter that will hold Gluu secret layer. google|kubernetes |
| dnsConfig | object | `{}` | Add custom dns config |
| dnsPolicy | string | `""` | Add custom dns policy |
| fullnameOverride | string | `""` |  |
| gluuCacheType | string | `"NATIVE_PERSISTENCE"` | Cache type. `NATIVE_PERSISTENCE`, `REDIS`. or `IN_MEMORY`. Defaults to `NATIVE_PERSISTENCE` . |
| gluuLdapAutoReplicate | bool | `false` | Turn off replication in LDAP server. This must be left as false. |
| gluuLdapSchedule | string | `"*/59 * * * *"` | Cron job Schedule for backup |
| gluuOxtrustConfigGeneration | bool | `true` | Whether to generate oxShibboleth configuration or not (default to true). |
| gluuRedisType | string | `"STANDALONE"` | Redis service type. `STANDALONE` or `CLUSTER`. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| gluuRedisUrl | string | `"redis:6379"` | Redis URL and port number <url>:<port>. Can be used when  `config.configmap.gluuCacheType` is set to `REDIS`. |
| gluuReleaseName | string | `"gluu"` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"gluufederation/opendj"` |  |
| image.tag | string | `"4.3.0_01"` |  |
| ldapPass | string | `"P@assw0rd"` | LDAP admin password if OpennDJ is used for persistence. |
| ldapServiceName | string | `"opendj"` | Name of the OpenDJ service. Please keep it as default. |
| multiCluster | object | `{"enabled":false,"ldapAdvertiseAdminPort":30440}` | Specify cluster details if used to activate backup. |
| nameOverride | string | `""` |  |
| ports | object | `{"admin":{"port":4444,"targetPort":4444},"ldap":{"port":1389,"targetPort":1389},"ldaps":{"port":1636,"targetPort":1636},"replication":{"port":8989,"targetPort":8989}}` | servicePorts values used in StatefulSet container |
| restartPolicy | string | `"Never"` |  |
| serviceAccount.create | bool | `true` | Specifies whether a service account should be created |
| serviceAccount.name | string | `nil` | The name of the service account to use. If not set and create is true, a name is generated using the fullname template |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.5.0](https://github.com/norwoodj/helm-docs/releases/v1.5.0)