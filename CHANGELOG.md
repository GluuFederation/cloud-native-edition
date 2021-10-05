# Changelog

### [1.6.9](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.8...v1.6.9) (2021-10-05)


### Bug Fixes

* chart annotations ([2f67d3c](https://www.github.com/GluuFederation/cloud-native-edition/commit/2f67d3c1885f9c55ef6ecab111626a5aedf5cc51))

### [1.6.8](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.7...v1.6.8) (2021-09-30)


### Bug Fixes

* add namespaceIntId for multicluster ldap setups ([3068483](https://www.github.com/GluuFederation/cloud-native-edition/commit/3068483222172dfdc13d5309aa7bde2717c113f3))
* add support for proxy in kubernetes API ([#364](https://www.github.com/GluuFederation/cloud-native-edition/issues/364)) ([a4e6676](https://www.github.com/GluuFederation/cloud-native-edition/commit/a4e667689cd46acf2a38bbaa8c35ca7cff63a756))
* full cleanup for uninstallation ([2fbffef](https://www.github.com/GluuFederation/cloud-native-edition/commit/2fbffefae720a274a5d5aea0bb7e5b787f71ca8e))
* missing sql port number prompt ([613d9e5](https://www.github.com/GluuFederation/cloud-native-edition/commit/613d9e51aea7d7a31a362f29ad28cc896f3d3572))
* remove duplicate volumeMount from openDJ statefulset ([43da1c0](https://www.github.com/GluuFederation/cloud-native-edition/commit/43da1c07a8f6f8acf8d2b1e7a88b8d9471a6afbb))
* update alb ingress ([7e4d81e](https://www.github.com/GluuFederation/cloud-native-edition/commit/7e4d81e9e0b36d9ac42bf9d74835828531b16c67))
* update kubernetes version to 1.19 ([#359](https://www.github.com/GluuFederation/cloud-native-edition/issues/359)) ([2be82c1](https://www.github.com/GluuFederation/cloud-native-edition/commit/2be82c166130b2863ebf586ad5cd5cf33a0c854b))

### [1.6.7](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.6...v1.6.7) (2021-08-24)


### Bug Fixes

* add GLUU_LDAP_MULTI_CLUSTERS_IDS ([edce285](https://www.github.com/GluuFederation/cloud-native-edition/commit/edce285d9e359e96524b5284feef00b8eaac4d7e))
* add imagePullSecrets ([b34f391](https://www.github.com/GluuFederation/cloud-native-edition/commit/b34f391f7a4819aae832f0b8aee12352ab7399ba))
* add imagePullSecrets to seconday opendj statefulset ([22a18bf](https://www.github.com/GluuFederation/cloud-native-edition/commit/22a18bfa115e8c065fb78eb3f852ec86bc490fdb))
* add prompt for replicas ([3bcc8d9](https://www.github.com/GluuFederation/cloud-native-edition/commit/3bcc8d93ceb1f8af72d0ffa7c4a5c7d3f10e3487))
* add secondary ldap for local replication ([901a12d](https://www.github.com/GluuFederation/cloud-native-edition/commit/901a12dc567ddbaf5216f72d8017facb5f78ce5b))
* finalize opendj mutli regional replication strategy ([47878f2](https://www.github.com/GluuFederation/cloud-native-edition/commit/47878f24aaf258acdb36001f6111d2d5d94b8e66))
* hardcode opendj regional statefulset replica ([70be7df](https://www.github.com/GluuFederation/cloud-native-edition/commit/70be7dffc56c9fc2c8a9fbef8c03b40bc5eb7b7f))
* missing settings ([2056b59](https://www.github.com/GluuFederation/cloud-native-edition/commit/2056b593ef22c23f7606ee2f7a35bda01f4efde2))
* prefix serf address with release name ([c88a16a](https://www.github.com/GluuFederation/cloud-native-edition/commit/c88a16add7ac46d6069df17e4be1ef3943e43acb))
* remove extra env ([a73ee8f](https://www.github.com/GluuFederation/cloud-native-edition/commit/a73ee8f328baf28ba5357bee626aee64732f5aae))
* remove int from  cluster id prompt ([82bb8f0](https://www.github.com/GluuFederation/cloud-native-edition/commit/82bb8f09e6f3994c3861e8f0870d38c33814d93b))
* resolve address of config ([3214c84](https://www.github.com/GluuFederation/cloud-native-edition/commit/3214c84938c7d3dc1a5e5a7cb6bd845396458d4e))
* resolve config address ([7aa7563](https://www.github.com/GluuFederation/cloud-native-edition/commit/7aa75631fcd5af7f903b8ab88604cdd7269cde44))
* use multiple statefulsets for multi cluster replication ([0eaa26a](https://www.github.com/GluuFederation/cloud-native-edition/commit/0eaa26a7d96fa5f0e301adb1f52440a6320147f4))


### Documentation

* fix Changelog ([3ede717](https://www.github.com/GluuFederation/cloud-native-edition/commit/3ede717296958249f4ae25b95a236a2dc2a49858))
* update changelog ([15c1335](https://www.github.com/GluuFederation/cloud-native-edition/commit/15c1335562af659844c87d77aacd0127fff91e2e))
* update docker build ([a3eab3a](https://www.github.com/GluuFederation/cloud-native-edition/commit/a3eab3aca1c733dd5d1520ce85e7325b472d17c9))
* update helm docs ([5794556](https://www.github.com/GluuFederation/cloud-native-edition/commit/5794556590b772b895cc7d7d677c42dfc19637d6))

### [1.6.6](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.5...v1.6.6) (2021-08-02)


### Bug Fixes

* add label injection to ingress defs ([7deb1ba](https://www.github.com/GluuFederation/cloud-native-edition/commit/7deb1ba897479bbd9ce3e5c556ec0df5e9e22d7c))
* adjust dev images tags ([83d8317](https://www.github.com/GluuFederation/cloud-native-edition/commit/83d83176eafaa203734d5c3d2e281df70b4fab5b))
* autoset mysql port when installed through pygluu ([da79b38](https://www.github.com/GluuFederation/cloud-native-edition/commit/da79b38e752cd69ad07cec5e345cb6cb76be0fe5))
* set ingress class to public whenn using microk8s in pygluu ([70f90a7](https://www.github.com/GluuFederation/cloud-native-edition/commit/70f90a75767c5e3f9e9ee4adfe73d9217dfae843))

### [1.6.5](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.4...v1.6.5) (2021-07-16)


### Bug Fixes

* depreciate radius ([3b3db07](https://www.github.com/GluuFederation/cloud-native-edition/commit/3b3db078789ebbf48bd17ccfb23425d7e0e28247))
* microk8s workflow ([d7acd2d](https://www.github.com/GluuFederation/cloud-native-edition/commit/d7acd2d2d3aa2fa861273f28948ff81e01c4f2ca))
* ngnix override paths ([251fb28](https://www.github.com/GluuFederation/cloud-native-edition/commit/251fb28f6a969ad10316ab731b22561fc08da844))


### Documentation

* update docs ([c38675d](https://www.github.com/GluuFederation/cloud-native-edition/commit/c38675d1f4ad581a26b8fdf3de273cb83c8782f4))

### [1.6.4](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.3...v1.6.4) (2021-07-13)


### Bug Fixes

* oxshibboleth syntax error ([fdf73e5](https://www.github.com/GluuFederation/cloud-native-edition/commit/fdf73e5d693f88cb8b4a4196cdca0d8200a228db))

### [1.6.3](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.2...v1.6.3) (2021-07-13)


### Bug Fixes

* add hpa to helm chart services ([bb9309f](https://www.github.com/GluuFederation/cloud-native-edition/commit/bb9309f966d5b68694b0f198434d67f842d18ee4))
* add ingress control, docs, and refactor opendj service name ([c4b9c0b](https://www.github.com/GluuFederation/cloud-native-edition/commit/c4b9c0bc5c6b0ff43b6edbccf8dbce5180955c1a))
* add migration option to GUI and Terminal installation ([94244c5](https://www.github.com/GluuFederation/cloud-native-edition/commit/94244c54e3d8343f9a9625b716c7746b40a2378e))
* add port number ([fab10a9](https://www.github.com/GluuFederation/cloud-native-edition/commit/fab10a90a2661d2ba9c62903a9e1428c12fd8ad0))
* fix oxauth service name and sql mounts ([d71b92d](https://www.github.com/GluuFederation/cloud-native-edition/commit/d71b92d7c3ca4a12575f3f0571bf672adf2cb92d))
* remove creationTimestamp key ([783882c](https://www.github.com/GluuFederation/cloud-native-edition/commit/783882cefef0dafb58ecefb6e4501ae224dfe0da))
* syntax on targetCPUUtilizationPercentage ([bc3f7ae](https://www.github.com/GluuFederation/cloud-native-edition/commit/bc3f7ae8daa5410d65e2a0f5474fbe9c5881d6d3))
* update helm charts ([45fb447](https://www.github.com/GluuFederation/cloud-native-edition/commit/45fb4479785d40a92a01842cfa1d32361ef8a8dd))


### Documentation

* update chart readme ([360f30a](https://www.github.com/GluuFederation/cloud-native-edition/commit/360f30a2ab7b3150e2c9bf2332448b12b7d7734b))

### [1.6.2](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.1...v1.6.2) (2021-07-02)


### Bug Fixes

* adjust image tag for secondary charts ([d846422](https://www.github.com/GluuFederation/cloud-native-edition/commit/d84642249e3b18d392cd190433d9058bd94fc783)), closes [#338](https://www.github.com/GluuFederation/cloud-native-edition/issues/338)
* helm chart email ([9f0e56b](https://www.github.com/GluuFederation/cloud-native-edition/commit/9f0e56b21525ebfea549db130a83257d1aba71f9))

### [1.6.1](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.0...v1.6.1) (2021-06-25)


### Bug Fixes

* add oxshibboleth address param ([abf101d](https://www.github.com/GluuFederation/cloud-native-edition/commit/abf101d52662b5db8d50747a78c61e0965698b08))
* add random function for jackrabbit clusterId ([e5a6c9d](https://www.github.com/GluuFederation/cloud-native-edition/commit/e5a6c9dd005f22148a867055a9f9792826f10540))
* allow injecting user custom envs ([aff31d7](https://www.github.com/GluuFederation/cloud-native-edition/commit/aff31d736c277f8b2fa6e53333e51a782d343faf))
* default set clusterId ([2dab08c](https://www.github.com/GluuFederation/cloud-native-edition/commit/2dab08cb0d8f86288d02aa77aad8a4ed19594106))
* exit on service account not found ([1ce5380](https://www.github.com/GluuFederation/cloud-native-edition/commit/1ce53803c84ed8e884fcb87abbf4192f6e4a2e0c))
* keep storageclass during upgrades ([245de68](https://www.github.com/GluuFederation/cloud-native-edition/commit/245de686f40ffa8db847654060d817355179e876))
* mount jackrabbit admin pass ([7d537cb](https://www.github.com/GluuFederation/cloud-native-edition/commit/7d537cba71ceb8ec087ea53b43f802e1521feca5))
* postgres automatically installed address ([cb9a146](https://www.github.com/GluuFederation/cloud-native-edition/commit/cb9a1469ccae08b09612d90cdfd8b5364dd54b56))
* specify different names for jackrabbit statefulset ([dab3298](https://www.github.com/GluuFederation/cloud-native-edition/commit/dab3298a218b8ea36fc6b2dc44a412b93c8710a1))
* syntax in java option param pass ([1c1aa33](https://www.github.com/GluuFederation/cloud-native-edition/commit/1c1aa3359195cf26eb1f1c786654759bb3ec7fce))


### Documentation

* update changelog for branch 4.2 ([1cd486c](https://www.github.com/GluuFederation/cloud-native-edition/commit/1cd486cc9733b7826e4a38668eb565fb89fa7997))
* update changelong ([23ac54d](https://www.github.com/GluuFederation/cloud-native-edition/commit/23ac54d1621055bc554d520ae35e86a41fbc0e8e))

## [1.6.0](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.4.4...v1.6.0) (2021-06-01)


### Features

* **4.3:** prep ([323167a](https://www.github.com/GluuFederation/cloud-native-edition/commit/323167ac5470ed4829a6fcd957eb44a4c56152c7))
* add RDBMS support ([#324](https://www.github.com/GluuFederation/cloud-native-edition/issues/324)) ([087ef4c](https://www.github.com/GluuFederation/cloud-native-edition/commit/087ef4c8b566e549d657772662667562b821fd73))
* add spanner and google secret  support ([#321](https://www.github.com/GluuFederation/cloud-native-edition/issues/321)) ([6e9d04b](https://www.github.com/GluuFederation/cloud-native-edition/commit/6e9d04bbc5307d8387314a1d095ab9086d8a3143))
* **helm:** allow injecting volumes and volumeMounts in values ([94a93bf](https://www.github.com/GluuFederation/cloud-native-edition/commit/94a93bfcf0f53feebba0a7ae04dcaa14bc35ae4e))
* **helm:** Allow to configure liveness and readiness probe globally ([053650d](https://www.github.com/GluuFederation/cloud-native-edition/commit/053650d4a6c907757133e79f6191260602c1ec7c))
* **ldap:** add support for unencrypted connection to LDAP server ([3841456](https://www.github.com/GluuFederation/cloud-native-edition/commit/38414561009fcc299d0af66e3250bef79465cb48))
* prepare 4.3 ([f24292a](https://www.github.com/GluuFederation/cloud-native-edition/commit/f24292a7996e795544923763b92d3adfde39c5a0))


### Bug Fixes

* add annotation injection ([e2e7a97](https://www.github.com/GluuFederation/cloud-native-edition/commit/e2e7a974fbd0edbd38bdf43111c9fe4ab1e96bc9))
* forcefully patch tls-certificate secret per config job run ([8e1088e](https://www.github.com/GluuFederation/cloud-native-edition/commit/8e1088ef24b76407dabddac0d41e3da716940cd4)), closes [#302](https://www.github.com/GluuFederation/cloud-native-edition/issues/302)
* **helm:** adjust health check ([4caea7c](https://www.github.com/GluuFederation/cloud-native-edition/commit/4caea7c005ea52728b4a2516362b05ca07b21df4))
* mount path for jackrabbit admin pass ([2aad038](https://www.github.com/GluuFederation/cloud-native-edition/commit/2aad0381babcb51febf30cdce39f57437c350f58))
* passport port name ([80ff4e7](https://www.github.com/GluuFederation/cloud-native-edition/commit/80ff4e705bf024c03144305d7e9f0d0710bbad67))


### Miscellaneous Chores

* release 1.6.0 ([bad3c37](https://www.github.com/GluuFederation/cloud-native-edition/commit/bad3c3720d70ad83ffff8ea6526b300009a5ba6d))

### [1.5.9](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.5.8...v1.5.9) (2021-08-10)


### Bug Fixes

* add secondary ldap replication  ([3e18bb8da](https://www.github.com/GluuFederation/cloud-native-edition/commit/3e18bb8da52534f460a9bb03ae58f959efe716d9))
* add image secrets  ([1620a8adaa](https://www.github.com/GluuFederation/cloud-native-edition/commit/1620a8adaa14c2633d6244690dc9b01a5126b173))
* opendj service name  ([2b5f532a4c](https://www.github.com/GluuFederation/cloud-native-edition/commit/2b5f532a4cf9fecae003652084ae31d310c305c9))
* remove duplicated env  ([b5ee9a44](https://www.github.com/GluuFederation/cloud-native-edition/commit/b5ee9a4424810c41babf582697a9a66af3b368a8))


### [1.5.8](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.5.7...v1.5.8) (2021-07-28)


### Bug Fixes

* add label injection to ingress defs  ([f4df42d6b4](https://www.github.com/GluuFederation/cloud-native-edition/commit/f4df42d6b405929665d02ef6a8849595f40e4747))

### [1.5.7](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.5.6...v1.5.7) (2021-06-24)


### Bug Fixes

* allow injecting volumes and volumeMounts in values ([b1a4d89d](https://www.github.com/GluuFederation/cloud-native-edition/commit/b1a4d89d339f96b05adf7daeb6126c8145244632))

### [1.5.6](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.5.5...v1.5.6) (2021-06-21)


### Bug Fixes

* mount jackrabbit admin password ([19ed34](https://www.github.com/GluuFederation/cloud-native-edition/commit/19ed34e95a632376a0bc538f361ae2131b38f612))
* postgres automatically installed address ([4c67cc](https://www.github.com/GluuFederation/cloud-native-edition/commit/4c67cc8e93408be22c670666a63ae9eb0d81cd13))
* allow injecting user custom envs ([da585d](https://www.github.com/GluuFederation/cloud-native-edition/commit/da585da1cff34e40979147e5422a8a9956da3954))
* add oxshibboleth address param ([23398c](https://www.github.com/GluuFederation/cloud-native-edition/commit/23398cac72195295a8438ee38712863597cadd94))
* specify different names for jackrabbit statefulset ([9a247f](https://www.github.com/GluuFederation/cloud-native-edition/commit/9a247fe6c441dab10de7e734a2323cc2aba4083d))
* syntax in java option param pass ([9a247f](https://www.github.com/GluuFederation/cloud-native-edition/commit/57ef4c84c289faee55ba6fb76eba73f9d69aba10))
* add random function for jackrabbit clusterId ([a28fd0f](https://www.github.com/GluuFederation/cloud-native-edition/commit/a28fd0f85e1cb4854eca64cc914fed5c8290cefd))

### [1.5.5](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.5.4...v1.5.5) (2021-05-31)


### Bug Fixes

* passport port name ([13620bb](https://www.github.com/GluuFederation/cloud-native-edition/commit/13620bbef8a95e245e7555ab6530d015897f533d))

### [1.5.4](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.5.3...v1.5.4) (2021-05-26)


### Bug Fixes

* change ldap readiness probe check ([6cf59de](https://www.github.com/GluuFederation/cloud-native-edition/commit/6cf59deb7ec48da2ee793ee080d239fef89b0ff9))
* update chart version ([5e861a1](https://www.github.com/GluuFederation/cloud-native-edition/commit/5e861a139db55e763869bd2429a4fbaf7d9b5f49))
* update cr rotate image ([825b0e3](https://www.github.com/GluuFederation/cloud-native-edition/commit/825b0e3a8552b7aeeeacaa374462d51cb1147f69))

### [1.5.3](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.5.2...v1.5.3) (2021-05-25)


### Features

* **helm:** allow to configure liveness and readiness probe globally ([ed793e5](https://www.github.com/GluuFederation/cloud-native-edition/commit/ed793e5cf2348c902a2130f991e0a9d35c1861d4))


### Bug Fixes

* add logo ([64b6dbd](https://www.github.com/GluuFederation/cloud-native-edition/commit/64b6dbd6bbeee16e0d4c90748b6b09dd8d52b2e9))
* **helm:** adjust helm version ([7f8a158](https://www.github.com/GluuFederation/cloud-native-edition/commit/7f8a1588495721e8f7d00511b8e06ece246388d9))

### [1.5.2](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.5.1...v1.5.2) (2021-05-24)


### Bug Fixes

* add annotation injection ([157dbe6](https://www.github.com/GluuFederation/cloud-native-edition/commit/157dbe6d32b65a22e3bf770156d9b68f0b27ed1b))
* update helm version ([b54d47a](https://www.github.com/GluuFederation/cloud-native-edition/commit/b54d47a50e6a5405d9c06c68907e3599580189d6))

### [1.5.1](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.5.0...v1.5.1) (2021-05-10)


### Bug Fixes

* update scim image ([f86326d](https://www.github.com/GluuFederation/cloud-native-edition/commit/f86326d91377a43c4dcb3be7e6022419027a1bc4))

## [1.5.0](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.4.5...v1.5.0) (2021-05-06)


### Features

* release ([442267c](https://www.github.com/GluuFederation/cloud-native-edition/commit/442267ca49896251c30e1dd78bef84f1415aabbb))


### Bug Fixes

* refactor 4.2 ([#311](https://www.github.com/GluuFederation/cloud-native-edition/issues/311)) ([cfe9f69](https://www.github.com/GluuFederation/cloud-native-edition/commit/cfe9f698f77285cd42c4a2bb3e1e76dde18e3e94))

### [1.4.5](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.4.4...v1.4.5) (2021-04-26)


### Bug Fixes

* release 1.4.5 ([25bc19d](https://www.github.com/GluuFederation/cloud-native-edition/commit/25bc19dcd5dd8a38b6d9877e12b3552cb6fbdcbc))

### [1.4.4](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.4.3...v1.4.4) (2021-03-19)


### Bug Fixes

* **helm-ldap-backup:** Update chart version ([0472b4a](https://www.github.com/GluuFederation/cloud-native-edition/commit/0472b4ae32a6ef2a5c1aee2420359c26528fb3d9))
* **helm:** comment out example storageCLass.parameters ([70a289e](https://www.github.com/GluuFederation/cloud-native-edition/commit/70a289e186cd150c30036f5809c4fc8e3fcd6a8f))
* **helm:** update chart version ([62b00dc](https://www.github.com/GluuFederation/cloud-native-edition/commit/62b00dcf6651a29a016509e8be4ca6c73b5b2c02))
* **images:** Update tags ([f4ad8eb](https://www.github.com/GluuFederation/cloud-native-edition/commit/f4ad8ebce9a6b09d4d378b2a2531ba1dbc959805))
* **jackrabbit:** Set admin password for jackrabbit ([6d8b0e0](https://www.github.com/GluuFederation/cloud-native-edition/commit/6d8b0e02eab74b19380d47dff424907161d95e0c)), closes [#299](https://www.github.com/GluuFederation/cloud-native-edition/issues/299)
* **ldap:** Fix serf peers parse ([a0e0c1c](https://www.github.com/GluuFederation/cloud-native-edition/commit/a0e0c1c0a8efcb539208b2d6cc4632eeb122a092)), closes [#299](https://www.github.com/GluuFederation/cloud-native-edition/issues/299)

### [1.4.3](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.4.2...v1.4.3) (2021-03-17)


### Bug Fixes

* **certmanager:** Update image ([c1cfba7](https://www.github.com/GluuFederation/cloud-native-edition/commit/c1cfba7a73df15d73246e61fee4a4bfdf35d4584))
* **redis:** add POC comment ([43e05ad](https://www.github.com/GluuFederation/cloud-native-edition/commit/43e05ad3ea45d14cb0e535bc374b3096371d53ff))
