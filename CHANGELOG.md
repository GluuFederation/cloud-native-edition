# Changelog

## [1.8.39](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.38...v1.8.39) (2024-09-03)


### Features

* change readiness and liveness checks to use script instead of http call ([#656](https://github.com/GluuFederation/cloud-native-edition/issues/656)) ([3b61542](https://github.com/GluuFederation/cloud-native-edition/commit/3b61542d9d8b2e6ba666a6b16b0b3acd86714a7e))
* **oxauth-key-rotation:** add schedule property ([#654](https://github.com/GluuFederation/cloud-native-edition/issues/654)) ([87fedbc](https://github.com/GluuFederation/cloud-native-edition/commit/87fedbc7dfaf6b0612dc82db348b9b7ab776285e))


### Bug Fixes

* update oxtrust and oxpasspoort image version to 4.5.5-2 ([#660](https://github.com/GluuFederation/cloud-native-edition/issues/660)) ([0b9a639](https://github.com/GluuFederation/cloud-native-edition/commit/0b9a6397859d1c90b034cd63b55c42f8f544b141))

## [1.8.38](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.37...v1.8.38) (2024-08-22)


### Features

* prepare assets for Gluu v4.5.5 ([#651](https://github.com/GluuFederation/cloud-native-edition/issues/651)) ([eac45e8](https://github.com/GluuFederation/cloud-native-edition/commit/eac45e8a9d37880317960676af8e014880ead0d7))


### Bug Fixes

* fix release ([4689603](https://github.com/GluuFederation/cloud-native-edition/commit/468960373effa91f760724c823ac63f125811088))

## [1.8.37](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.36...v1.8.37) (2024-07-30)


### Bug Fixes

* resolve permission denied error when installing passport library ([#648](https://github.com/GluuFederation/cloud-native-edition/issues/648)) ([ec0b9ce](https://github.com/GluuFederation/cloud-native-edition/commit/ec0b9ce09e97fadce2ffe15f81c7c74a4c29a267))

## [1.8.36](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.35...v1.8.36) (2024-07-19)


### Bug Fixes

* update image tag of upgrade job ([#646](https://github.com/GluuFederation/cloud-native-edition/issues/646)) ([644a7ad](https://github.com/GluuFederation/cloud-native-edition/commit/644a7ad7e067e026099dcc99e1a07496ee762e9a))

## [1.8.35](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.34...v1.8.35) (2024-07-15)


### Bug Fixes

* prepare release 1.8.35 ([57f336c](https://github.com/GluuFederation/cloud-native-edition/commit/57f336c9a1730a7ad29219eb06bbd536eee35517))

## [1.8.34](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.33...v1.8.34) (2024-05-30)


### Features

* add java arguments to casa and fix typo ([#632](https://github.com/GluuFederation/cloud-native-edition/issues/632)) ([7ac2227](https://github.com/GluuFederation/cloud-native-edition/commit/7ac2227cad038ec602ff00d7b027fc533f19ef76))


### Bug Fixes

* disable opendj by default as jans and flex to avoid backup job fail ([#633](https://github.com/GluuFederation/cloud-native-edition/issues/633)) ([c4b6d59](https://github.com/GluuFederation/cloud-native-edition/commit/c4b6d59dcf4e3c387c30f827a966f12ebfa0ef84))
* README.md ([ea5f6ad](https://github.com/GluuFederation/cloud-native-edition/commit/ea5f6ad7ca6e5ac7a0582e80ed608c409fafe644))


### Documentation

* add note on memory limit to avoid java args break and fix typo ([#636](https://github.com/GluuFederation/cloud-native-edition/issues/636)) ([9dfaf86](https://github.com/GluuFederation/cloud-native-edition/commit/9dfaf86afd90408e2dd08d48935f23581af2e16a))

## [1.8.33](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.32...v1.8.33) (2024-04-01)


### Bug Fixes

* address gateway customization in shib and overide ttl ([ef59ebe](https://github.com/GluuFederation/cloud-native-edition/commit/ef59ebe1dc5182f28252bb35d92afd97ad02221e)), closes [#630](https://github.com/GluuFederation/cloud-native-edition/issues/630)

## [1.8.32](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.31...v1.8.32) (2024-03-20)


### Features

* add java memory arguments in helpers file ([#628](https://github.com/GluuFederation/cloud-native-edition/issues/628)) ([31de98f](https://github.com/GluuFederation/cloud-native-edition/commit/31de98fb2888591f63541a367b1c5c54473a9f90))


### Miscellaneous Chores

* prepare for 1.8.32 release ([53546a0](https://github.com/GluuFederation/cloud-native-edition/commit/53546a03dd7358a0e6abab3710ed21dbfda2bae8))

## [1.8.31](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.30...v1.8.31) (2024-01-30)


### Bug Fixes

* add support for custom istio gateways ([#623](https://github.com/GluuFederation/cloud-native-edition/issues/623)) ([d2e03ee](https://github.com/GluuFederation/cloud-native-edition/commit/d2e03ee9a7401c4f532e4b1b5aba27149face8fb))
* gluuDocumentStoreType changes not reflected when using pygluu-kubernetes installer ([#617](https://github.com/GluuFederation/cloud-native-edition/issues/617)) ([1644fad](https://github.com/GluuFederation/cloud-native-edition/commit/1644fad597b52003366548dd43e8ce23a544548b))

## [1.8.30](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.29...v1.8.30) (2024-01-02)


### Bug Fixes

* prepare for 1.8.30 release ([a81a02b](https://github.com/GluuFederation/cloud-native-edition/commit/a81a02bc448fc54584e997cbec49674d963e0b3d))

## [1.8.29](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.28...v1.8.29) (2023-12-27)


### Features

* add custom scripts to cn ([#613](https://github.com/GluuFederation/cloud-native-edition/issues/613)) ([7e7705d](https://github.com/GluuFederation/cloud-native-edition/commit/7e7705d23a1aa4bcabc3a339b94cf0f0a8712e4f))


### Bug Fixes

* clean up zip ([c73ae4c](https://github.com/GluuFederation/cloud-native-edition/commit/c73ae4cd4c1a67de34e0c03ee57295f8331ee6a3))

## [1.8.28](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.27...v1.8.28) (2023-12-07)


### Bug Fixes

* changes to microk8s workflow ([#605](https://github.com/GluuFederation/cloud-native-edition/issues/605)) ([bfe6929](https://github.com/GluuFederation/cloud-native-edition/commit/bfe6929d662c0ce648322b19cd227adef368f77d))

## [1.8.27](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.26...v1.8.27) (2023-11-01)


### Bug Fixes

* wrong condition on sslCertFromDomain ([a153cb6](https://github.com/GluuFederation/cloud-native-edition/commit/a153cb64e21bff37e1a59334ca7db6fe71bf797a))

## [1.8.26](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.25...v1.8.26) (2023-10-20)


### Features

* add idp path to shibboleth ([#601](https://github.com/GluuFederation/cloud-native-edition/issues/601)) ([cc6f0c6](https://github.com/GluuFederation/cloud-native-edition/commit/cc6f0c608d391a4808b1e943f68519b88e00cf41))


### Bug Fixes

* add helm release as a prefix ([#598](https://github.com/GluuFederation/cloud-native-edition/issues/598)) ([2abe135](https://github.com/GluuFederation/cloud-native-edition/commit/2abe135db6af4d23b14346c1aa861923ba448629))
* handle ssl case with cert maanger. Force ssl pull from domain only ([eaf8180](https://github.com/GluuFederation/cloud-native-edition/commit/eaf818070bdb63a30493256500eb34422ebb64fb))
* release 1.8.26 ([2533b26](https://github.com/GluuFederation/cloud-native-edition/commit/2533b269e268217e2479d1f98ea4fa9ddaae06d3))

## [1.8.25](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.24...v1.8.25) (2023-09-18)


### Bug Fixes

* add default lbIP to avoid potential errors during helm install ([#590](https://github.com/GluuFederation/cloud-native-edition/issues/590)) ([76aae0d](https://github.com/GluuFederation/cloud-native-edition/commit/76aae0da656e22ca3e4d7f40a36bc4e49c6f1db9))
* update kubeAPI min versioning ([fc4450b](https://github.com/GluuFederation/cloud-native-edition/commit/fc4450b26cb156e2cf57caa1cf80255f09329b7e))
* use interval-based cronjob schedule syntax ([#594](https://github.com/GluuFederation/cloud-native-edition/issues/594)) ([e5b6628](https://github.com/GluuFederation/cloud-native-edition/commit/e5b662856a830b0cd0003dcee333d8b65731d727))

## [1.8.24](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.23...v1.8.24) (2023-09-11)


### Bug Fixes

* release helm chart 1.8.24 containing client_id AS upgrade ([b9dc33b](https://github.com/GluuFederation/cloud-native-edition/commit/b9dc33bce093b7065f133b29cf30aa82b99e61d8))

## [1.8.23](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.22...v1.8.23) (2023-09-08)


### Bug Fixes

* error converting YAML to JSON using pygluu-kubernetes installer ([#587](https://github.com/GluuFederation/cloud-native-edition/issues/587)) ([3a6f5b0](https://github.com/GluuFederation/cloud-native-edition/commit/3a6f5b071adba12416acb117ef9a8c5af39f6033))

## [1.8.22](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.21...v1.8.22) (2023-09-05)


### Bug Fixes

* prepare hotfix release ([9d5c201](https://github.com/GluuFederation/cloud-native-edition/commit/9d5c201921276ab8bd99d7d090d3e7b3895e4978))
* update image tags ([#582](https://github.com/GluuFederation/cloud-native-edition/issues/582)) ([a3865cd](https://github.com/GluuFederation/cloud-native-edition/commit/a3865cd3404026294563d5cfe161cf4b008ea383))
* update image tags ([#585](https://github.com/GluuFederation/cloud-native-edition/issues/585)) ([401058d](https://github.com/GluuFederation/cloud-native-edition/commit/401058d0a7b757bcdb6da76406bd7fe6e06a3ef2))

## [1.8.21](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.20...v1.8.21) (2023-09-01)


### Bug Fixes

* **istio:** add permissions to create tls-certificate in istio ns ([#580](https://github.com/GluuFederation/cloud-native-edition/issues/580)) ([965a7b3](https://github.com/GluuFederation/cloud-native-edition/commit/965a7b3b0d7d541b9cbc85deec4149614f1900cb))
* remove ingress.class annotation and add spec.ingressClassName  ([#567](https://github.com/GluuFederation/cloud-native-edition/issues/567)) ([ed49422](https://github.com/GluuFederation/cloud-native-edition/commit/ed49422326f0f7519b19fdae2c2aabf7ccfbfdc1))
* stale request error when having multiple pod replicas ([#572](https://github.com/GluuFederation/cloud-native-edition/issues/572)) ([aa0b30c](https://github.com/GluuFederation/cloud-native-edition/commit/aa0b30cddf658f6c5dec79a9d5dab3a9cff058e8))

## [1.8.20](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.19...v1.8.20) (2023-07-28)


### Bug Fixes

* property reference ([6b02fbc](https://github.com/GluuFederation/cloud-native-edition/commit/6b02fbcaada36ee0849e9d1be89550083d3e9150)), closes [#569](https://github.com/GluuFederation/cloud-native-edition/issues/569)

## [1.8.19](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.18...v1.8.19) (2023-07-10)


### Bug Fixes

* topology spread  constrains app label selector ([9e374ba](https://github.com/GluuFederation/cloud-native-edition/commit/9e374ba410be0b2ce8886d945dcb3095ad93a5df))

## [1.8.18](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.17...v1.8.18) (2023-07-10)


### Bug Fixes

* chore versions 4.4 ([f518668](https://github.com/GluuFederation/cloud-native-edition/commit/f51866876697024fcb02bf6e0fb786668ba39e21))
* remove unneeded configuration snippet ([#559](https://github.com/GluuFederation/cloud-native-edition/issues/559)) ([3541c1d](https://github.com/GluuFederation/cloud-native-edition/commit/3541c1d409c3db4976a4377f38ac18690897908d))


### Documentation

* kubernetes fixes ([#561](https://github.com/GluuFederation/cloud-native-edition/issues/561)) ([4dc4d95](https://github.com/GluuFederation/cloud-native-edition/commit/4dc4d95400f80d8b38afcb9e883810df54354b23))

## [1.8.17](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.16...v1.8.17) (2023-06-15)


### Bug Fixes

* **opendj:** non root user permission ([#554](https://github.com/GluuFederation/cloud-native-edition/issues/554)) ([dcbaab3](https://github.com/GluuFederation/cloud-native-edition/commit/dcbaab35daf41de0f98ab6799a8ba89e7d950511))

## [1.8.17](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.15...v1.8.16) (2023-05-08)


### Bug Fixes

* update oxauth image tag to include HttpService2 ([#547](https://github.com/GluuFederation/cloud-native-edition/issues/547)) ([b4fee12](https://github.com/GluuFederation/cloud-native-edition/commit/b4fee1251545195464ee6d4108fd09060aca57bb))

## [1.8.15](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.14...v1.8.15) (2023-04-17)


### Bug Fixes

* aws and google config ([#542](https://github.com/GluuFederation/cloud-native-edition/issues/542)) ([20e3d32](https://github.com/GluuFederation/cloud-native-edition/commit/20e3d32ed99da8a04315f6fb95f5acc2b16ddc8b))
* missing pods and pods/exec permission for default Role ([#544](https://github.com/GluuFederation/cloud-native-edition/issues/544)) ([06edf2f](https://github.com/GluuFederation/cloud-native-edition/commit/06edf2f0bf759640c98d0ae9e20df093decac9f2))

## [1.8.14](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.13...v1.8.14) (2023-04-10)


### Bug Fixes

* update image tags to resolve API UMA mode ([#539](https://github.com/GluuFederation/cloud-native-edition/issues/539)) ([f5b4d1b](https://github.com/GluuFederation/cloud-native-edition/commit/f5b4d1bbe1a428ad508cb82767cee7cac908ff7c))

## [1.8.13](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.12...v1.8.13) (2023-04-06)


### Bug Fixes

* ensure secrets are base64-encoded string ([#533](https://github.com/GluuFederation/cloud-native-edition/issues/533)) ([cca808b](https://github.com/GluuFederation/cloud-native-edition/commit/cca808b2fdfdb3247ce1051bdd196ee5d1466650))
* get cert and key regardless of secrets layer ([#531](https://github.com/GluuFederation/cloud-native-edition/issues/531)) ([ffccc0a](https://github.com/GluuFederation/cloud-native-edition/commit/ffccc0a4512eb30b79e0ef6ff8de2c56a7e6a410))
* set unique session-cookie-name of ingresses to avoid collision ([#537](https://github.com/GluuFederation/cloud-native-edition/issues/537)) ([1629f8e](https://github.com/GluuFederation/cloud-native-edition/commit/1629f8ea4681cf0eba6e530f1fad5bfb3bfab9ad))


### Documentation

* customization ([#535](https://github.com/GluuFederation/cloud-native-edition/issues/535)) ([2c53800](https://github.com/GluuFederation/cloud-native-edition/commit/2c5380077feb8e34ba965942e8e166beb7596967))

## [1.8.12](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.11...v1.8.12) (2023-03-21)


### Bug Fixes

* add support for injecting affinty and nodeSelector ([91be257](https://github.com/GluuFederation/cloud-native-edition/commit/91be257c8988d895190f5eecbdf204a0f80224be))

## [1.8.11](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.10...v1.8.11) (2023-03-20)


### Bug Fixes

* add support for toleration lists in values.yaml ([005fabd](https://github.com/GluuFederation/cloud-native-edition/commit/005fabd04941ac52c3425b36616904f48fa34366)), closes [#527](https://github.com/GluuFederation/cloud-native-edition/issues/527)

## [1.8.10](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.9...v1.8.10) (2023-03-15)


### Bug Fixes

* release 1.8.9 ([11d48dd](https://github.com/GluuFederation/cloud-native-edition/commit/11d48dd79f92ca9a9b7a0104a9a1a834fd778500))
* update images tags ([d35a24f](https://github.com/GluuFederation/cloud-native-edition/commit/d35a24f2f4552c38e8ff08d741ae342563b6fc01))

## [1.8.9](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.8...v1.8.9) (2023-03-09)


### Bug Fixes

* release 1.8.10 ([54a5762](https://github.com/GluuFederation/cloud-native-edition/commit/54a5762d8ede0b05b99b4048cf3c61ae1ef84684))
* release 1.8.9 ([5ae27c6](https://github.com/GluuFederation/cloud-native-edition/commit/5ae27c6ae9225ece7ca316388c7c502df886611a))
* release 1.8.9 with memory leak fix ([e246191](https://github.com/GluuFederation/cloud-native-edition/commit/e246191901665d7701870dd12fa8bfb08b998a2f))

## [1.8.8](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.7...v1.8.8) (2023-03-06)


### Bug Fixes

* add aws envs and unquote aws config ([7e40c38](https://github.com/GluuFederation/cloud-native-edition/commit/7e40c38534a032ae0f75d0d046a70635d6f003ab))

## [1.8.7](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.6...v1.8.7) (2023-03-01)


### Bug Fixes

* upstream fixes ([7357cae](https://github.com/GluuFederation/cloud-native-edition/commit/7357cae12c4cbe963992f4d023163e81aecb6a57))

## [1.8.6](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.5...v1.8.6) (2023-02-09)


### Bug Fixes

* upgrade job arbs section ([8fcd713](https://github.com/GluuFederation/cloud-native-edition/commit/8fcd713ae045fa7d8cf671c0eb1f21ca53f585cf))

## [1.8.5](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.4...v1.8.5) (2023-02-09)


### Bug Fixes

* add preStop configuration ([76e67a9](https://github.com/GluuFederation/cloud-native-edition/commit/76e67a943122f4303526e78c7c1f09decaa6307a))

## [1.8.4](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.3...v1.8.4) (2023-02-06)


### Features

* add appLoggers for jackrabbit ([81cb26b](https://github.com/GluuFederation/cloud-native-edition/commit/81cb26bf05152afb78b0b9b838db52cb33d12374))


### Bug Fixes

* exit upgrade job in istio correctly ([7a565c9](https://github.com/GluuFederation/cloud-native-edition/commit/7a565c9cec4f38b39796b05e06eacf33f4f407ce))
* use appLoggers ([c19e86d](https://github.com/GluuFederation/cloud-native-edition/commit/c19e86d50dcae376f88c85ce80a8ec84bcaf92f6))


### Miscellaneous Chores

* release 1.8.4 ([492c1c5](https://github.com/GluuFederation/cloud-native-edition/commit/492c1c50c6b48c3c5303bd974350d8927aeae059))

## [1.8.3](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.2...v1.8.3) (2023-01-23)


### Bug Fixes

* upgrade syntax and sts additional volumeMount ([f499e16](https://github.com/GluuFederation/cloud-native-edition/commit/f499e16796ac2cafe6c127814b9bfaa1e4390f59))

## [1.8.2](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.1...v1.8.2) (2023-01-20)


### Bug Fixes

* appVersion ([46d8afd](https://github.com/GluuFederation/cloud-native-edition/commit/46d8afd1fe943dc9d5110798d93bf05ef3f00ebb))
* permission issues and allow for security override in non FQDN setups ([5bdb12f](https://github.com/GluuFederation/cloud-native-edition/commit/5bdb12fe8404c4010feb2f46798fdfef6fbbefc6))

## [1.8.1](https://github.com/GluuFederation/cloud-native-edition/compare/v1.8.0...v1.8.1) (2023-01-13)


### Bug Fixes

* add init containers for adjusting ownership on upgrade ([c1c80d9](https://github.com/GluuFederation/cloud-native-edition/commit/c1c80d9a02b7747d7838b33dccbd4312f9b92a65))
* add init containers for adjusting ownership on upgrade ([dd9359f](https://github.com/GluuFederation/cloud-native-edition/commit/dd9359fca732645f512708a0525b199b089f2ef4))
* ass fsGroup for sts ([3158281](https://github.com/GluuFederation/cloud-native-edition/commit/315828191e0ec582734f20492b6651c8b0e7a4e2))
* update opendj to v4.5.0-3 ([#507](https://github.com/GluuFederation/cloud-native-edition/issues/507)) ([0451de1](https://github.com/GluuFederation/cloud-native-edition/commit/0451de11ccc6c0159e3643089ab822d9f7b673ed))

## [1.8.0](https://github.com/GluuFederation/cloud-native-edition/compare/v1.7.9...v1.8.0) (2023-01-02)


### Features

* add AWS secret manager support ([#494](https://github.com/GluuFederation/cloud-native-edition/issues/494)) ([35c8010](https://github.com/GluuFederation/cloud-native-edition/commit/35c8010d0a4b8892b389e725dd72a7df1d9446e4))
* add security context ([#501](https://github.com/GluuFederation/cloud-native-edition/issues/501)) ([4b85f4f](https://github.com/GluuFederation/cloud-native-edition/commit/4b85f4f7b1956d0a418dae2e0cb3a218b0a9611b))

## [1.7.9](https://github.com/GluuFederation/cloud-native-edition/compare/v1.7.8...v1.7.9) (2022-11-16)


### Features

* **charts:** add pdb and topology spread constrants ([ffaa227](https://github.com/GluuFederation/cloud-native-edition/commit/ffaa227e84ca3b6aeb2a4509e521d7ee520e69d5))


### Miscellaneous Chores

* release 1.7.9 ([fd07327](https://github.com/GluuFederation/cloud-native-edition/commit/fd0732747f371e14d040ddd47d7650e8ba3997b7))

## [1.7.8](https://github.com/GluuFederation/cloud-native-edition/compare/v1.7.7...v1.7.8) (2022-11-14)


### Bug Fixes

* add detailed oxShibboleth apploggers https://github.com/GluuFederation/docker-oxshibboleth/issues/48 ([0733a3b](https://github.com/GluuFederation/cloud-native-edition/commit/0733a3be662f3ac8baa74fa547f0114ceec71d11))
* keep oxsshipoleth disabled by default ([7632a89](https://github.com/GluuFederation/cloud-native-edition/commit/7632a89dcf19062270f4549a2d78fcde4a6ea511))

## [1.7.7](https://github.com/GluuFederation/cloud-native-edition/compare/v1.7.6...v1.7.7) (2022-10-04)


### Bug Fixes

* indentation on cronjob ([d09a7f5](https://github.com/GluuFederation/cloud-native-edition/commit/d09a7f57870c443d3986c741ff2174fb7e681fb7))
* update cronjob api versions ([b9998b8](https://github.com/GluuFederation/cloud-native-edition/commit/b9998b8fe7429ff377ec882fbc43048158250462))

## [1.7.6](https://github.com/GluuFederation/cloud-native-edition/compare/v1.7.5...v1.7.6) (2022-09-06)


### Bug Fixes

* incorrect conversion of global.oxshibboleth.appLoggers value ([#469](https://github.com/GluuFederation/cloud-native-edition/issues/469)) ([35d7752](https://github.com/GluuFederation/cloud-native-edition/commit/35d775249bdd202ab910f93433b96b399781b7c5))
* **istio:** revisit istio virtualservices ([#475](https://github.com/GluuFederation/cloud-native-edition/issues/475)) ([d6f6b99](https://github.com/GluuFederation/cloud-native-edition/commit/d6f6b9995d906f7a477ccc85fc75ee3249a1ffe4))

## [1.7.5](https://github.com/GluuFederation/cloud-native-edition/compare/v1.7.4...v1.7.5) (2022-08-17)


### Bug Fixes

* remove cluster role bindings ([#466](https://github.com/GluuFederation/cloud-native-edition/issues/466)) ([ae50dde](https://github.com/GluuFederation/cloud-native-edition/commit/ae50dde784e1a6c6caa090f36b8bc056bba6b2b3))

## [1.7.4](https://github.com/GluuFederation/cloud-native-edition/compare/v1.7.3...v1.7.4) (2022-08-08)


### Bug Fixes

* add job ttl and set deault to 300s ([#461](https://github.com/GluuFederation/cloud-native-edition/issues/461)) ([861dc48](https://github.com/GluuFederation/cloud-native-edition/commit/861dc480051242daea57f6970180b24729f2080f))

## [1.7.3](https://github.com/GluuFederation/cloud-native-edition/compare/v1.7.2...v1.7.3) (2022-08-01)


### Bug Fixes

* release `1.7.3` ([97a3093](https://github.com/GluuFederation/cloud-native-edition/commit/97a3093d1109ca859da87f4248f98fc4a2dfe086))

## [1.7.2](https://github.com/GluuFederation/cloud-native-edition/compare/v1.7.1...v1.7.2) (2022-07-24)


### Bug Fixes

* add 101 ox ldif as yaml ([1f1155e](https://github.com/GluuFederation/cloud-native-edition/commit/1f1155eaae0882954ca0628e83be56a8078335e2))
* add 101-ox for ldap upgrading ([3071303](https://github.com/GluuFederation/cloud-native-edition/commit/30713038aa43e48b613c776133c857dd5720a6dc))
* cherry committed from 4.3 ([47794fc](https://github.com/GluuFederation/cloud-native-edition/commit/47794fc1289e68000fac4db20170748ca1df6f0b))
* **gui:** avoid fixed version pinning for dependencies ([#440](https://github.com/GluuFederation/cloud-native-edition/issues/440)) ([1b8b932](https://github.com/GluuFederation/cloud-native-edition/commit/1b8b93299c791645889353c352ce0142015cb950))
* resolve Mapping from collections module ([#456](https://github.com/GluuFederation/cloud-native-edition/issues/456)) ([2acc537](https://github.com/GluuFederation/cloud-native-edition/commit/2acc5370d8634b51b95a53ff3dfe59c06c06231c))
* resources assignments ([#448](https://github.com/GluuFederation/cloud-native-edition/issues/448)) ([5a3f8cc](https://github.com/GluuFederation/cloud-native-edition/commit/5a3f8cc1e3b439a5a66ceacfd973f302d7ac8057))

### [1.7.1](https://github.com/GluuFederation/cloud-native-edition/compare/v1.7.0...v1.7.1) (2022-05-09)


### Bug Fixes

* pass spanner emulator env ([1565347](https://github.com/GluuFederation/cloud-native-edition/commit/1565347d600b66d7a37dce6384eb3e6ab26226c1))

## [1.7.0](https://github.com/GluuFederation/cloud-native-edition/compare/v1.6.18...v1.7.0) (2022-05-06)


### Bug Fixes

* handle ALB edge case ([4c4b51a](https://github.com/GluuFederation/cloud-native-edition/commit/4c4b51a999f5e5f586cd08d0946af6fdbb72c59d))


### Miscellaneous Chores

* release 1.7.0 ([7066ae2](https://github.com/GluuFederation/cloud-native-edition/commit/7066ae2efd113deaab1f471395ed277766bf5c58))

### [1.7.0](https://github.com/GluuFederation/cloud-native-edition/compare/v1.6.17...v1.7.0) (2022-03-21)


### Bug Fixes

* **cr:** mount missing google creds when using spanner as a persistence ([ff2dc86](https://github.com/GluuFederation/cloud-native-edition/commit/ff2dc8686f725de2d5fb20f5eea518d8a4fe6556)), closes [#413](https://github.com/GluuFederation/cloud-native-edition/issues/413)
* **ingress:** add device-code and firebase messaging ingress ([a7fe730](https://github.com/GluuFederation/cloud-native-edition/commit/a7fe7305da32f3ece33f89a3063e6424840539ed))

### [1.6.17](https://github.com/GluuFederation/cloud-native-edition/compare/v1.6.16...v1.6.17) (2022-03-11)


### Bug Fixes

* **alb:** hide alb prompt for non alb setups ([b05dee3](https://github.com/GluuFederation/cloud-native-edition/commit/b05dee3952f613d1db7116e1048989559261ebe8))
* **jackrabbit:** default clusterid ([9ae84c7](https://github.com/GluuFederation/cloud-native-edition/commit/9ae84c7f109acc2c57befbb2f5cee50d3b1ee862))
* **lb:** stop the change of the lb address after getting it when using nginx ([2f986bd](https://github.com/GluuFederation/cloud-native-edition/commit/2f986bd172138f01010240cac603a6f5cd415616))
* **postgres:** update postgres helm keys ([c305ff3](https://github.com/GluuFederation/cloud-native-edition/commit/c305ff3f29dcb6462bb178bd5b2e1678360939fb))

### [1.6.16](https://github.com/GluuFederation/cloud-native-edition/compare/v1.6.15...v1.6.16) (2022-02-15)


### Bug Fixes

* **alb:** force arn to be used ([95b6e26](https://github.com/GluuFederation/cloud-native-edition/commit/95b6e263ba05cdd2f0565e40a4adaf74528a5863))
* **helm:** remove v5 pacakges ([392f4f2](https://github.com/GluuFederation/cloud-native-edition/commit/392f4f23c7a0fe7ce86d94836f7ef3a0c9b0a2f6))
* **helm:** remove v5 packages ([c80ed55](https://github.com/GluuFederation/cloud-native-edition/commit/c80ed551ac1fa29a22e34ff8eff34f9d2a0a3e23))
* **pygluu:** remove alb parse in helm installation. ([9040783](https://github.com/GluuFederation/cloud-native-edition/commit/904078388c60c566b5cbbe5da59e158f8a3998f9))
* **version:** update dev tags ([dab67fa](https://github.com/GluuFederation/cloud-native-edition/commit/dab67fab0c584f7925fe567e9d7f306c25978a88))

### [1.6.15](https://github.com/GluuFederation/cloud-native-edition/compare/v1.6.14...v1.6.15) (2022-01-17)


### Bug Fixes

* add injection of service properties ([73a417f](https://github.com/GluuFederation/cloud-native-edition/commit/73a417f81cc5ac7514d2364b82c5666403f7a36a))
* app loggers ([#396](https://github.com/GluuFederation/cloud-native-edition/issues/396)) ([5e309eb](https://github.com/GluuFederation/cloud-native-edition/commit/5e309ebcb60579e83a301ba902dc693261156568))
* update Kubernetes version ([#389](https://github.com/GluuFederation/cloud-native-edition/issues/389)) ([ca1e64c](https://github.com/GluuFederation/cloud-native-edition/commit/ca1e64c4993b57b32f15917c14efb882c5c957a2))

### [1.6.14](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.13...v1.6.14) (2021-11-16)


### Bug Fixes

* refactor values calls ([a199105](https://www.github.com/GluuFederation/cloud-native-edition/commit/a199105f691c2241716ea3dd5bc4e0e0537986d6))

### [1.6.13](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.12...v1.6.13) (2021-11-16)


### Bug Fixes

* alb ingress reference ([2a5a971](https://www.github.com/GluuFederation/cloud-native-edition/commit/2a5a971df38d7a3bf1b5edee0f29468cf6aff786))

### [1.6.12](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.12...v1.6.12) (2021-11-16)


### Bug Fixes

* sonar integration workflow ([#379](https://www.github.com/GluuFederation/cloud-native-edition/issues/379)) ([65a18d0](https://www.github.com/GluuFederation/cloud-native-edition/commit/65a18d0104c4b4e802fbdd408cf46d3e839e251a))
* add per ingress annotations ([44d4359](https://www.github.com/GluuFederation/cloud-native-edition/commit/44d43591753392e2b2cfb29e3128b6ee9f235d71))
* use helm hooks ([#376](https://www.github.com/GluuFederation/cloud-native-edition/issues/376)) ([e8f3929](https://www.github.com/GluuFederation/cloud-native-edition/commit/e8f3929a285b2f86973116677e03fd33312f6d0c))

### Miscellaneous Chores

* release 1.6.12 ([33827b2](https://www.github.com/GluuFederation/cloud-native-edition/commit/33827b2a957dba0fe2b229ecb924afa8444731ae))

### [1.6.11](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.10...v1.6.11) (2021-10-08)


### Bug Fixes

* add labels annotations ([#369](https://www.github.com/GluuFederation/cloud-native-edition/issues/369)) ([2b4a67c](https://www.github.com/GluuFederation/cloud-native-edition/commit/2b4a67c71cc2ec0abfd8e6d19bfc77fbd9057bf4))

### [1.6.10](https://www.github.com/GluuFederation/cloud-native-edition/compare/v1.6.9...v1.6.10) (2021-10-06)


### Bug Fixes

* add alb chart ([#366](https://www.github.com/GluuFederation/cloud-native-edition/issues/366)) ([56b22fc](https://www.github.com/GluuFederation/cloud-native-edition/commit/56b22fc8507f478d69d6b1d872dc9634e88847a2))

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
