# Changelog

## [1.5.0](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.4.4...v1.5.0) (2021-06-01)


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
