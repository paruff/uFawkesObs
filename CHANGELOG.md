# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0-beta.1](https://github.com/paruff/uFawkesObs/compare/v0.3.25-alpha.1...v0.4.0-beta.1) (2026-09-24)


### Added

* **test:** migrate Loki integration tests to Testcontainers ([7c5e5dd](https://github.com/paruff/uFawkesObs/commit/7c5e5dd7cc4c9bdcac502df3c5a277765b6f09e7))
* **test:** migrate Loki integration tests to Testcontainers ([6778447](https://github.com/paruff/uFawkesObs/commit/67784476ec40cd90ae7dd1f563b6ec826493d655))
* **test:** migrate Tempo integration tests to Testcontainers ([94c4b55](https://github.com/paruff/uFawkesObs/commit/94c4b551f0a92e0724a77bde716f0e21790bc399))
* **test:** migrate Tempo integration tests to Testcontainers ([28f275d](https://github.com/paruff/uFawkesObs/commit/28f275d14f6eac9b8e6b29fa7ce30f79101730bb))


### Fixed

* **test:** use a unique team_id per DORA acceptance run, not a fixed one ([c5e03d4](https://github.com/paruff/uFawkesObs/commit/c5e03d4d7502ae8885652ab1e7594d81baa89bf2))
* **test:** use a unique team_id per DORA acceptance run, not a fixed one ([1415e26](https://github.com/paruff/uFawkesObs/commit/1415e265306487513d5b83808b4807eedb49d375))
* **test:** wait for Tempo's actual /ready, not just its open port ([cb9c06e](https://github.com/paruff/uFawkesObs/commit/cb9c06e1e6e7c48f9364ea948441d365196086a8))


### Docs

* delete docs/plan.md, tracker is the source of truth ([#348](https://github.com/paruff/uFawkesObs/issues/348)) ([8c53318](https://github.com/paruff/uFawkesObs/commit/8c533185555a4023e29fe2dae7ff6c83226f5858))
* delete docs/plan.md, tracker is the source of truth ([#348](https://github.com/paruff/uFawkesObs/issues/348)) ([56a31cd](https://github.com/paruff/uFawkesObs/commit/56a31cd944f7ff26ff960a494b8d06ba05def4f8))
* mark project status as beta, six of seven LB-* items closed ([b7cc530](https://github.com/paruff/uFawkesObs/commit/b7cc530d046b666e6401b971784d9b5f7e5b78c6))
* mark project status as beta, six of seven LB-* items closed ([6ff5a08](https://github.com/paruff/uFawkesObs/commit/6ff5a0844e70c1a407a5725f4cf89643c3622c02))
* **model-policy:** remove hardcoded model/provider names, keep grades ([e813338](https://github.com/paruff/uFawkesObs/commit/e8133384bf9be2ecd8b6450b12c7db2b4cedefd6))
* **model-policy:** remove hardcoded model/provider names, keep grades ([2b9a0b5](https://github.com/paruff/uFawkesObs/commit/2b9a0b5fb314f85db5dfdeebcc677c215b16ae96))
* **test:** describe all five pyramid tiers, honest partial state ([e64a541](https://github.com/paruff/uFawkesObs/commit/e64a54121f3151d67eef5c9cb7b2b70e92b2961c))
* **test:** describe all five pyramid tiers, honest partial state ([ad9a638](https://github.com/paruff/uFawkesObs/commit/ad9a63841f42ae34b2b06042bfcfc9e6881a3edc))

## [0.3.25-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.24-alpha.1...v0.3.25-alpha.1) (2026-09-24)


### Added

* **test:** InSpec profile for AGENTS.md §4 live-stack conformance ([#444](https://github.com/paruff/uFawkesObs/issues/444)) ([7c0c924](https://github.com/paruff/uFawkesObs/commit/7c0c924c7656bd3b53baa0986850d7973dedaf5d))
* **test:** Testcontainers spike for integration tier ([b5603b4](https://github.com/paruff/uFawkesObs/commit/b5603b42d89aa11d0c437a1f084f2ffb15cdb302))
* **test:** Testcontainers spike for integration tier ([d30bc5a](https://github.com/paruff/uFawkesObs/commit/d30bc5ab2e47934fe5c3490c100bfbaee6c4ee5d))


### Fixed

* **deps:** rename lock files so Dependabot cannot partially bump them ([#419](https://github.com/paruff/uFawkesObs/issues/419)) ([b9e7311](https://github.com/paruff/uFawkesObs/commit/b9e731122ca000d91b346b4af6ac717f643ffffe))
* **dora:** persist failed deployment events instead of dropping them ([#412](https://github.com/paruff/uFawkesObs/issues/412)) ([de45f49](https://github.com/paruff/uFawkesObs/commit/de45f49aa8aad21692a8455876bec1cc7d7cdc18))


### Docs

* add testing pyramid plan (Testcontainers + InSpec) ([#418](https://github.com/paruff/uFawkesObs/issues/418)) ([d859523](https://github.com/paruff/uFawkesObs/commit/d85952322e3cb48e8c2f9a2a3ff45f005ce89bf7))
* fold test-suite determinism audit into DETERMINISM.md ([#402](https://github.com/paruff/uFawkesObs/issues/402)) ([9b29041](https://github.com/paruff/uFawkesObs/commit/9b2904143e73026df6982c185570c0fdb52be512))


### Chores

* **deps:** update aiohttp requirement from &gt;=3.14 to &gt;=3.14.3 in /dora/compute ([94007ef](https://github.com/paruff/uFawkesObs/commit/94007ef0e26961a168abee609ea3ea6e6b028b13))
* **deps:** update aiohttp requirement from &gt;=3.14 to &gt;=3.14.3 in /tests/unit ([01f9fae](https://github.com/paruff/uFawkesObs/commit/01f9fae77f89398d3a7ceb7406cf6506b95b32ae))
* **deps:** update aiohttp requirement in /dora/compute ([fa81fa7](https://github.com/paruff/uFawkesObs/commit/fa81fa7ccd95207aa2547912281613a569685b1f))
* **deps:** update aiohttp requirement in /tests/unit ([57948d9](https://github.com/paruff/uFawkesObs/commit/57948d9a274c25b6a8feef784bd68aa35ff50068))
* **deps:** update aiosqlite requirement from &gt;=0.20 to &gt;=0.22.1 in /dora/ingestion ([86dd7e0](https://github.com/paruff/uFawkesObs/commit/86dd7e09b26082bb872ae44a2f7921d4770d1495))
* **deps:** update aiosqlite requirement in /dora/compute ([#441](https://github.com/paruff/uFawkesObs/issues/441)) ([e379863](https://github.com/paruff/uFawkesObs/commit/e379863dbe59416a0ade287e9b450dc98cbf9432))
* **deps:** update aiosqlite requirement in /dora/ingestion ([43a78be](https://github.com/paruff/uFawkesObs/commit/43a78bea6ae9c165cc982965a90ef8c97ed02c6e))
* **deps:** update fastapi requirement from &gt;=0.110 to &gt;=0.141.1 in /dora/ingestion ([55d7005](https://github.com/paruff/uFawkesObs/commit/55d7005c4f89efe39332ebaeea51a047ceacdaf3))
* **deps:** update fastapi requirement from &gt;=0.110 to &gt;=0.141.1 in /tests/unit ([c3bd8f0](https://github.com/paruff/uFawkesObs/commit/c3bd8f043e4a54208abd3f8dd1de3fd8a48e7311))
* **deps:** update fastapi requirement in /dora/ingestion ([12ecd0e](https://github.com/paruff/uFawkesObs/commit/12ecd0eff4fdb15ef04267dc34f33c72020e7e2b))
* **deps:** update fastapi requirement in /tests/unit ([815c0c5](https://github.com/paruff/uFawkesObs/commit/815c0c5da2bc988b2c692c4d56e06693f09d24eb))
* **deps:** update jsonschema requirement from &gt;=4.20 to &gt;=4.26.0 in /dora/ingestion ([b8bbe98](https://github.com/paruff/uFawkesObs/commit/b8bbe980c533b00254a9864291704d03072953ea))
* **deps:** update jsonschema requirement in /dora/compute ([#440](https://github.com/paruff/uFawkesObs/issues/440)) ([f5a2b76](https://github.com/paruff/uFawkesObs/commit/f5a2b765403bce50b1167e85890e4c68283feed2))
* **deps:** update jsonschema requirement in /dora/ingestion ([e81a62d](https://github.com/paruff/uFawkesObs/commit/e81a62d1fdd26deb5d9a65753bdb3d5a81aa0bbe))
* **deps:** update opentelemetry-exporter-otlp-proto-http requirement ([4e3dbca](https://github.com/paruff/uFawkesObs/commit/4e3dbca4ad35e6db4922ffca34318c50fabb45f4))
* **deps:** update opentelemetry-exporter-otlp-proto-http requirement from &gt;=1.22.0 to &gt;=1.44.0 in /tests/acceptance ([f0587d4](https://github.com/paruff/uFawkesObs/commit/f0587d475f1dadcbc1cb20be0d8aa4918e7a3402))
* **deps:** update pytest requirement from &gt;=7.4.3 to &gt;=9.1.1 in /tests/integration ([1bdf513](https://github.com/paruff/uFawkesObs/commit/1bdf5138a0de8a8220068e8078157398877f259f))
* **deps:** update pytest requirement from &gt;=7.4.3 to &gt;=9.1.1 in /tests/unit ([5a843cd](https://github.com/paruff/uFawkesObs/commit/5a843cd86577d7057a4a45b95f8c717b39926f23))
* **deps:** update pytest requirement from &gt;=8.0 to &gt;=9.1.1 in /tests/acceptance ([205c47e](https://github.com/paruff/uFawkesObs/commit/205c47ebfbe36b0077e052df139407b37f8c4b00))
* **deps:** update pytest requirement in /tests/acceptance ([39f1b48](https://github.com/paruff/uFawkesObs/commit/39f1b4849980cfe1346d45d01f633b0ae9aa354d))
* **deps:** update pytest requirement in /tests/integration ([cbdde5f](https://github.com/paruff/uFawkesObs/commit/cbdde5f2b7d3033801fadd8dcb84cd2da8c7ac54))
* **deps:** update pytest requirement in /tests/unit ([63f6a34](https://github.com/paruff/uFawkesObs/commit/63f6a3405dc084ad8e0c789ee2fe8a346d450c03))
* **deps:** update pytest-bdd requirement from &gt;=6.1.1 to &gt;=8.1.0 in /tests/integration ([7f07095](https://github.com/paruff/uFawkesObs/commit/7f0709583e2d4b78fdc1c0ba257a5e51117a6d70))
* **deps:** update pytest-bdd requirement in /tests/integration ([1c13042](https://github.com/paruff/uFawkesObs/commit/1c13042897089630b0f0f718b5cc287601ab6f18))
* **deps:** update python-dotenv requirement from &gt;=1.0.0 to &gt;=1.2.3 in /tests/integration ([369d54e](https://github.com/paruff/uFawkesObs/commit/369d54e7d3efe848e9552676873c881abd24b156))
* **deps:** update python-dotenv requirement in /tests/integration ([e63d515](https://github.com/paruff/uFawkesObs/commit/e63d5156583070e6707d631ec342ba98bc8d4c3b))
* **deps:** update pyyaml requirement from &gt;=6.0 to &gt;=6.0.3 in /tests/acceptance ([c3582a1](https://github.com/paruff/uFawkesObs/commit/c3582a1b9d6de52289409763b5e600d3608425f8))
* **deps:** update pyyaml requirement from &gt;=6.0.1 to &gt;=6.0.3 in /tests/integration ([346d358](https://github.com/paruff/uFawkesObs/commit/346d35817cb0b6578b2f4788fc0a3da8d6519209))
* **deps:** update pyyaml requirement in /tests/acceptance ([9ab21e8](https://github.com/paruff/uFawkesObs/commit/9ab21e8f594211eeb3c66572dba96fad7fbf6c08))
* **deps:** update pyyaml requirement in /tests/integration ([b287b28](https://github.com/paruff/uFawkesObs/commit/b287b285525bc174d970b25b251e7209eefb7be5))
* **deps:** update requests requirement from &gt;=2.31 to &gt;=2.34.2 in /tests/unit ([fd6ea81](https://github.com/paruff/uFawkesObs/commit/fd6ea81aa25e405a567afbb894ec2bcebc1b0821))
* **deps:** update requests requirement from &gt;=2.31.0 to &gt;=2.34.2 in /tests/acceptance ([2f32587](https://github.com/paruff/uFawkesObs/commit/2f32587be61ae60209f74c039e11c16eb6e4559b))
* **deps:** update requests requirement from &gt;=2.31.0 to &gt;=2.34.2 in /tests/integration ([6f35fe5](https://github.com/paruff/uFawkesObs/commit/6f35fe5d4c9fc4e8ed41297d3119299c6274b86a))
* **deps:** update requests requirement in /tests/acceptance ([2c2b8d2](https://github.com/paruff/uFawkesObs/commit/2c2b8d25f1f53d2e2872232075bab1921f6c67e8))
* **deps:** update requests requirement in /tests/integration ([45d334e](https://github.com/paruff/uFawkesObs/commit/45d334e22e13b611da0c4b849b963a4830dc1d7f))
* **deps:** update requests requirement in /tests/unit ([d43bf96](https://github.com/paruff/uFawkesObs/commit/d43bf962e61a52e349c8d3d2ed8b6e13c34dbb9d))
* **deps:** update uvicorn requirement from &gt;=0.29 to &gt;=0.53.0 in /dora/ingestion ([d355c3b](https://github.com/paruff/uFawkesObs/commit/d355c3bf27569dbd6b46f995a5f588b02664cbf8))
* **deps:** update uvicorn requirement in /dora/ingestion ([f40dc80](https://github.com/paruff/uFawkesObs/commit/f40dc8027f0bc926310f819847badffba65e8073))
* **deps:** update yamllint requirement from &gt;=1.33.0 to &gt;=1.38.0 in /tests/unit ([0a2af56](https://github.com/paruff/uFawkesObs/commit/0a2af568f464d71e257b705c451508b4c05ec0a7))
* **deps:** update yamllint requirement in /tests/unit ([58c3bb9](https://github.com/paruff/uFawkesObs/commit/58c3bb9d6f314c7396df2560b2f4926c593ede06))

## [0.3.24-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.23-alpha.1...v0.3.24-alpha.1) (2026-09-23)


### Fixed

* implement determinism Should items (relock, digests, dependabot) ([1165d94](https://github.com/paruff/uFawkesObs/commit/1165d942a00fc7780e1166a17921087b8624c884))
* **test:** make image-version tests digest-aware ([254953b](https://github.com/paruff/uFawkesObs/commit/254953b6d1fa9d157adc43a46d58b8b32eab61f9))
* **test:** strip digest suffix in the other two tag-extraction tests ([fca1078](https://github.com/paruff/uFawkesObs/commit/fca10781362fffccae1be0a36a08a59a18237122))

## [0.3.23-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.22-alpha.1...v0.3.23-alpha.1) (2026-09-23)


### Fixed

* **ci:** pin runner images and Python patch versions for determinism ([3968704](https://github.com/paruff/uFawkesObs/commit/3968704c0861570c00c1bef2c586c031f51f7cfd))
* **ci:** SHA-pin paruff/ufawkespipe reusable workflows ([4b70b4c](https://github.com/paruff/uFawkesObs/commit/4b70b4c549b9f574d9602aed39fdafeaebc3ef57))
* **deps:** extend lock-file pattern to remaining requirements files ([46b1f81](https://github.com/paruff/uFawkesObs/commit/46b1f817362c842a7828d59dbf22c26322e5dc6c))

## [0.3.22-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.21-alpha.1...v0.3.22-alpha.1) (2026-09-23)


### Added

* **acceptance:** Phase 2 — cross-plane telemetry contract tests ([c5d26c9](https://github.com/paruff/uFawkesObs/commit/c5d26c9480267a9735ec72b1cb3ca674d724f2b0))
* **acceptance:** Phase 2 — cross-plane telemetry contract tests ([49fe6a6](https://github.com/paruff/uFawkesObs/commit/49fe6a69eb3faf49255d62e3db9b20560bf10285))
* **acceptance:** Phase 3 — SLI/SLO test gates (OBS-SLI-001-006) ([592c4f4](https://github.com/paruff/uFawkesObs/commit/592c4f453c8acc80feac305f3126f7c974005e04))
* **acceptance:** Phase 3 — SLI/SLO test gates (OBS-SLI-001-006) ([c6c7f7d](https://github.com/paruff/uFawkesObs/commit/c6c7f7d78933d5d3f0794604fcbfd4018b21bf67))
* **acceptance:** Phase 4 — Synthetic Workload Generator ([2a8547e](https://github.com/paruff/uFawkesObs/commit/2a8547edaa71b9b2b43da5ad70ee3374819f797e))
* **acceptance:** Phase 4 — Synthetic workload generators (DORA + registry) ([b531785](https://github.com/paruff/uFawkesObs/commit/b5317859b7a5cbcdfbfe31e3407b6b9083f4d74e))
* **acceptance:** Phase 5 — Chaos & Failure Injection (DORA + registry) ([f2f9a25](https://github.com/paruff/uFawkesObs/commit/f2f9a2586c776766f3bbc884ad4954d40baad624))
* **acceptance:** Phase 5 — Chaos & Failure Injection (DORA + registry) ([e073aa2](https://github.com/paruff/uFawkesObs/commit/e073aa25c1b6e70d5dc1d2acfa9cfd0febd35119))
* **acceptance:** Phase 6 — Evidence Pipeline & Documentation ([6f698b9](https://github.com/paruff/uFawkesObs/commit/6f698b95a283dcfa489217af649e0631c6c870de))
* **acceptance:** Phase 6 — Evidence Pipeline & Documentation ([73a5f81](https://github.com/paruff/uFawkesObs/commit/73a5f8139c4a205b7103a67b3f2548b0c839a275))
* **acceptance:** Phase 7 — Post-Merge Comprehensive Suite CI ([11f668e](https://github.com/paruff/uFawkesObs/commit/11f668e8ce6dabb633529a9ea05849cb3f02b16b))
* **acceptance:** Phase 7 — Post-Merge Comprehensive Suite CI ([21f7103](https://github.com/paruff/uFawkesObs/commit/21f7103e342231c60f4cca916a5290eead860188))
* **acceptance:** unified pytest-bdd runtime, Alloy log fix ([fda85e2](https://github.com/paruff/uFawkesObs/commit/fda85e2ae837f12525389748efcb522cf97c1af6))
* **acceptance:** unified pytest-bdd runtime, Alloy log fix ([ae86f0d](https://github.com/paruff/uFawkesObs/commit/ae86f0d49b93b8f938c2c8aa6e3d27ff8e718c54))
* add GitOps lifecycle gates — main CI guard, post-deploy verify, rollback ([73139d0](https://github.com/paruff/uFawkesObs/commit/73139d04bf5fbc9805a86bae326753795a3bf9b2))
* add GitOps lifecycle gates — main CI guard, post-deploy verify, rollback ([be70f7d](https://github.com/paruff/uFawkesObs/commit/be70f7d45c63cff4195300182491bc9e2ee160c4))
* add test coverage measurement, fix [#343](https://github.com/paruff/uFawkesObs/issues/343) ([768c430](https://github.com/paruff/uFawkesObs/commit/768c430505de29e7cd551014914dc6ab758d9459))
* **adr:** ADR-006 DORA Metric Definitions and Data Contract (M4-01) ([baf579e](https://github.com/paruff/uFawkesObs/commit/baf579e2df43ab822ae7e00ce20dcd6e5d050508))
* **adr:** ADR-006 DORA Metric Definitions and Data Contract (M4-01) ([2e14370](https://github.com/paruff/uFawkesObs/commit/2e14370a6e4cf2e238335eb396b85986859b3265))
* **alertmanager:** add Discord alert delivery with distroless bridge ([#181](https://github.com/paruff/uFawkesObs/issues/181)) ([0ef739d](https://github.com/paruff/uFawkesObs/commit/0ef739d431469bce3a20414a999cc4703b5473d5))
* **alertmanager:** add tested Slack and Discord notification recipes ([#181](https://github.com/paruff/uFawkesObs/issues/181)) ([7ce3572](https://github.com/paruff/uFawkesObs/commit/7ce357285a9dea9d309ead0b68b623c0f0971ca0))
* **ci:** add Acceptance Full to main-ci-guard, document real gate ([38b23b0](https://github.com/paruff/uFawkesObs/commit/38b23b0b0110650b36e716a42e049c874d7199c9))
* **dashboards:** add DORA metrics dashboard with Prometheus and PostgreSQL datasources ([4c6ca43](https://github.com/paruff/uFawkesObs/commit/4c6ca43ed05e4d6c8b065892a98b35f06406398f))
* **dashboards:** M4-04 — Provision Grafana DORA Metrics Dashboard ([b35ba1d](https://github.com/paruff/uFawkesObs/commit/b35ba1db70b41c0e5f6c952dd1a4573466cac78b))
* **deploy:** switch to tag-based deploy/rollback (LB-04 redesign) ([96f8a10](https://github.com/paruff/uFawkesObs/commit/96f8a100fde2b26b1b876b8eac9f8e4b5ecf5036))
* **deploy:** switch to tag-based deploy/rollback (LB-04 redesign) ([0da2965](https://github.com/paruff/uFawkesObs/commit/0da2965133b200b5338139d1273d63a4b8a5fdbd))
* **dora:** add dora-compute + pushgateway, fold worker into dora-api ([#205](https://github.com/paruff/uFawkesObs/issues/205)) ([f02ea0e](https://github.com/paruff/uFawkesObs/commit/f02ea0e6b53ecfff3fb1caf927fdec4c90ab2937))
* **dora:** add dora-compute + pushgateway, fold worker into dora-api ([#205](https://github.com/paruff/uFawkesObs/issues/205)) ([d0992e6](https://github.com/paruff/uFawkesObs/commit/d0992e64c4fbc2e4d2b0449c39d7ec63cd20fb5d))
* **dora:** add dora-db-init one-shot migration job ([#202](https://github.com/paruff/uFawkesObs/issues/202)) ([3e9c339](https://github.com/paruff/uFawkesObs/commit/3e9c339ab04d92099a182ec0d899ddcb1e3515fb))
* **dora:** add dora-db-init one-shot migration job ([#202](https://github.com/paruff/uFawkesObs/issues/202)) ([91a302e](https://github.com/paruff/uFawkesObs/commit/91a302e5910a098519bc0981d1135d35b63b070c))
* **dora:** add rework rate as 5th DORA metric (DORA 2026) ([75acf97](https://github.com/paruff/uFawkesObs/commit/75acf97f3009b11220d0c9b525672170fbcd1675))
* **dora:** add Rework Rate as 5th DORA metric (DORA 2026) ([8794e72](https://github.com/paruff/uFawkesObs/commit/8794e72bcce45b845d765743559ef415f10a1576))
* **dora:** add Rework Rate as 5th DORA metric (DORA 2026) ([3bbe98e](https://github.com/paruff/uFawkesObs/commit/3bbe98eb897f7ac927ac289d135439e30d2ab888))
* **dora:** add rework rate as 5th DORA metric and rename MTTR to FDRT (DORA 2026) ([0b5b4b4](https://github.com/paruff/uFawkesObs/commit/0b5b4b48d88f5b43adeebdb0fd03ec9597619774))
* **dora:** add SQLite backend for event_queue, default for dora profile ([efd20a1](https://github.com/paruff/uFawkesObs/commit/efd20a18b1f561896d8ccf31e1edf8c77f6fe289))
* **dora:** ADR-007 consolidation plan + opencode workflow ([#199](https://github.com/paruff/uFawkesObs/issues/199)-[#206](https://github.com/paruff/uFawkesObs/issues/206)) ([b780d24](https://github.com/paruff/uFawkesObs/commit/b780d241e7e4d69702122c717ca6352a3513abce))
* **dora:** ADR-007 consolidation plan + opencode workflow + issues [#199](https://github.com/paruff/uFawkesObs/issues/199)-[#206](https://github.com/paruff/uFawkesObs/issues/206) ([0ae128b](https://github.com/paruff/uFawkesObs/commit/0ae128b49772a4d3729cc3123c92783e223f4a9f))
* **dora:** consolidate uFawkesDORA packages under dora/ and wire dora-api ([#200](https://github.com/paruff/uFawkesObs/issues/200)) ([1185239](https://github.com/paruff/uFawkesObs/commit/1185239c36ef291245b985c602e2529a62713ceb))
* **dora:** enforce optional DORA_API_KEY bearer auth on ingestion API ([770ba17](https://github.com/paruff/uFawkesObs/commit/770ba171facbf3a3d2a3c8416ba57dee375ad61c))
* **dora:** M4-02 Wire DORA Profile to uFawkesDORA & uFawkesRes ([5427d65](https://github.com/paruff/uFawkesObs/commit/5427d65810bbd3ba53bce37f6a454d443756f8f2))
* **dora:** M4-02 Wire DORA Profile to uFawkesDORA & uFawkesRes ([ae17aab](https://github.com/paruff/uFawkesObs/commit/ae17aab9fdde48baf4f4d52da6462d67329cbe26))
* **dora:** M4-03 Add DORA Recording Rules to Prometheus ([3ad1661](https://github.com/paruff/uFawkesObs/commit/3ad16615805da962039c92ebc0b100ddedc8bb78))
* **dora:** merge 5 DORA dashboards from uFawkesDORA ([#203](https://github.com/paruff/uFawkesObs/issues/203)) ([bfcd842](https://github.com/paruff/uFawkesObs/commit/bfcd842e82d329599e8592ee2592c54ab6b7c185))
* **dora:** merge 5 DORA dashboards from uFawkesDORA ([#203](https://github.com/paruff/uFawkesObs/issues/203)) ([c7640eb](https://github.com/paruff/uFawkesObs/commit/c7640eba6e0ec6bc9fc17755dbb4c8b26e3e6810))
* **dora:** merge DORA regression alerts, add pushgateway scrape job ([#204](https://github.com/paruff/uFawkesObs/issues/204)) ([f76e736](https://github.com/paruff/uFawkesObs/commit/f76e736eb1c2ccc3318076e395ee9fc8d0a394d7))
* **dora:** merge DORA regression alerts, add pushgateway scrape job ([#204](https://github.com/paruff/uFawkesObs/issues/204)) ([5e2abf1](https://github.com/paruff/uFawkesObs/commit/5e2abf12df20e13009766c86886435f13e3a3d16))
* **dora:** merge DORA regression alerts, add pushgateway scrape job ([#204](https://github.com/paruff/uFawkesObs/issues/204)) ([016be00](https://github.com/paruff/uFawkesObs/commit/016be00c21098443ea6a2546e45c883a68a4a477))
* **dora:** merge uFawkesDORA collector patterns ([#208](https://github.com/paruff/uFawkesObs/issues/208)) ([9216394](https://github.com/paruff/uFawkesObs/commit/921639410742483c63eb42092d1badbbdaaad376))
* **dora:** merge uFawkesDORA collector patterns ([#208](https://github.com/paruff/uFawkesObs/issues/208)) ([ce8b7dc](https://github.com/paruff/uFawkesObs/commit/ce8b7dcfd50d045c64758f618124796bf3370fb0))
* **dora:** split compute MetricsDB into SQLite/Postgres backends ([0e74b74](https://github.com/paruff/uFawkesObs/commit/0e74b7430837c124ecfefaabe2bde7882820a6c7))
* **dora:** SQLite-backed DORA profile with Postgres resource-plan override ([480602c](https://github.com/paruff/uFawkesObs/commit/480602c6793aacbc8c4b37afc82fd8fff4c53056))
* **dora:** wire up resource-plan Postgres override and gitignore data/dora ([d4558b7](https://github.com/paruff/uFawkesObs/commit/d4558b736aca774925b727eca3c634fff5dc2f6d))


### Fixed

* **acceptance:** add missing pytest imports to step files ([160371e](https://github.com/paruff/uFawkesObs/commit/160371e457882e655018bbd7532818580d011e35))
* **acceptance:** chaos_steps.py lint fixes (indentation, f-string, unused vars) ([9f79f24](https://github.com/paruff/uFawkesObs/commit/9f79f247cbdc058d0dad24e20ea1ee1f3f289811))
* **acceptance:** exclude DORA Overview pending CI-timing investigation ([a7012c9](https://github.com/paruff/uFawkesObs/commit/a7012c96aef24657a9fd4865198eb8cd41f548a2))
* **acceptance:** exclude DORA Overview pending CI-timing investigation ([3d51123](https://github.com/paruff/uFawkesObs/commit/3d51123fe87135d06ef9b6e394d26febab94fd78))
* **acceptance:** only stop stack in auto mode if we started it ([2033328](https://github.com/paruff/uFawkesObs/commit/20333286ae490c212b6f6a5d202007f7f734ac5b))
* **acceptance:** only stop stack in auto mode if we started it ([#310](https://github.com/paruff/uFawkesObs/issues/310)) ([523c95c](https://github.com/paruff/uFawkesObs/commit/523c95c2b1743cb60022a66e27b90e99d916ea8f))
* **acceptance:** only tear down the stack if this session started it ([c4ed384](https://github.com/paruff/uFawkesObs/commit/c4ed38484b15f5a08909093dd9448e745269a2fc))
* **acceptance:** only tear down the stack if this session started it ([ae774c0](https://github.com/paruff/uFawkesObs/commit/ae774c03226ba6ef0d0018429b97e7ef82ad6e6f)), closes [#310](https://github.com/paruff/uFawkesObs/issues/310)
* **acceptance:** raise OBS-CONTRACT-001's Tempo timeout to 30s ([f5f82be](https://github.com/paruff/uFawkesObs/commit/f5f82be73509e28311e508bd3f21455b7adda835))
* **acceptance:** raise OBS-CONTRACT-001's Tempo timeout to 30s ([9e6cd52](https://github.com/paruff/uFawkesObs/commit/9e6cd52b373415552a12f3e4a9874033463be6e8))
* **acceptance:** replace dead OTLP-based DORA event seeder with REST ([bad8b6a](https://github.com/paruff/uFawkesObs/commit/bad8b6ad59135f8a84820b8334bc93469ae14340))
* **acceptance:** resolve 10 configuration issues detected by tests ([7bcda30](https://github.com/paruff/uFawkesObs/commit/7bcda305d41913f4c8071f492210afea5a807d4d))
* **acceptance:** resolve 10 configuration issues from Phase 1-6 tests ([ca77028](https://github.com/paruff/uFawkesObs/commit/ca7702889c649c8325e9288a844a004c7c7e6cae))
* **acceptance:** resolve query-expr template vars in dashboard panel checks ([5794b60](https://github.com/paruff/uFawkesObs/commit/5794b6086b1a1395849f33a6ba89e68752066522))
* **acceptance:** resolve query-expr template vars in dashboard panel checks ([735ae77](https://github.com/paruff/uFawkesObs/commit/735ae776d4259331d5e5deda49773768ed53dcd8))
* **acceptance:** resolve remaining Acceptance Full failure + add diagnostics ([60f135b](https://github.com/paruff/uFawkesObs/commit/60f135b1a40218da3a92fe7cf8d409e39b24c86c))
* **acceptance:** resolve two SLO gate failures in full acceptance suite ([25cd386](https://github.com/paruff/uFawkesObs/commit/25cd386331994a6e6c321b520e743d5b7ca3ec97))
* **acceptance:** resolve two SLO gate failures in full acceptance suite ([d110973](https://github.com/paruff/uFawkesObs/commit/d110973796e0e8a3016bcd1fa5dcd9d6130fca70))
* **acceptance:** root-cause and fix OBS-SLI-006's 17-day-red gate ([c73c390](https://github.com/paruff/uFawkesObs/commit/c73c390407e73716e5579011cbf13252cc8ff253))
* **acceptance:** root-cause and fix OBS-SLI-006's 17-day-red gate ([bd95498](https://github.com/paruff/uFawkesObs/commit/bd9549841f928e3307cf1aa3d46abcfba8048140))
* **acceptance:** SLO summary print always showed FAIL for non-latency SLIs ([349e757](https://github.com/paruff/uFawkesObs/commit/349e7575771d8ac4c676d9eddd9ccd74ea6be891))
* **acceptance:** SLO summary print always showed FAIL for non-latency SLIs ([3fce95e](https://github.com/paruff/uFawkesObs/commit/3fce95e8dd058cebbbfdf34c233522bf53b44862))
* **acceptance:** stop silently swallowing exceptions in chaos polling loops ([699bf02](https://github.com/paruff/uFawkesObs/commit/699bf02fe9be938335c7e7336fbb59d931f8984d))
* **acceptance:** wait for seeded DORA metric before asserting ([5f2afd5](https://github.com/paruff/uFawkesObs/commit/5f2afd5e2a6bf0a8150b089e1acb1219ab98e8d8))
* **alertmanager:** repair the broken Slack recipe, verify live (LB-03) ([167c4f7](https://github.com/paruff/uFawkesObs/commit/167c4f7e903e9dfadbab6b06c62308128e217001))
* **alertmanager:** repair the broken Slack recipe, verify live (LB-03/[#181](https://github.com/paruff/uFawkesObs/issues/181)) ([3fac74e](https://github.com/paruff/uFawkesObs/commit/3fac74e9f89b0d8c4d07ab6acdb46d1c500e80a4))
* **ci:** add actions/checks permissions for reusable workflow calls ([6b91e6c](https://github.com/paruff/uFawkesObs/commit/6b91e6c4933c4e8dffdc3dfb10fbb4c69397bbc4))
* **ci:** add actions/checks permissions for reusable workflow calls ([0a2d837](https://github.com/paruff/uFawkesObs/commit/0a2d837083b805e10a2a658f078b4b3be7c3daad))
* **ci:** add workflow_call trigger to ci-acceptance-smoke.yml ([214bd8b](https://github.com/paruff/uFawkesObs/commit/214bd8b243e431f04f360726e17e5664ba5ba9cd))
* **ci:** add workflow_call trigger to ci-acceptance-smoke.yml ([bc2b3e4](https://github.com/paruff/uFawkesObs/commit/bc2b3e400f0879d4fa9b6a7df3ce2e27908d5b35))
* **ci:** align DORA_POSTGRES_URL placeholder with smoke workflow ([c48626b](https://github.com/paruff/uFawkesObs/commit/c48626b9ae24a85880b1d96d06007cf922193ee6))
* **ci:** align opencode pin to the v1.18.x series used across the family ([bb902d4](https://github.com/paruff/uFawkesObs/commit/bb902d4b569d15f861d19ef4a33230eaab577659))
* **ci:** align opencode pin to the v1.18.x series used across the family ([04972af](https://github.com/paruff/uFawkesObs/commit/04972af0d70618bee22510a7e4d4e5ca80c952b9))
* **ci:** allow external_directory writes for opencode ([4d28835](https://github.com/paruff/uFawkesObs/commit/4d28835a42e25f576cb5da349d31424ab436b1f9))
* **ci:** allow external_directory writes for opencode ([a35fb77](https://github.com/paruff/uFawkesObs/commit/a35fb77f04505b1536d2de9ffed81944f842d2ef))
* **ci:** also satisfy DORA_POSTGRES_URL in ci-acceptance-smoke.yml ([0962717](https://github.com/paruff/uFawkesObs/commit/096271725c5898e4894b2d11bab796ab25aff025))
* **ci:** apply ruff-format to test_deploy_pipeline.py ([f02f3d2](https://github.com/paruff/uFawkesObs/commit/f02f3d241bc0169d6f18e9a19504a10b09235032))
* **ci:** bump ufawkespipe reusable workflows to v1.3.0-beta.1 ([800c2bd](https://github.com/paruff/uFawkesObs/commit/800c2bded93b84b610a4a55f6600e1777e6b1ad9))
* **ci:** bump ufawkespipe reusable workflows to v1.3.0-beta.1 ([a11683a](https://github.com/paruff/uFawkesObs/commit/a11683a2913b20d8f66b43473886844933790ebf))
* **ci:** correct telemetry-generator health check endpoint ([9a9ba9f](https://github.com/paruff/uFawkesObs/commit/9a9ba9f7b1f5110c3b3c7ba627bf69eef5e9bf76))
* **ci:** correct telemetry-generator health check endpoint in acceptance-full workflow ([048f371](https://github.com/paruff/uFawkesObs/commit/048f3713705d1399c7cdc5ecff2a2414b3c7760b))
* **ci:** drop dead push trigger from deploy workflow ([#183](https://github.com/paruff/uFawkesObs/issues/183)) ([ec283b7](https://github.com/paruff/uFawkesObs/commit/ec283b7df3650d7550576a70993f3e4902e95533))
* **ci:** drop dead push trigger from GitOps deploy workflow ([#183](https://github.com/paruff/uFawkesObs/issues/183)) ([72dc05c](https://github.com/paruff/uFawkesObs/commit/72dc05c0a3488ad18d7fc7b7765f7a70c4216a31))
* **ci:** exclude CHANGELOG.md from markdownlint ([c3e65b3](https://github.com/paruff/uFawkesObs/commit/c3e65b358cd6c71b59f4823082258da44d46daba))
* **ci:** exclude CHANGELOG.md from markdownlint ([db74c9e](https://github.com/paruff/uFawkesObs/commit/db74c9efb33126df4fe995525974c9f6e2380d03))
* **ci:** fail the readiness gate when a service never becomes healthy ([8d8fc3d](https://github.com/paruff/uFawkesObs/commit/8d8fc3da6ab7e29a3e1bcf6cbbd93afdf819b08e))
* **ci:** fail the readiness gate when a service never becomes healthy ([da9cc40](https://github.com/paruff/uFawkesObs/commit/da9cc40e50848a28452fdb5e5f1ecc0469bd9e53))
* **ci:** gate opencode's issues trigger on author_association ([1b7e991](https://github.com/paruff/uFawkesObs/commit/1b7e9916fc43f9faa8220bb1d3ec55578bae4a5b))
* **ci:** gate opencode's issues trigger on author_association ([200ad15](https://github.com/paruff/uFawkesObs/commit/200ad1512545beaeeda93ce1d6629843239aabb8))
* **ci:** guard undefined trackingIssue in health-guard script ([0943102](https://github.com/paruff/uFawkesObs/commit/09431024389b8d2ff9c3c3d23edbc8b68b6d4b76))
* **ci:** guard undefined trackingIssue in health-guard script ([e37d643](https://github.com/paruff/uFawkesObs/commit/e37d643fe8e548f8732b32a710330f7653652d3e))
* **ci:** harden opencode workflow against code injection ([#209](https://github.com/paruff/uFawkesObs/issues/209)) ([a11ff99](https://github.com/paruff/uFawkesObs/commit/a11ff99e22fbeb23e56f8f6b2b27bf206986d44b))
* **ci:** remove duplicate acceptance-smoke job, run smoke standalone ([4e531a5](https://github.com/paruff/uFawkesObs/commit/4e531a53086cd974f2b81e952e0353a57f623ddf))
* **ci:** remove PR trigger from acceptance smoke workflow ([3ac8ac0](https://github.com/paruff/uFawkesObs/commit/3ac8ac09d759c2e60f9359792a5f7490a5f1299b))
* **ci:** resolve OBS-SLI-006 DORA dashboards by starting dora profile in Acceptance Full ([f6e0e73](https://github.com/paruff/uFawkesObs/commit/f6e0e731edd80c3b6b5bd262a9d0ca29ca774a3e))
* **ci:** restore bash:deny on opencode.yml, dropped during [#350](https://github.com/paruff/uFawkesObs/issues/350) consolidation ([2cfc8a3](https://github.com/paruff/uFawkesObs/commit/2cfc8a39e74694a00ffd3808acc3f3450ec19b72))
* **ci:** restore bash:deny on opencode.yml, dropped during [#350](https://github.com/paruff/uFawkesObs/issues/350) consolidation ([b62e99e](https://github.com/paruff/uFawkesObs/commit/b62e99e8b16ef14085ff8863beb18d4b72a0630b))
* **ci:** satisfy DORA_POSTGRES_URL interpolation in core-profile jobs ([43cac5e](https://github.com/paruff/uFawkesObs/commit/43cac5ef755ae96f575e1b7b9e53a5a9518b77c1))
* **ci:** satisfy the new slack_webhook_url secret's required env var ([5d7bb14](https://github.com/paruff/uFawkesObs/commit/5d7bb147fd5ccf5eccccefb0dcbb58fc58c9dc19))
* **ci:** set DORA_POSTGRES_URL in full acceptance workflow ([ad7face](https://github.com/paruff/uFawkesObs/commit/ad7face73f0b7e89239dd85dd67581b9bb2bce5a))
* **ci:** SHA-pin third-party actions and repoint opencode to a live upstream ([5d41220](https://github.com/paruff/uFawkesObs/commit/5d41220a5f2b534237c439072b520fbaf976dbb7))
* **ci:** SHA-pin third-party actions and repoint opencode to a live upstream ([3313bd1](https://github.com/paruff/uFawkesObs/commit/3313bd1fd431312ceb14608142ee6c1531e6521d))
* **ci:** skip preflight commit-format on copilot branches ([e297e30](https://github.com/paruff/uFawkesObs/commit/e297e30e871c7c6f84ab1258428079f494dfb94a))
* **ci:** start dora profile and seed DORA data in Acceptance Full ([b901494](https://github.com/paruff/uFawkesObs/commit/b9014940a6d80a3b7e6ea073ff1750c6f84fd61a))
* **ci:** unblock Full Acceptance Suite compose interpolation ([e6b3267](https://github.com/paruff/uFawkesObs/commit/e6b32673c0a5bb77bff9ce771a47a9d06d523c69))
* **ci:** unblock Release Please with a PAT-capable token ([092bb99](https://github.com/paruff/uFawkesObs/commit/092bb99cfc3d00d6d2c7480e978b665e918e3e76))
* **ci:** unblock Release Please with a PAT-capable token ([ba63659](https://github.com/paruff/uFawkesObs/commit/ba63659dd5656b4e29f86cc42f1f9e1e298cb255))
* **ci:** use the real pushgateway compose service name ([d9ac27e](https://github.com/paruff/uFawkesObs/commit/d9ac27ea065e4c4e035a9531788b2b2e8d0db347))
* **compose:** bind telemetry backends to localhost by default ([57aba40](https://github.com/paruff/uFawkesObs/commit/57aba40ee2ac5d0211159f491c9c2fa778a333c9))
* **compose:** document and correctly exempt distroless healthchecks ([e23984f](https://github.com/paruff/uFawkesObs/commit/e23984fe9402ac9d39937886d4a41db945590c59))
* **compose:** document and correctly exempt distroless healthchecks ([fb9b47b](https://github.com/paruff/uFawkesObs/commit/fb9b47b85cde87f43e6ccb732c0833d15180669c))
* **compose:** repair broken healthchecks and stale telemetry docs ([2b8d20e](https://github.com/paruff/uFawkesObs/commit/2b8d20ea9c8b5cda6af986d4dc062ee61ab24c57))
* **compose:** restore alloy service and fix otel-collector healthcheck removal ([77f7bf8](https://github.com/paruff/uFawkesObs/commit/77f7bf84072cbfa83ad0b9f4eb58d1e928af94e4))
* **compose:** restrict internal/scrape-only ports to localhost ([#335](https://github.com/paruff/uFawkesObs/issues/335)) ([f8c9f2e](https://github.com/paruff/uFawkesObs/commit/f8c9f2eac73b9349f2049fdd8e4e093861731c74))
* **compose:** restrict internal/scrape-only ports to localhost ([#335](https://github.com/paruff/uFawkesObs/issues/335)) ([1637652](https://github.com/paruff/uFawkesObs/commit/1637652e6092d96039a7bb95fe5f137dc1fce694))
* **config,tests:** resolve DORA Overview empty in fresh CI ([#253](https://github.com/paruff/uFawkesObs/issues/253)) ([b90c14d](https://github.com/paruff/uFawkesObs/commit/b90c14d8f3615c2eb2a45b0c8d4259fd8d21a97d))
* **config,tests:** resolve DORA Overview empty in fresh CI ([#253](https://github.com/paruff/uFawkesObs/issues/253)) ([4a85a3b](https://github.com/paruff/uFawkesObs/commit/4a85a3b0de59ba1500b6a03e6feb2cd0a604a0b6))
* **config:** fix PromQL syntax error in ai-rules.yml recording rule ([9813a3d](https://github.com/paruff/uFawkesObs/commit/9813a3d9f7bc82e23d76847df23be8adff58b75d))
* **dashboards:** correct DORA Overview legend labels to real field ([b1d4142](https://github.com/paruff/uFawkesObs/commit/b1d4142039d7df9fcf0f5842c183243a421f4405))
* **dashboards:** correct DORA Overview legend labels to real field ([3363464](https://github.com/paruff/uFawkesObs/commit/3363464fd53185ec02d02ac3b93baa8d5f03a508))
* **dashboards:** implement [#250](https://github.com/paruff/uFawkesObs/issues/250) — Service Error/Latency/SLO dashboards ([2a80a92](https://github.com/paruff/uFawkesObs/commit/2a80a9247deec9704020bba55cea2aa5f0b951b8))
* **dashboards:** implement [#250](https://github.com/paruff/uFawkesObs/issues/250) — Service Error/Latency/SLO dashboards ([69c0dfa](https://github.com/paruff/uFawkesObs/commit/69c0dfacdad7497562054cebe92e5943e1cb5553))
* **dashboards:** remove unwired DORA stub dashboards ([a90470b](https://github.com/paruff/uFawkesObs/commit/a90470b4cd13fb386d6214b3db250d8e864d7407))
* **dashboards:** remove unwired DORA stub dashboards ([#251](https://github.com/paruff/uFawkesObs/issues/251)) ([9547097](https://github.com/paruff/uFawkesObs/commit/95470975badd1014ca1370548009386dc64cf7ff))
* **dashboards:** resolve remaining OBS-SLI-006 findings surfaced by exception logging ([38f133f](https://github.com/paruff/uFawkesObs/commit/38f133f4ad7ad4777054514f340e7f82ced2a927))
* **dashboards:** resolve remaining OBS-SLI-006 findings surfaced by exception logging ([3e8e4fe](https://github.com/paruff/uFawkesObs/commit/3e8e4fececda767e882b07dc7ad0595039257d8b))
* **deploy:** alert on failure, log target IP for [#381](https://github.com/paruff/uFawkesObs/issues/381) diagnosis ([63aa964](https://github.com/paruff/uFawkesObs/commit/63aa9649e4e4d1e455cc1ad5cd369cceed80279b))
* **deploy:** alert on failure, log target IP for [#381](https://github.com/paruff/uFawkesObs/issues/381) diagnosis ([462f086](https://github.com/paruff/uFawkesObs/commit/462f0865e426a3e4ddd49bc1e326cc6b6becf039))
* **deploy:** keep rollback guidance clear of the no-push invariant scan ([38ef50e](https://github.com/paruff/uFawkesObs/commit/38ef50e1e335c49277d4983dff3c9779cdc32fcf))
* **deploy:** make the health gate run on the deploy host, guard rollback bootstrap ([98b0937](https://github.com/paruff/uFawkesObs/commit/98b09377b11804683b5dbc963cf9ad17ec3d645f))
* **deploy:** make the health gate run on the deploy host, guard rollback bootstrap ([986a99c](https://github.com/paruff/uFawkesObs/commit/986a99c9cc1f3b4a41a00200f404fc50a8a58548))
* **deploy:** pin detect-changes diff base explicitly for workflow_run ([acbdeae](https://github.com/paruff/uFawkesObs/commit/acbdeaea2664a52e8605b044bfab469a2248618b))
* **deploy:** pin detect-changes diff base explicitly for workflow_run ([eb5cf8c](https://github.com/paruff/uFawkesObs/commit/eb5cf8c77b7fab0befad5d2a788b9e88f9e05656)), closes [#301](https://github.com/paruff/uFawkesObs/issues/301)
* **deploy:** resolve the diff base to a SHA instead of a caret ref ([e14e558](https://github.com/paruff/uFawkesObs/commit/e14e55865f97929f9fbb3bdba99ea1f947278326))
* **deploy:** resolve the diff base to a SHA instead of a caret ref ([1a777ce](https://github.com/paruff/uFawkesObs/commit/1a777ce0d86c85371b1ac6a82402f043ff8a9db0))
* **dora:** attribute manual incident events to the real repo ([f2a8697](https://github.com/paruff/uFawkesObs/commit/f2a8697a4a000607442c7e7e17cf4c391f5fc66d))
* **dora:** break FDRT deployment-order ties with row id ([e3adfce](https://github.com/paruff/uFawkesObs/commit/e3adfce92a3bfb8277ab4060f9f52a3eea4e05c7))
* **dora:** close GHA script injection in collectors ([7dc6eb4](https://github.com/paruff/uFawkesObs/commit/7dc6eb4df6593ff11e922f2b35fd08434aa6d40d))
* **dora:** close GHA script injection in reusable collector workflows ([1e18051](https://github.com/paruff/uFawkesObs/commit/1e180514bda02dcfeaabc102d4fb946181a4960a))
* **dora:** close remaining HIGH-severity review findings ([#278](https://github.com/paruff/uFawkesObs/issues/278), [#279](https://github.com/paruff/uFawkesObs/issues/279), [#280](https://github.com/paruff/uFawkesObs/issues/280)) ([417966c](https://github.com/paruff/uFawkesObs/commit/417966cb6399a96d59975e16b454ba1d976e9c36))
* **dora:** close the six MEDIUM review findings ([#281](https://github.com/paruff/uFawkesObs/issues/281)-286) ([342911e](https://github.com/paruff/uFawkesObs/commit/342911ea12af8d36bc2571537cc11c8bf2d8b4d0))
* **dora:** connect resource-plane services to fawkes-backbone-net ([95b1750](https://github.com/paruff/uFawkesObs/commit/95b175091a5a2fd18ba66ede955fa353e1af0922))
* **dora:** connect resource-plane services to fawkes-backbone-net ([7d6128f](https://github.com/paruff/uFawkesObs/commit/7d6128f001ab8c31f2cd7de42d72f8d1a5527813))
* **dora:** correct pushgateway job name and payload trailing newline ([085b19a](https://github.com/paruff/uFawkesObs/commit/085b19a2fe1f3f40ceeabb32119e1ad4a64a8bbf))
* **dora:** correct pushgateway job name and payload trailing newline ([5955a66](https://github.com/paruff/uFawkesObs/commit/5955a66d3d6c31c739c6c67918f377fb8c44db29))
* **dora:** curl-examples.sh doesn't match its own event schemas ([#280](https://github.com/paruff/uFawkesObs/issues/280)) ([e177d5e](https://github.com/paruff/uFawkesObs/commit/e177d5e16da86511cac78f3c4e88ab5deb6f6e10))
* **dora:** dedupe event_queue writes on identical payload ([ac86853](https://github.com/paruff/uFawkesObs/commit/ac86853816d518948dee7b78097888b828e299a5))
* **dora:** dedupe event_queue writes on identical payload ([3b05f2f](https://github.com/paruff/uFawkesObs/commit/3b05f2ff04a30b84c61692467c5f89a04de27598))
* **dora:** enforce optional DORA_API_KEY bearer auth on ingestion API ([ec784a9](https://github.com/paruff/uFawkesObs/commit/ec784a9e0bbb54735fcfa46124f9384543088aa5))
* **dora:** escape team_id in Prometheus label/URL output ([#276](https://github.com/paruff/uFawkesObs/issues/276)) ([dc015c8](https://github.com/paruff/uFawkesObs/commit/dc015c8d489848a7e7f8b4c453343fb351a96c7c))
* **dora:** feed Lead Time and FDRT from real deployment events ([ae26c15](https://github.com/paruff/uFawkesObs/commit/ae26c153a9fda91608da57bca7450ef3f1c7e44d))
* **dora:** feed Lead Time and FDRT from real deployment events ([#267](https://github.com/paruff/uFawkesObs/issues/267)) ([4ea41f4](https://github.com/paruff/uFawkesObs/commit/4ea41f4ed2ea356e8ad2268708839b5f86fc4f26))
* **dora:** rename resource-plan to resource-plane, drop stale uFawkesDORA dep ([81fbaa0](https://github.com/paruff/uFawkesObs/commit/81fbaa03adee7d1145ee6810009affa4482cde2f))
* **dora:** rename resource-plan to resource-plane, drop stale uFawkesDORA dep ([4d81323](https://github.com/paruff/uFawkesObs/commit/4d81323d062920c038010cef3b3d5f431510ce9b))
* **dora:** repoint dora-metrics.json's recording rules at the fed pipeline ([c94d257](https://github.com/paruff/uFawkesObs/commit/c94d257165f937ccc5e62409456ee4afbfdaa020))
* **dora:** repoint dora-metrics.json's recording rules at the fed pipeline ([5a26e20](https://github.com/paruff/uFawkesObs/commit/5a26e206d4b0d6b084a5c185f8edf580e3b68043))
* **dora:** scale regression alert thresholds to the real ratio range ([55ba6bb](https://github.com/paruff/uFawkesObs/commit/55ba6bbe2dec44e44bc3964c4cd86b4e8493edc5))
* **dora:** send DORA_API_KEY from the deploy-event script ([00af213](https://github.com/paruff/uFawkesObs/commit/00af213d764f72ab0b7e589e1f47c4e26be2c37d))
* **dora:** stop dora-db-init from breaking compose parsing without resource-plan ([cbec58e](https://github.com/paruff/uFawkesObs/commit/cbec58ef37793009b281a561ca8829843d5e584f))
* **dora:** use Pushgateway job@base64 path for team_id ([b36eefc](https://github.com/paruff/uFawkesObs/commit/b36eefcbfb1a3b9bd8a2127ac41022236a7c4d77))
* **dora:** use Pushgateway job@base64 path for team_id ([bb86756](https://github.com/paruff/uFawkesObs/commit/bb86756cb96468f26ec91754fdf80698c9b2f84a))
* **dora:** use set -eu in POSIX sh collectors, add shellcheck pre-commit hook ([e795810](https://github.com/paruff/uFawkesObs/commit/e7958102c3a687faefed54b026d4a1659c074c03))
* **dora:** Woodpecker collector snippet fails schema validation ([#279](https://github.com/paruff/uFawkesObs/issues/279)) ([7f98734](https://github.com/paruff/uFawkesObs/commit/7f98734072f5d898783e8f1493d3dc2f8441e989))
* **grafana:** disable anonymous viewer access by default ([86a77d2](https://github.com/paruff/uFawkesObs/commit/86a77d2c7372c687d113c659a06d1d90e034e49d))
* **grafana:** disable anonymous viewer access by default ([51baf55](https://github.com/paruff/uFawkesObs/commit/51baf552e485a228d465d814d2c855d3a37119a5))
* **grafana:** observability UX cleanup and exception-logging principle ([fdbd0e7](https://github.com/paruff/uFawkesObs/commit/fdbd0e7a62785c3f7169bd575cd9032139910ac3))
* **grafana:** observability UX cleanup and exception-logging principle ([020ee45](https://github.com/paruff/uFawkesObs/commit/020ee4517f8e4a0f630d5f7ebfa9d0e529b28d4b))
* **grafana:** repair Application/Infrastructure dashboards and add home dashboard ([9610874](https://github.com/paruff/uFawkesObs/commit/9610874515edbec388e58ce98dc1c0476effa576))
* **grafana:** repair broken dashboards, healthchecks, and stale docs ([19e5457](https://github.com/paruff/uFawkesObs/commit/19e5457c5ee832b65c6b29e15723340d1ef37214))
* **grafana:** repair Platform/Services dashboard variable plumbing ([8629bab](https://github.com/paruff/uFawkesObs/commit/8629bab39fa7641f74e981e7dd3beac76f6e4942))
* **grafana:** repair Platform/Services dashboard variable plumbing ([d601583](https://github.com/paruff/uFawkesObs/commit/d6015832b7e6ff1875163c7dd0a9d1ca6c222055))
* land stranded test coverage measurement ([#343](https://github.com/paruff/uFawkesObs/issues/343)) ([a22aab0](https://github.com/paruff/uFawkesObs/commit/a22aab052c3af88a2c71ee7a7cb76cff5c5d7c39))
* **observability:** seed telemetry-generator traffic and wait for propagation ([5122b6e](https://github.com/paruff/uFawkesObs/commit/5122b6e660d1a1e9bebd7dcf7714af5da4dd2d8e))
* **observability:** seed telemetry-generator traffic and wait for propagation ([706fe3d](https://github.com/paruff/uFawkesObs/commit/706fe3d040f83ac274f3bbcccd196dcd192189f5)), closes [#274](https://github.com/paruff/uFawkesObs/issues/274)
* **otel:** remove dead otlp/dora exporter from collector-dora.yaml ([df6d3b5](https://github.com/paruff/uFawkesObs/commit/df6d3b56231d6ceaa583c0a25232fec43c89d3e9))
* **otel:** remove dead otlp/dora exporter from collector-dora.yaml ([b24c5ac](https://github.com/paruff/uFawkesObs/commit/b24c5ac872bee7f2f79721a9c8e93e5bdd2197a0))
* remove broken healthcheck from otel-collector (distroless image) ([aeb802d](https://github.com/paruff/uFawkesObs/commit/aeb802d98af32bd6cbec491fc5aa14d29254444c))
* remove broken healthcheck from otel-collector (distroless image) ([c90203f](https://github.com/paruff/uFawkesObs/commit/c90203f8432a2e66664b2f3a522f8a686ff3b89c))
* resolve audit medium findings M-1, M-2, M-3 ([1aef6de](https://github.com/paruff/uFawkesObs/commit/1aef6de3bc3a988042ff0487539cf17f1bc253a7))
* resolve audit medium findings M-1, M-2, M-3 ([f757171](https://github.com/paruff/uFawkesObs/commit/f757171d1a4f957382283194c9f7bd49bd5260dd))
* resolve public-release audit findings ([65e3bc6](https://github.com/paruff/uFawkesObs/commit/65e3bc6e65faca27522e938a2d4fa1fc835a69ca))
* **security:** reject the REPLACE_ME placeholder in the Grafana guard ([3ec4d4c](https://github.com/paruff/uFawkesObs/commit/3ec4d4cd88ab2c13da6dce9ce15fa0e127dadd36))
* **security:** reject the REPLACE_ME placeholder in the Grafana guard ([be0e5df](https://github.com/paruff/uFawkesObs/commit/be0e5dfec1b3e05436d2f4cc15661c401f35817f))
* **test:** match CI's DORA compute interval in local acceptance runs ([33a68b1](https://github.com/paruff/uFawkesObs/commit/33a68b116110e9147532025ff479334b096deaf0))
* **test:** match CI's DORA compute interval in local acceptance runs ([e3e6980](https://github.com/paruff/uFawkesObs/commit/e3e6980b08b65f1e8cf1a48425b8a5526ddd5897))
* **test:** pin unit test deps with a lock file for determinism ([bed693a](https://github.com/paruff/uFawkesObs/commit/bed693ad758f9a2926d5619d175e7457fb62f897))
* **test:** pin unit test deps with a lock file for determinism ([999bb66](https://github.com/paruff/uFawkesObs/commit/999bb66d19ba64b232cd7ae1603404aa91b94f40))
* **tests:** accept semver pre-release suffix in rollback pin check ([843289b](https://github.com/paruff/uFawkesObs/commit/843289bdb5ce97d10f6bc08d0695a8b475e36977))
* **tests:** add aiohttp to unit test requirements ([#206](https://github.com/paruff/uFawkesObs/issues/206)) ([0843f0b](https://github.com/paruff/uFawkesObs/commit/0843f0b4b2a1e8e695107786ea16055f215ac826))
* **tests:** avoid CodeQL URL-substring finding in rollback drill guard ([#182](https://github.com/paruff/uFawkesObs/issues/182)) ([460b1f4](https://github.com/paruff/uFawkesObs/commit/460b1f4c0b5fbf61e754599b20506a134c53c319))
* **tests:** load dora_events.py directly, avoid opentelemetry in unit CI ([f553558](https://github.com/paruff/uFawkesObs/commit/f55355845471d1802f0c88acb75efc1e11ae8db0))
* **tests:** make dora.ingestion.processor.worker importable outside Docker ([#206](https://github.com/paruff/uFawkesObs/issues/206)) ([1722dc0](https://github.com/paruff/uFawkesObs/commit/1722dc0a7b9d9024bd876ed25dff98e9c453b1cb))
* **tests:** treat pushgateway as optional in Prometheus target checks ([#204](https://github.com/paruff/uFawkesObs/issues/204)) ([7c1937f](https://github.com/paruff/uFawkesObs/commit/7c1937fbb49cc65a9c72486db0cda1b905543c59))
* **workflow:** correct if condition syntax in deploy.yml trigger expressions ([5f8b7e4](https://github.com/paruff/uFawkesObs/commit/5f8b7e44e654d74c15d5eee3b556dde4020fdde9))
* **workflow:** correct if condition syntax in deploy.yml trigger expressions ([223fedf](https://github.com/paruff/uFawkesObs/commit/223fedffaaad817a3b6cac272a1b752f4fdcb294))
* YAML quoting, markdownlint MD022, and secret baseline ([81ccc91](https://github.com/paruff/uFawkesObs/commit/81ccc91de4fd44e55314fd4ff442214e1d5df762))


### Docs

* add 4-tier planning cascade and link product artifacts ([5eea7f1](https://github.com/paruff/uFawkesObs/commit/5eea7f1e709c2f4a5d7d69b0d9894da67f1ad6ae))
* add ci-fix-report.md documenting CI repair for PR [#137](https://github.com/paruff/uFawkesObs/issues/137) ([4236e2a](https://github.com/paruff/uFawkesObs/commit/4236e2aa77e4340ce5c4daebbdb0950f8dd05789))
* add findings note on uFawkesRes suite-tier status ([47f2951](https://github.com/paruff/uFawkesObs/commit/47f29511f38b0c2ce656e7b143fc77377be6bd8b))
* add findings note on uFawkesRes suite-tier status ([8a184f7](https://github.com/paruff/uFawkesObs/commit/8a184f75af4be511c070170f676ef391d5984126))
* add uFawkesDojo, fix stale DORA/Sec family table entries ([c119209](https://github.com/paruff/uFawkesObs/commit/c11920956d9a368ce3e42a26d53a1bfd480eae75))
* add uFawkesDojo, fix stale DORA/Sec family table entries ([d676d9b](https://github.com/paruff/uFawkesObs/commit/d676d9b18ddf2c37747a423239b317190b156a6a))
* **adr:** correct ADR-007 issue range and DB/pyproject assumptions ([652a05d](https://github.com/paruff/uFawkesObs/commit/652a05d7446c45ec49d271410a11c2875a81fd57))
* align AGENTS.md gitops lifecycle with prei standards ([120936d](https://github.com/paruff/uFawkesObs/commit/120936d56d2dfc614cb8b8e1ba36b76bf4e9ef60))
* align AGENTS.md gitops lifecycle with prei standards ([34d673b](https://github.com/paruff/uFawkesObs/commit/34d673b82834196d31f2a5bfb0e4c8fa1cff5452))
* assess Prometheus/Grafana/dashboard portability to Fawkes ([76a95ac](https://github.com/paruff/uFawkesObs/commit/76a95acf104b993a76d8bb16c2daf1c7dc433381))
* assess Prometheus/Grafana/dashboard portability to Fawkes ([24af6c7](https://github.com/paruff/uFawkesObs/commit/24af6c723f191927869bb48838ecde2c8807aaa0))
* **changelog:** cut 0.2.0 entry for first public release ([a9b01e8](https://github.com/paruff/uFawkesObs/commit/a9b01e83a5e8a72b02363b3048bd021bb9ecfb46))
* **changelog:** cut 0.2.0 entry for first public release ([981bb0a](https://github.com/paruff/uFawkesObs/commit/981bb0a397ecd29fa33b30dddb8fc84de35f72d7))
* **changelog:** cut v0.3.0-alpha.1 entry ahead of LB-04 drill ([70e22b8](https://github.com/paruff/uFawkesObs/commit/70e22b83f6d110ced0ce9ecbe68dac2ec920390d))
* **ci:** correct required-check names to what PR [#298](https://github.com/paruff/uFawkesObs/issues/298) actually shows ([939b240](https://github.com/paruff/uFawkesObs/commit/939b2407712c427283cb268640615c04c72e60ca))
* **ci:** rename Chaos Nightly workflow to Chaos Resilience (Nightly) ([d83e46e](https://github.com/paruff/uFawkesObs/commit/d83e46e181531115efd0ffdd2be882af997e5a52))
* **ci:** rename CI Quality workflow to Quality & Security Gates ([c5fafb4](https://github.com/paruff/uFawkesObs/commit/c5fafb4d3e14b346aa1fe1939ea42f6bdcd332c4))
* **ci:** rename Repo Hygiene workflow and Pre-commit Hooks job ([44452e0](https://github.com/paruff/uFawkesObs/commit/44452e06edcd418c2cf01d6ab746afe3b4107095))
* consolidate live status tracking into EXECUTION_QUEUE.md ([39b178e](https://github.com/paruff/uFawkesObs/commit/39b178ea1054126c88acfd13b2282be0b644f483))
* consolidate live status tracking into EXECUTION_QUEUE.md ([a3f1d47](https://github.com/paruff/uFawkesObs/commit/a3f1d4759b703e69501269970a8170e795fc29b0))
* consolidate opencode workflows, fix issue [#350](https://github.com/paruff/uFawkesObs/issues/350) ([68bf1a0](https://github.com/paruff/uFawkesObs/commit/68bf1a0100cfb5eefe1521cc4178a8acd5557408))
* consolidate planning cascade from PATH_TO_LATE_BETA.md ([382361b](https://github.com/paruff/uFawkesObs/commit/382361bfefea79d17391234d592b9a75d7cade55))
* consolidate planning cascade from PATH_TO_LATE_BETA.md ([bd43142](https://github.com/paruff/uFawkesObs/commit/bd43142138622b240663037b9b5eaf5e03784826))
* cross-link governance docs and add late-beta closeout week plan ([29b7daf](https://github.com/paruff/uFawkesObs/commit/29b7daf656edf640d2f2be47293c586425a2999a))
* cross-link governance docs and add late-beta closeout week plan ([0f9563e](https://github.com/paruff/uFawkesObs/commit/0f9563eaf2c10aad72de24b78939f3ad56d5e1f9))
* **deploy:** add rollback drill runbook and link from deployment strategy ([#182](https://github.com/paruff/uFawkesObs/issues/182)) ([fcb01fa](https://github.com/paruff/uFawkesObs/commit/fcb01faadb1ad6c150d855f747c9c7ab14cc7ea5))
* **deploy:** add Synology drill-host provisioning for LB-04 ([9aaaef9](https://github.com/paruff/uFawkesObs/commit/9aaaef98cc0ce70a317032395a26d2c289648a36))
* **deploy:** add Synology drill-host provisioning for LB-04 ([ac72c9a](https://github.com/paruff/uFawkesObs/commit/ac72c9a09d71df293e3c821a0a344124e6b9d486))
* **deploy:** record LB-04 rollback drill results ([d12aae1](https://github.com/paruff/uFawkesObs/commit/d12aae19231250dbc2f44761617d61ee811d7994))
* **deploy:** record LB-04 rollback drill results ([3a4a754](https://github.com/paruff/uFawkesObs/commit/3a4a754c58faaee49f2e52a5694f8bfa3a2f1cdd))
* **deploy:** rewrite rollback drill and strategy for tag-based design ([a305c9a](https://github.com/paruff/uFawkesObs/commit/a305c9a213e234d9f876917dc0a428d32c113002))
* document Slack and Discord alertmanager notification setup ([#181](https://github.com/paruff/uFawkesObs/issues/181)) ([55bd342](https://github.com/paruff/uFawkesObs/commit/55bd34205e1cf66224196e19b0cf35d146ca7777))
* **dora:** amend ADR-006, the OTLP ingestion model was never built ([ff73c04](https://github.com/paruff/uFawkesObs/commit/ff73c04366da78f1efe87878f1247c0d777aeb21))
* **dora:** document dora-api's fail-open auth default ([a7bc727](https://github.com/paruff/uFawkesObs/commit/a7bc72764bb52800e9bff58ee90b7b1b7c03b20e))
* **dora:** merge uFawkesDORA spec/design/decisions/discovery ([#207](https://github.com/paruff/uFawkesObs/issues/207)) ([3b171c0](https://github.com/paruff/uFawkesObs/commit/3b171c0addc3a2a477e941cfb1e32bf1f4b6ee44))
* **dora:** merge uFawkesDORA spec/design/decisions/discovery ([#207](https://github.com/paruff/uFawkesObs/issues/207)) ([8681a85](https://github.com/paruff/uFawkesObs/commit/8681a85cee44b9c0c365649bcf6eaa6df0377e2e))
* Fawkes replaces uFawkesObs wholesale, not consumes it ([2292b71](https://github.com/paruff/uFawkesObs/commit/2292b71393fcf6d1de473f8409327078949bdfbd))
* Fawkes replaces uFawkesObs wholesale, not consumes it ([a435575](https://github.com/paruff/uFawkesObs/commit/a435575b55c3eb7f25d0e47e1c76d7deb3b7a916))
* fix broken link, stale version, and blocked LB-04 status ([74cd2ca](https://github.com/paruff/uFawkesObs/commit/74cd2ca08233af7fddfbb0f12432cccc5f6190e4))
* fix markdownlint MD022 — blank lines after ### subheadings ([5d1300a](https://github.com/paruff/uFawkesObs/commit/5d1300a7d0f873546e27658f7bbc77c9daa23e58))
* fix media-refinery reference cleanup that missed staging ([ebc0483](https://github.com/paruff/uFawkesObs/commit/ebc0483558483ae5f27d7bbbdf455403c46cc5cb))
* fix stale Prometheus version and blocked LB-04 status ([d78b6da](https://github.com/paruff/uFawkesObs/commit/d78b6dad21f76a54701326168a2c0291e64b869f))
* integrate expert feedback — M5 migration to Fawkes track ([ce4e4f0](https://github.com/paruff/uFawkesObs/commit/ce4e4f0c6449acd15332da65210733bf9dc9c52e))
* integrate expert feedback — M5 migration to Fawkes, non-goals updated ([37742b1](https://github.com/paruff/uFawkesObs/commit/37742b16f2ddbf1abf132e01816fadb54dd84926))
* link CONTRIBUTING.md from README instead of placeholder text ([8d32ef3](https://github.com/paruff/uFawkesObs/commit/8d32ef329c43b5334bc607d41b54b74a6b64cbc8))
* link CONTRIBUTING.md from README instead of placeholder text ([9f2c350](https://github.com/paruff/uFawkesObs/commit/9f2c35018c381bddbdf127bbacd98ba302b765fa))
* log Phase 2 agent decision findings F04-F06 ([4a26be2](https://github.com/paruff/uFawkesObs/commit/4a26be26207925765f48c3fead0c80a6f0ed78ce))
* **m3-05:** add docker-compose.integration.yml and multi-stack integration guide ([c054b34](https://github.com/paruff/uFawkesObs/commit/c054b34e94c97f4a122f21d6a0e3ed38e8908da6))
* **m3-05:** add docker-compose.integration.yml and multi-stack integration guide ([93faf6c](https://github.com/paruff/uFawkesObs/commit/93faf6c0b92f83e0773ead15d818eab575122bb2))
* mark [#343](https://github.com/paruff/uFawkesObs/issues/343)/[#345](https://github.com/paruff/uFawkesObs/issues/345) done, correct chaos-nightly false alarm ([6c5574d](https://github.com/paruff/uFawkesObs/commit/6c5574dab091df78b8bb94df6b32fe150d3bdee3))
* mark LB-02 done in Path to Late Beta ([850abb5](https://github.com/paruff/uFawkesObs/commit/850abb581e8eb1e8cc69865df0885071ed4f3cbf))
* mark LB-02 done in Path to Late Beta ([753b8ca](https://github.com/paruff/uFawkesObs/commit/753b8cab8dd056a7a1995143911def9b713b9916))
* mark LB-05 and LB-06 done in Path to Late Beta ([2862a4c](https://github.com/paruff/uFawkesObs/commit/2862a4c08fc285fe7296d4feec966d0e22f4475a))
* mark LB-05 and LB-06 done in Path to Late Beta ([397d84a](https://github.com/paruff/uFawkesObs/commit/397d84a62d4afc3be11e33c2be085e45bc5ca618))
* move Day One guide into docs ([9a88a4f](https://github.com/paruff/uFawkesObs/commit/9a88a4f65b773a6036a65285d4c5f52fb1b0d652))
* **plan:** add Path to Late Beta plan and tracking issues ([d2bff8c](https://github.com/paruff/uFawkesObs/commit/d2bff8c24ae926633b417077f040f88fc2f298ef))
* **plan:** add Path to Late Beta plan and tracking issues ([37998af](https://github.com/paruff/uFawkesObs/commit/37998af1b3b07b3c53e7f3fc1cd9e789a560a539))
* **plan:** reconcile plan.md status against gh issue list (LB-07 [#185](https://github.com/paruff/uFawkesObs/issues/185)) ([cfca8ff](https://github.com/paruff/uFawkesObs/commit/cfca8ff1b7d1b7dd7b78f485934dfb23e5d45756))
* **plan:** reconcile plan.md status vs gh issue list ([#185](https://github.com/paruff/uFawkesObs/issues/185)) ([9cfb700](https://github.com/paruff/uFawkesObs/commit/9cfb700146fa43370f7de660ae90f7207cd9da5e))
* **product:** bring discovery/spec/design revision to main ([aba6e50](https://github.com/paruff/uFawkesObs/commit/aba6e5012dc3decf2c73c20aa0653c38c7c9e7ea))
* **product:** honest discovery brief, spec/design sync, add CLAUDE.md ([094e114](https://github.com/paruff/uFawkesObs/commit/094e1147d25a6f77695ac365f7da14e1e87e2898))
* publish Obs's DORA event and OTLP contract surface ([28aaafb](https://github.com/paruff/uFawkesObs/commit/28aaafb59f811426255a91493b5581d7dfbc3653))
* publish Obs's DORA event and OTLP contract surface ([6afc146](https://github.com/paruff/uFawkesObs/commit/6afc146c4d5a37bcb5b042deea0e7f5ea0357e09))
* reconcile docs drift, relocate files, document test pyramid ([872ebd2](https://github.com/paruff/uFawkesObs/commit/872ebd2d2d02817ef4b2eccbccd2de0b0c0eae1e))
* reconcile docs drift, relocate files, document test pyramid ([#342](https://github.com/paruff/uFawkesObs/issues/342)-[#351](https://github.com/paruff/uFawkesObs/issues/351)) ([fc503b3](https://github.com/paruff/uFawkesObs/commit/fc503b35f17a85408d0d00cb63512cbb41e212ba))
* record static review of LB-04 rollback drill ([#182](https://github.com/paruff/uFawkesObs/issues/182)) ([66d7647](https://github.com/paruff/uFawkesObs/commit/66d7647140352fcf0154f8396735e05b8152e0cc))
* refactor MODEL_POLICY.md to grade-based system with benchmark thresholds ([bb3db75](https://github.com/paruff/uFawkesObs/commit/bb3db759b34144cdd6d4f28a31dcfe4c3485acd0))
* relocate pr-review-block skill to .agents/skills/ ([4113789](https://github.com/paruff/uFawkesObs/commit/411378997dd0c2c308f4b5871ff35455e44575f3))
* relocate pr-review-block skill to .agents/skills/ ([efb1bab](https://github.com/paruff/uFawkesObs/commit/efb1babed35ffa91adc4c17932c7b773dff6b7ac))
* remove obsolete pre-release cruft and fix stale media-refinery refs ([795ce5f](https://github.com/paruff/uFawkesObs/commit/795ce5ff150681ff5e5d11a93950242aab95b2b1))
* remove obsolete pre-release cruft and fix stale media-refinery refs ([db4a520](https://github.com/paruff/uFawkesObs/commit/db4a5202d3314ef6fffd18b7737cc3f499ea9038))
* reposition uFawkesAI as a template, remove duplicate stack table ([396c2c1](https://github.com/paruff/uFawkesObs/commit/396c2c1f6561ef8f5e87dde02eedec13234ec8d0))
* reposition uFawkesAI as a template, remove duplicate stack table ([277ab9f](https://github.com/paruff/uFawkesObs/commit/277ab9f6eaaa96499ba9c3490bbbb520769b05f2))
* restructure README for public release, close [#345](https://github.com/paruff/uFawkesObs/issues/345) ([63c6466](https://github.com/paruff/uFawkesObs/commit/63c6466197dca0633cd95892020ab1a3058fe84b))
* restructure README for public release, close [#345](https://github.com/paruff/uFawkesObs/issues/345) ([ff26f1e](https://github.com/paruff/uFawkesObs/commit/ff26f1e30db04c4548d29695100e07bf84fe7dc0))
* retire uFawkesRes/Sec, add Fawkes graduation path ([047cc69](https://github.com/paruff/uFawkesObs/commit/047cc69b46651cf638e1bb35c8b2b9256307ec13))
* retire uFawkesRes/Sec, add Fawkes graduation path ([3c2e779](https://github.com/paruff/uFawkesObs/commit/3c2e7797f7da0d00f4f20914e2e5387ef2520a88))
* shift daily focus to P2, record P1 carryover status ([afee986](https://github.com/paruff/uFawkesObs/commit/afee986d557867fce05887deafb5ba955b6c5e17))
* shift daily focus to P2, record P1 carryover status ([535907f](https://github.com/paruff/uFawkesObs/commit/535907f7ad90e1265a901523ae645a40123b02ae))
* update blocker status in public-release tracker ([0c03396](https://github.com/paruff/uFawkesObs/commit/0c033968d9b8338a835fcb46b4f59b2a91b11647))
* update blocker status, PR-01/PR-03 fixed, PR-02 finding worse ([e03d0b4](https://github.com/paruff/uFawkesObs/commit/e03d0b4445257f51e6c1616047b2e59b33c9a1d4))
* update main-ci-guard to stable workflow version, fix issue [#352](https://github.com/paruff/uFawkesObs/issues/352) ([30d0b30](https://github.com/paruff/uFawkesObs/commit/30d0b30caa2e29ce6190b38469b1bd67fad69608))
* update MODEL_POLICY.md to reflect OpenCode setup, fix issue [#346](https://github.com/paruff/uFawkesObs/issues/346) ([79d241d](https://github.com/paruff/uFawkesObs/commit/79d241d232866437de6439ce449fda9b5765eeb2))
* update plan-for-the-day.md with completed tasks ([d403052](https://github.com/paruff/uFawkesObs/commit/d403052b571a3191dde807c43007e52c0315933f))
* update session retrospective with learnings ([60fc307](https://github.com/paruff/uFawkesObs/commit/60fc307dfc7be200caf29ec9f1a83661a928ed11))


### Changed

* **dora:** apply ruff formatting to consolidated packages ([#200](https://github.com/paruff/uFawkesObs/issues/200)) ([0617a90](https://github.com/paruff/uFawkesObs/commit/0617a904bb62aaf4111a3cf279f76a65c5ed3c5c))
* **dora:** collapse _merge_team_results' 5x duplicated logic ([ef8a7bc](https://github.com/paruff/uFawkesObs/commit/ef8a7bc19c553e2220a39c82f517e1759326afdb))
* **dora:** fold the compute loop into dora-api, drop Pushgateway ([124b79d](https://github.com/paruff/uFawkesObs/commit/124b79da823cf037c769ea7bf7faab4887639846))
* **dora:** fold the compute loop into dora-api, drop Pushgateway ([2c0c84a](https://github.com/paruff/uFawkesObs/commit/2c0c84aa6649435db8e1ce733103b03c289902e8))
* **dora:** remove the dormant otel-collector-dora container ([7164527](https://github.com/paruff/uFawkesObs/commit/71645276c49cf60e847e4177fefa8970f944b08b))
* **dora:** remove the dormant otel-collector-dora container ([d854732](https://github.com/paruff/uFawkesObs/commit/d85473223844f9a2f10cf2dc5961afbd95d4d809))
* **dora:** rename MTTR to FDRT (Failed Deployment Recovery Time) ([cc4d4eb](https://github.com/paruff/uFawkesObs/commit/cc4d4eb84104057bda4654a5d40a21a1aa9d73a6))
* **dora:** split oversized compute functions per AGENTS.md guideline ([b178ccb](https://github.com/paruff/uFawkesObs/commit/b178ccb1ddb042c679b248299291117b776eceec))


### Chores

* **ci:** add Acceptance Full health guard and explicit deploy skip summaries ([7d7a382](https://github.com/paruff/uFawkesObs/commit/7d7a382bf7381ee0ed4f0b41bf67163175976e70))
* **ci:** consolidate secret scanning, stop tracking graphify-out ([4926b51](https://github.com/paruff/uFawkesObs/commit/4926b51bb53faff36878245e449c22915f1588c5))
* **ci:** consolidate secret scanning, stop tracking graphify-out ([3cff5e6](https://github.com/paruff/uFawkesObs/commit/3cff5e65478691341f191c2ab7cc4578f653864f))
* **ci:** consolidate workflow naming into a clear test pyramid ([8100373](https://github.com/paruff/uFawkesObs/commit/81003739b6891d68f481fd5c8093ff2e70074e10))
* **ci:** guard acceptance-full gate health ([fb13be8](https://github.com/paruff/uFawkesObs/commit/fb13be866cf9b85a5a50fc5175d7322aa98fd511))
* **ci:** tighten acceptance-full guard lookup ([71999c0](https://github.com/paruff/uFawkesObs/commit/71999c0d1bdd469457ee0133112ee846a72f2935))
* **community:** add beta feedback channel ([6546ad4](https://github.com/paruff/uFawkesObs/commit/6546ad4d189e139455b4fc95aef5494af43f906f))
* **community:** add beta feedback channel ([a78c933](https://github.com/paruff/uFawkesObs/commit/a78c933e31e64d020dde9f17fcc658eccc169ee3))
* **deploy:** comment-only change to prove deploy.yml SSH connectivity ([#182](https://github.com/paruff/uFawkesObs/issues/182)) ([27c1eea](https://github.com/paruff/uFawkesObs/commit/27c1eea65b552fe7c3df54a15c125e6acf04957a))
* **deploy:** document rollback drill runbook for LB-04 ([#182](https://github.com/paruff/uFawkesObs/issues/182)) ([7ddc9ac](https://github.com/paruff/uFawkesObs/commit/7ddc9ac82a1e7cae46f4440986e2c1a7e96be742))
* **deploy:** enable and guard LB-04 rollback drill for live execution ([#182](https://github.com/paruff/uFawkesObs/issues/182)) ([46d65eb](https://github.com/paruff/uFawkesObs/commit/46d65ebeef955c57b1a0f513319d19f96e447b86))
* **deploy:** prove deploy.yml SSH connectivity before the LB-04 drill ([8c64f0d](https://github.com/paruff/uFawkesObs/commit/8c64f0d1bba75c48823eba553ee72d0700b3623f))
* **deps:** bump actions/checkout from 4 to 7 ([0539e79](https://github.com/paruff/uFawkesObs/commit/0539e79983570d8c70036851dac91830df50e307))
* **deps:** bump actions/checkout from 4 to 7 ([9b984dc](https://github.com/paruff/uFawkesObs/commit/9b984dc7b4424ab47ed863b2b0c6b86772b13d3b))
* **deps:** bump actions/setup-python from 6 to 7 ([e741fc9](https://github.com/paruff/uFawkesObs/commit/e741fc9bb721f708bd918446c21d239dea1b0236))
* **deps:** bump anomalyco/opencode/github from 1.18.26 to 1.18.29 ([bbfd7aa](https://github.com/paruff/uFawkesObs/commit/bbfd7aa21d29d47feb77450b65cbf353d0426d15))
* **deps:** bump anomalyco/opencode/github from 1.18.26 to 1.18.29 ([bd2e762](https://github.com/paruff/uFawkesObs/commit/bd2e7623df623a31014b4720dd5f97607a9b1652))
* **deps:** bump googleapis/release-please-action from 4.4.1 to 5.0.0 ([d45a9b6](https://github.com/paruff/uFawkesObs/commit/d45a9b6592f39c4ded10aa599cf637b754d9f8a5))
* **deps:** bump googleapis/release-please-action from 4.4.1 to 5.0.0 ([74e122d](https://github.com/paruff/uFawkesObs/commit/74e122de36e34ba8e1f6b7b4e5729deed4070c9b))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-build.yml ([65b6e2a](https://github.com/paruff/uFawkesObs/commit/65b6e2aed4c801511386b18c5abe4dd4ba19a453))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-build.yml ([176524c](https://github.com/paruff/uFawkesObs/commit/176524cff6efc9ede1008b10549228ceee514d1a))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-build.yml ([6fb03c7](https://github.com/paruff/uFawkesObs/commit/6fb03c7243eb1a50c7c6009791f8c17ec26eef4b))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-build.yml from 1.1.0 to 1.1.1 ([2ec4936](https://github.com/paruff/uFawkesObs/commit/2ec493624476c713313a785a6892173a9c82dace))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-build.yml from 1.3.0.pre.beta.1 to 1.4.0.pre.beta.1 ([eee648d](https://github.com/paruff/uFawkesObs/commit/eee648dda76bfa06960250610a14198c3da5dd94))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-dependency-review.yml ([483eda6](https://github.com/paruff/uFawkesObs/commit/483eda6827ef5eb1b0dc399b43b2dfd9fb865560))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-dependency-review.yml ([783e723](https://github.com/paruff/uFawkesObs/commit/783e723c9a630c796fd07175402491378b4fc7c2))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-dependency-review.yml ([b881bbe](https://github.com/paruff/uFawkesObs/commit/b881bbed6dbb1896196cbfa0457a5d61c9cb1150))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-dependency-review.yml from 1.1.0 to 1.1.1 ([fcb0b89](https://github.com/paruff/uFawkesObs/commit/fcb0b89ab83955bb8a10c8bfb8050dad004dc120))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-dependency-review.yml from 1.3.0.pre.beta.1 to 1.4.0.pre.beta.1 ([9b5e96d](https://github.com/paruff/uFawkesObs/commit/9b5e96deb3cee2f09a694d710c10ebcaa0fbd040))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-lint.yml ([4917bfd](https://github.com/paruff/uFawkesObs/commit/4917bfdaf8c8a1b658cf40303b6215b0c1770516))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-lint.yml ([10f2464](https://github.com/paruff/uFawkesObs/commit/10f24645f52d07fcb2c1d7fc84e1b6e356ccb684))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-lint.yml ([776094e](https://github.com/paruff/uFawkesObs/commit/776094e58407250c66dd61da22f05cb92dfc8c5b))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-lint.yml from 1.1.0 to 1.1.1 ([621743d](https://github.com/paruff/uFawkesObs/commit/621743ddcdc37b8913622981c8097555f7c797d6))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-lint.yml from 1.3.0.pre.beta.1 to 1.4.0.pre.beta.1 ([4adc0e4](https://github.com/paruff/uFawkesObs/commit/4adc0e4ffe130b547ec3428aab7e5b48e40e3496))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-preflight.yml ([07446a5](https://github.com/paruff/uFawkesObs/commit/07446a5158bf10a66eb665ae04dde2e6df189a50))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-preflight.yml ([8e27082](https://github.com/paruff/uFawkesObs/commit/8e27082863864d671b3d4d2ae592afee8f9268e0))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-preflight.yml ([81d563a](https://github.com/paruff/uFawkesObs/commit/81d563a0926e5d30285936676b5f95529c0cf170))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-preflight.yml from 1.1.0 to 1.1.1 ([ebc9cb5](https://github.com/paruff/uFawkesObs/commit/ebc9cb5fa277959c2d06bcd8eaae8fda35757c29))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-preflight.yml from 1.3.0.pre.beta.1 to 1.4.0.pre.beta.1 ([b181937](https://github.com/paruff/uFawkesObs/commit/b181937a26cbf4bfa9a44426aa7e254afc92fb57))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-security-scanning.yml ([855b020](https://github.com/paruff/uFawkesObs/commit/855b020f3c420ecc97fbea27ee894264374e6bf2))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-security-scanning.yml ([3bc0e47](https://github.com/paruff/uFawkesObs/commit/3bc0e47203ec8fe90b4e2ab4443affea61282020))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-security-scanning.yml ([d3a906f](https://github.com/paruff/uFawkesObs/commit/d3a906fddc00b9322493497219d3d8440cfe846d))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-security-scanning.yml from 1.1.0 to 1.1.1 ([72b193e](https://github.com/paruff/uFawkesObs/commit/72b193e16665947347450752d6b6123d5af6907a))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-security-scanning.yml from 1.3.0.pre.beta.1 to 1.4.0.pre.beta.1 ([ddd1076](https://github.com/paruff/uFawkesObs/commit/ddd10767a57acb14cb4ffcace2e226e4844595e7))
* **docs:** align plan.md with merged M4 tasks and create MODEL_POLICY.md ([1178342](https://github.com/paruff/uFawkesObs/commit/117834205a135c1be925c903c25c78439ead84e2))
* **docs:** align plan.md with merged M4 tasks and create MODEL_POLICY.md ([abe456b](https://github.com/paruff/uFawkesObs/commit/abe456b15026c659bd358a076a28bdde6256af93))
* **dora:** decommission Postgres/resource-plane backend, SQLite only ([ac28c95](https://github.com/paruff/uFawkesObs/commit/ac28c95d70c09e1d1a4137960b9762ba76d76e27))
* **dora:** decommission Postgres/resource-plane backend, SQLite only ([#275](https://github.com/paruff/uFawkesObs/issues/275)) ([08cf915](https://github.com/paruff/uFawkesObs/commit/08cf915ddbf95d5b909345c8c954770a42abf395))
* **governance:** adopt shared AGENTS.md template and fix downstream references ([a832308](https://github.com/paruff/uFawkesObs/commit/a8323080eb0098d7920b458ae9d5f33473b9b434))
* **governance:** adopt shared AGENTS.md template and fix downstream references ([f473388](https://github.com/paruff/uFawkesObs/commit/f4733887cf60b5a5cb9a164ac2adc2a72b25c90a))
* **main:** release 0.3.1-alpha.1 ([5864744](https://github.com/paruff/uFawkesObs/commit/5864744a17331a3e54a9c343cd47b4235fdb0acb))
* **main:** release 0.3.1-alpha.1 ([4c22391](https://github.com/paruff/uFawkesObs/commit/4c223911adce680099587f23865acb2c15112429))
* **main:** release 0.3.10-alpha.1 ([5d10985](https://github.com/paruff/uFawkesObs/commit/5d109850674f671477eca17b288a5d3d92fd1d53))
* **main:** release 0.3.10-alpha.1 ([739bea1](https://github.com/paruff/uFawkesObs/commit/739bea1a7393d3d1a0461637d4cdfb705555e4cd))
* **main:** release 0.3.11-alpha.1 ([9e11051](https://github.com/paruff/uFawkesObs/commit/9e11051b66efc54692a02e19009d1826e931dc3c))
* **main:** release 0.3.11-alpha.1 ([3bc2b23](https://github.com/paruff/uFawkesObs/commit/3bc2b23be0d8af2b2c06b4f41057b1f962e7ce42))
* **main:** release 0.3.12-alpha.1 ([7923767](https://github.com/paruff/uFawkesObs/commit/7923767ba7a66e90ff2e9f4ac7079afb9b88eb8f))
* **main:** release 0.3.12-alpha.1 ([3dabc5e](https://github.com/paruff/uFawkesObs/commit/3dabc5e354e80a066033b2a2800b2c7a8bd964a4))
* **main:** release 0.3.13-alpha.1 ([55eed1d](https://github.com/paruff/uFawkesObs/commit/55eed1d8c4453c4fd1d9068ab08c1ff43824493c))
* **main:** release 0.3.13-alpha.1 ([6e3094c](https://github.com/paruff/uFawkesObs/commit/6e3094c99c443aaf0a140444db9045f108f76a83))
* **main:** release 0.3.13-alpha.1 ([904ede0](https://github.com/paruff/uFawkesObs/commit/904ede0188d60ecc4c600b7233ec08575ba042c7))
* **main:** release 0.3.13-alpha.1 ([38a53a0](https://github.com/paruff/uFawkesObs/commit/38a53a0be0c94ebdbc61a0b1cded72969c97a32c))
* **main:** release 0.3.14-alpha.1 ([3aac4ed](https://github.com/paruff/uFawkesObs/commit/3aac4edb58ba98464d2b7a86faf60f357f2dc02c))
* **main:** release 0.3.14-alpha.1 ([fc7b05e](https://github.com/paruff/uFawkesObs/commit/fc7b05e3dbb53a53ba9e7c54718fb62dcbc6e2f7))
* **main:** release 0.3.15-alpha.1 ([4759e98](https://github.com/paruff/uFawkesObs/commit/4759e988582dc62c14eee13bf70b222c0ae39faf))
* **main:** release 0.3.15-alpha.1 ([3b0cd3e](https://github.com/paruff/uFawkesObs/commit/3b0cd3ee662fd70c676a69141150b0d4a7b5b347))
* **main:** release 0.3.16-alpha.1 ([45f4179](https://github.com/paruff/uFawkesObs/commit/45f4179054d2d965112903374dfd59a6da28335d))
* **main:** release 0.3.16-alpha.1 ([3d787ab](https://github.com/paruff/uFawkesObs/commit/3d787ab14e97744430875ffef603c59244707894))
* **main:** release 0.3.17-alpha.1 ([82796c6](https://github.com/paruff/uFawkesObs/commit/82796c651b7ef421e206eae1bd5d5d06a4c2393e))
* **main:** release 0.3.17-alpha.1 ([7db16ce](https://github.com/paruff/uFawkesObs/commit/7db16ceae7efe254d303b2065acd23d5a17264a9))
* **main:** release 0.3.18-alpha.1 ([a6e28f7](https://github.com/paruff/uFawkesObs/commit/a6e28f71b1a8353a1438e3981dd0a75dd24588ec))
* **main:** release 0.3.18-alpha.1 ([0176150](https://github.com/paruff/uFawkesObs/commit/0176150de78dc643f16c1ecbf794954c56b9894b))
* **main:** release 0.3.19-alpha.1 ([5871df9](https://github.com/paruff/uFawkesObs/commit/5871df9adf523aec168684b4dadcb37971b7c872))
* **main:** release 0.3.19-alpha.1 ([b0cf13b](https://github.com/paruff/uFawkesObs/commit/b0cf13bee7a6a17f2ae27e49c3835154b0d9739c))
* **main:** release 0.3.2-alpha.1 ([ee3d161](https://github.com/paruff/uFawkesObs/commit/ee3d161f6ac3104f33a4a19d8771ada3220dad5a))
* **main:** release 0.3.2-alpha.1 ([cdabdca](https://github.com/paruff/uFawkesObs/commit/cdabdca3d1625ee305ca2de6d3af7057754baa5e))
* **main:** release 0.3.20-alpha.1 ([2718a47](https://github.com/paruff/uFawkesObs/commit/2718a4786453a911f9a638b32c185690204fa02c))
* **main:** release 0.3.20-alpha.1 ([96eac1e](https://github.com/paruff/uFawkesObs/commit/96eac1ea00e0ef6946f7ff4d1a25255cf1dc537f))
* **main:** release 0.3.20-alpha.1 ([162e2f5](https://github.com/paruff/uFawkesObs/commit/162e2f56cbc906faa9b9bd98aea5516f7eb12f2a))
* **main:** release 0.3.21-alpha.1 ([7b8f55b](https://github.com/paruff/uFawkesObs/commit/7b8f55b890389da61ce0a856139ecb889f453755))
* **main:** release 0.3.3-alpha.1 ([b3545b1](https://github.com/paruff/uFawkesObs/commit/b3545b1a84b1d5047554a39ff11b291400f7321b))
* **main:** release 0.3.3-alpha.1 ([387ac09](https://github.com/paruff/uFawkesObs/commit/387ac09c0b55bff9bd1f5b7a220da06d996e679c))
* **main:** release 0.3.4-alpha.1 ([04c8738](https://github.com/paruff/uFawkesObs/commit/04c8738046c79e61f7ce3e4d66a02b7a43ff7009))
* **main:** release 0.3.4-alpha.1 ([9c9d74b](https://github.com/paruff/uFawkesObs/commit/9c9d74b42d039884657cdc2bcdde1c136db89e8a))
* **main:** release 0.3.5-alpha.1 ([7100da1](https://github.com/paruff/uFawkesObs/commit/7100da190ffd74a7ab4bf90cddc552b83d09ab15))
* **main:** release 0.3.5-alpha.1 ([e4350a3](https://github.com/paruff/uFawkesObs/commit/e4350a3dc366a37dae2c587e18857fe3a81a475f))
* **main:** release 0.3.6-alpha.1 ([deede0c](https://github.com/paruff/uFawkesObs/commit/deede0c5896a9711518061e8d92eb8713b24d4b7))
* **main:** release 0.3.6-alpha.1 ([f6ea4de](https://github.com/paruff/uFawkesObs/commit/f6ea4def9093c93c43d6b787a7dd86472cdfa427))
* **main:** release 0.3.7-alpha.1 ([8c32e06](https://github.com/paruff/uFawkesObs/commit/8c32e0675d7f7706750929d5c7778032f55958f1))
* **main:** release 0.3.7-alpha.1 ([d32efd1](https://github.com/paruff/uFawkesObs/commit/d32efd17a1309b72c9cd1a7d51fa1f0a7aaf1b9b))
* **main:** release 0.3.8-alpha.1 ([4c272b4](https://github.com/paruff/uFawkesObs/commit/4c272b4ec70121f024701ddc5190efa3e2a459bf))
* **main:** release 0.3.8-alpha.1 ([b450187](https://github.com/paruff/uFawkesObs/commit/b450187ff330517782385f1aaa4bb01a2cf3ef5e))
* **main:** release 0.3.9-alpha.1 ([a870ec4](https://github.com/paruff/uFawkesObs/commit/a870ec4d0aad10cc249a391544b3ecbf94028db8))
* **main:** release 0.3.9-alpha.1 ([e8acd06](https://github.com/paruff/uFawkesObs/commit/e8acd06710812e65ae6227b2b38d65485a7565bd))
* **make:** align Makefile with the consolidated CI pyramid ([b14347f](https://github.com/paruff/uFawkesObs/commit/b14347ff6362f8759b98d56a49abe0b59cbc8afd))
* **make:** align Makefile with the consolidated CI pyramid ([c1c320f](https://github.com/paruff/uFawkesObs/commit/c1c320fd9e6a50ac532215b548fbab7c1b315362))
* merge main into chore/ci-pyramid-consolidation ([2c160d0](https://github.com/paruff/uFawkesObs/commit/2c160d0debd29502b31682b9c3e842cb948bb9e3))
* **product:** measure time_to_first_signal_minutes onboarding baseline ([0dd20e5](https://github.com/paruff/uFawkesObs/commit/0dd20e585ea788f255a9b49c3c78962ef230fe52))
* **product:** measure time_to_first_signal_minutes onboarding baseline ([#179](https://github.com/paruff/uFawkesObs/issues/179)) ([7ff602e](https://github.com/paruff/uFawkesObs/commit/7ff602e1bba65f56f6831df1ff1cab6abc5a0519))
* **release:** automate releases off the Acceptance Full gate ([e68bae3](https://github.com/paruff/uFawkesObs/commit/e68bae32a23f3dd70f14c932bc6a7bf47293f3df))
* **release:** automate releases off the Acceptance Full gate ([6b491e7](https://github.com/paruff/uFawkesObs/commit/6b491e7cf731bd374c72289925e9b124e1171a64))
* remove temporary CI diagnosis and fix report files ([efa84f4](https://github.com/paruff/uFawkesObs/commit/efa84f45b188e1fc343f3d9a93286113043e34d0))
* remove temporary CI diagnosis and fix report files ([2edbd77](https://github.com/paruff/uFawkesObs/commit/2edbd778fa64201cf922e407c2b3807d338d7cbb))
* **repo:** audit remediation — P0/P1 findings from IMPLEMENTATION_PLAN.md ([05d589e](https://github.com/paruff/uFawkesObs/commit/05d589ebefd791ff4c3513862147a499830d4cac))
* **repo:** audit remediation — P0/P1 findings from IMPLEMENTATION_PLAN.md ([fc75d59](https://github.com/paruff/uFawkesObs/commit/fc75d59967bc7104cb31e18c1da233301232f337))
* trigger preflight rerun ([8f102d8](https://github.com/paruff/uFawkesObs/commit/8f102d8c18bbf195cf2b8a4e8406607d1cc8a1f1))

## [0.3.21-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.20-alpha.1...v0.3.21-alpha.1) (2026-09-23)


### Fixed

* **compose:** restrict internal/scrape-only ports to localhost ([#335](https://github.com/paruff/uFawkesObs/issues/335)) ([f8c9f2e](https://github.com/paruff/uFawkesObs/commit/f8c9f2eac73b9349f2049fdd8e4e093861731c74))
* **compose:** restrict internal/scrape-only ports to localhost ([#335](https://github.com/paruff/uFawkesObs/issues/335)) ([1637652](https://github.com/paruff/uFawkesObs/commit/1637652e6092d96039a7bb95fe5f137dc1fce694))
* **deploy:** alert on failure, log target IP for [#381](https://github.com/paruff/uFawkesObs/issues/381) diagnosis ([63aa964](https://github.com/paruff/uFawkesObs/commit/63aa9649e4e4d1e455cc1ad5cd369cceed80279b))
* **deploy:** alert on failure, log target IP for [#381](https://github.com/paruff/uFawkesObs/issues/381) diagnosis ([462f086](https://github.com/paruff/uFawkesObs/commit/462f0865e426a3e4ddd49bc1e326cc6b6becf039))


### Docs

* update blocker status in public-release tracker ([0c03396](https://github.com/paruff/uFawkesObs/commit/0c033968d9b8338a835fcb46b4f59b2a91b11647))
* update blocker status, PR-01/PR-03 fixed, PR-02 finding worse ([e03d0b4](https://github.com/paruff/uFawkesObs/commit/e03d0b4445257f51e6c1616047b2e59b33c9a1d4))

## [0.3.20-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.19-alpha.1...v0.3.20-alpha.1) (2026-09-23)


### Added

* add test coverage measurement, fix [#343](https://github.com/paruff/uFawkesObs/issues/343) ([768c430](https://github.com/paruff/uFawkesObs/commit/768c430505de29e7cd551014914dc6ab758d9459))


### Fixed

* land stranded test coverage measurement ([#343](https://github.com/paruff/uFawkesObs/issues/343)) ([a22aab0](https://github.com/paruff/uFawkesObs/commit/a22aab052c3af88a2c71ee7a7cb76cff5c5d7c39))


### Docs

* mark [#343](https://github.com/paruff/uFawkesObs/issues/343)/[#345](https://github.com/paruff/uFawkesObs/issues/345) done, correct chaos-nightly false alarm ([6c5574d](https://github.com/paruff/uFawkesObs/commit/6c5574dab091df78b8bb94df6b32fe150d3bdee3))
* restructure README for public release, close [#345](https://github.com/paruff/uFawkesObs/issues/345) ([63c6466](https://github.com/paruff/uFawkesObs/commit/63c6466197dca0633cd95892020ab1a3058fe84b))
* restructure README for public release, close [#345](https://github.com/paruff/uFawkesObs/issues/345) ([ff26f1e](https://github.com/paruff/uFawkesObs/commit/ff26f1e30db04c4548d29695100e07bf84fe7dc0))

## [0.3.19-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.18-alpha.1...v0.3.19-alpha.1) (2026-09-18)


### Chores

* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-build.yml ([65b6e2a](https://github.com/paruff/uFawkesObs/commit/65b6e2aed4c801511386b18c5abe4dd4ba19a453))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-build.yml from 1.3.0.pre.beta.1 to 1.4.0.pre.beta.1 ([eee648d](https://github.com/paruff/uFawkesObs/commit/eee648dda76bfa06960250610a14198c3da5dd94))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-dependency-review.yml ([483eda6](https://github.com/paruff/uFawkesObs/commit/483eda6827ef5eb1b0dc399b43b2dfd9fb865560))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-dependency-review.yml from 1.3.0.pre.beta.1 to 1.4.0.pre.beta.1 ([9b5e96d](https://github.com/paruff/uFawkesObs/commit/9b5e96deb3cee2f09a694d710c10ebcaa0fbd040))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-lint.yml ([4917bfd](https://github.com/paruff/uFawkesObs/commit/4917bfdaf8c8a1b658cf40303b6215b0c1770516))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-lint.yml from 1.3.0.pre.beta.1 to 1.4.0.pre.beta.1 ([4adc0e4](https://github.com/paruff/uFawkesObs/commit/4adc0e4ffe130b547ec3428aab7e5b48e40e3496))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-preflight.yml ([07446a5](https://github.com/paruff/uFawkesObs/commit/07446a5158bf10a66eb665ae04dde2e6df189a50))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-preflight.yml from 1.3.0.pre.beta.1 to 1.4.0.pre.beta.1 ([b181937](https://github.com/paruff/uFawkesObs/commit/b181937a26cbf4bfa9a44426aa7e254afc92fb57))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-security-scanning.yml ([855b020](https://github.com/paruff/uFawkesObs/commit/855b020f3c420ecc97fbea27ee894264374e6bf2))
* **deps:** bump paruff/ufawkespipe/.github/workflows/reusable-security-scanning.yml from 1.3.0.pre.beta.1 to 1.4.0.pre.beta.1 ([ddd1076](https://github.com/paruff/uFawkesObs/commit/ddd10767a57acb14cb4ffcace2e226e4844595e7))

## [0.3.18-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.17-alpha.1...v0.3.18-alpha.1) (2026-09-14)


### Fixed

* **ci:** restore bash:deny on opencode.yml, dropped during [#350](https://github.com/paruff/uFawkesObs/issues/350) consolidation ([2cfc8a3](https://github.com/paruff/uFawkesObs/commit/2cfc8a39e74694a00ffd3808acc3f3450ec19b72))
* **ci:** restore bash:deny on opencode.yml, dropped during [#350](https://github.com/paruff/uFawkesObs/issues/350) consolidation ([b62e99e](https://github.com/paruff/uFawkesObs/commit/b62e99e8b16ef14085ff8863beb18d4b72a0630b))

## [0.3.17-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.16-alpha.1...v0.3.17-alpha.1) (2026-09-13)


### Docs

* integrate expert feedback — M5 migration to Fawkes track ([ce4e4f0](https://github.com/paruff/uFawkesObs/commit/ce4e4f0c6449acd15332da65210733bf9dc9c52e))
* integrate expert feedback — M5 migration to Fawkes, non-goals updated ([37742b1](https://github.com/paruff/uFawkesObs/commit/37742b16f2ddbf1abf132e01816fadb54dd84926))

## [0.3.16-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.15-alpha.1...v0.3.16-alpha.1) (2026-09-13)


### Docs

* cross-link governance docs and add late-beta closeout week plan ([29b7daf](https://github.com/paruff/uFawkesObs/commit/29b7daf656edf640d2f2be47293c586425a2999a))

## [0.3.15-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.14-alpha.1...v0.3.15-alpha.1) (2026-09-13)


### Docs

* consolidate planning cascade from PATH_TO_LATE_BETA.md ([382361b](https://github.com/paruff/uFawkesObs/commit/382361bfefea79d17391234d592b9a75d7cade55))
* consolidate planning cascade from PATH_TO_LATE_BETA.md ([bd43142](https://github.com/paruff/uFawkesObs/commit/bd43142138622b240663037b9b5eaf5e03784826))

## [0.3.14-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.13-alpha.1...v0.3.14-alpha.1) (2026-09-13)


### Chores

* **main:** release 0.3.13-alpha.1 ([55eed1d](https://github.com/paruff/uFawkesObs/commit/55eed1d8c4453c4fd1d9068ab08c1ff43824493c))
* **main:** release 0.3.13-alpha.1 ([6e3094c](https://github.com/paruff/uFawkesObs/commit/6e3094c99c443aaf0a140444db9045f108f76a83))

## [0.3.13-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.12-alpha.1...v0.3.13-alpha.1) (2026-09-13)


### Fixed

* **test:** match CI's DORA compute interval in local acceptance runs ([33a68b1](https://github.com/paruff/uFawkesObs/commit/33a68b116110e9147532025ff479334b096deaf0))
* **test:** match CI's DORA compute interval in local acceptance runs ([e3e6980](https://github.com/paruff/uFawkesObs/commit/e3e6980b08b65f1e8cf1a48425b8a5526ddd5897))


### Docs

* add 4-tier planning cascade and link product artifacts ([5eea7f1](https://github.com/paruff/uFawkesObs/commit/5eea7f1e709c2f4a5d7d69b0d9894da67f1ad6ae))
* consolidate opencode workflows, fix issue [#350](https://github.com/paruff/uFawkesObs/issues/350) ([68bf1a0](https://github.com/paruff/uFawkesObs/commit/68bf1a0100cfb5eefe1521cc4178a8acd5557408))
* reconcile docs drift, relocate files, document test pyramid ([872ebd2](https://github.com/paruff/uFawkesObs/commit/872ebd2d2d02817ef4b2eccbccd2de0b0c0eae1e))
* reconcile docs drift, relocate files, document test pyramid ([#342](https://github.com/paruff/uFawkesObs/issues/342)-[#351](https://github.com/paruff/uFawkesObs/issues/351)) ([fc503b3](https://github.com/paruff/uFawkesObs/commit/fc503b35f17a85408d0d00cb63512cbb41e212ba))
* refactor MODEL_POLICY.md to grade-based system with benchmark thresholds ([bb3db75](https://github.com/paruff/uFawkesObs/commit/bb3db759b34144cdd6d4f28a31dcfe4c3485acd0))
* update main-ci-guard to stable workflow version, fix issue [#352](https://github.com/paruff/uFawkesObs/issues/352) ([30d0b30](https://github.com/paruff/uFawkesObs/commit/30d0b30caa2e29ce6190b38469b1bd67fad69608))
* update MODEL_POLICY.md to reflect OpenCode setup, fix issue [#346](https://github.com/paruff/uFawkesObs/issues/346) ([79d241d](https://github.com/paruff/uFawkesObs/commit/79d241d232866437de6439ce449fda9b5765eeb2))
* update plan-for-the-day.md with completed tasks ([d403052](https://github.com/paruff/uFawkesObs/commit/d403052b571a3191dde807c43007e52c0315933f))
* update session retrospective with learnings ([60fc307](https://github.com/paruff/uFawkesObs/commit/60fc307dfc7be200caf29ec9f1a83661a928ed11))

## [0.3.12-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.11-alpha.1...v0.3.12-alpha.1) (2026-09-12)


### Fixed

* **deploy:** resolve the diff base to a SHA instead of a caret ref ([e14e558](https://github.com/paruff/uFawkesObs/commit/e14e55865f97929f9fbb3bdba99ea1f947278326))
* **deploy:** resolve the diff base to a SHA instead of a caret ref ([1a777ce](https://github.com/paruff/uFawkesObs/commit/1a777ce0d86c85371b1ac6a82402f043ff8a9db0))


### Chores

* **deps:** bump anomalyco/opencode/github from 1.18.26 to 1.18.29 ([bbfd7aa](https://github.com/paruff/uFawkesObs/commit/bbfd7aa21d29d47feb77450b65cbf353d0426d15))
* **deps:** bump anomalyco/opencode/github from 1.18.26 to 1.18.29 ([bd2e762](https://github.com/paruff/uFawkesObs/commit/bd2e7623df623a31014b4720dd5f97607a9b1652))

## [0.3.11-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.10-alpha.1...v0.3.11-alpha.1) (2026-09-04)


### Fixed

* **ci:** fail the readiness gate when a service never becomes healthy ([8d8fc3d](https://github.com/paruff/uFawkesObs/commit/8d8fc3da6ab7e29a3e1bcf6cbbd93afdf819b08e))
* **ci:** fail the readiness gate when a service never becomes healthy ([da9cc40](https://github.com/paruff/uFawkesObs/commit/da9cc40e50848a28452fdb5e5f1ecc0469bd9e53))


### Docs

* **deploy:** add Synology drill-host provisioning for LB-04 ([9aaaef9](https://github.com/paruff/uFawkesObs/commit/9aaaef98cc0ce70a317032395a26d2c289648a36))
* **deploy:** add Synology drill-host provisioning for LB-04 ([ac72c9a](https://github.com/paruff/uFawkesObs/commit/ac72c9a09d71df293e3c821a0a344124e6b9d486))


### Changed

* **dora:** fold the compute loop into dora-api, drop Pushgateway ([124b79d](https://github.com/paruff/uFawkesObs/commit/124b79da823cf037c769ea7bf7faab4887639846))


### Chores

* **deps:** bump googleapis/release-please-action from 4.4.1 to 5.0.0 ([d45a9b6](https://github.com/paruff/uFawkesObs/commit/d45a9b6592f39c4ded10aa599cf637b754d9f8a5))
* **deps:** bump googleapis/release-please-action from 4.4.1 to 5.0.0 ([74e122d](https://github.com/paruff/uFawkesObs/commit/74e122de36e34ba8e1f6b7b4e5729deed4070c9b))

## [0.3.10-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.9-alpha.1...v0.3.10-alpha.1) (2026-09-02)


### Docs

* Fawkes replaces uFawkesObs wholesale, not consumes it ([2292b71](https://github.com/paruff/uFawkesObs/commit/2292b71393fcf6d1de473f8409327078949bdfbd))
* Fawkes replaces uFawkesObs wholesale, not consumes it ([a435575](https://github.com/paruff/uFawkesObs/commit/a435575b55c3eb7f25d0e47e1c76d7deb3b7a916))

## [0.3.9-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.8-alpha.1...v0.3.9-alpha.1) (2026-09-02)


### Fixed

* **deploy:** make the health gate run on the deploy host, guard rollback bootstrap ([98b0937](https://github.com/paruff/uFawkesObs/commit/98b09377b11804683b5dbc963cf9ad17ec3d645f))


### Changed

* **dora:** remove the dormant otel-collector-dora container ([7164527](https://github.com/paruff/uFawkesObs/commit/71645276c49cf60e847e4177fefa8970f944b08b))
* **dora:** remove the dormant otel-collector-dora container ([d854732](https://github.com/paruff/uFawkesObs/commit/d85473223844f9a2f10cf2dc5961afbd95d4d809))

## [0.3.8-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.7-alpha.1...v0.3.8-alpha.1) (2026-09-02)


### Docs

* **deploy:** record LB-04 rollback drill results ([d12aae1](https://github.com/paruff/uFawkesObs/commit/d12aae19231250dbc2f44761617d61ee811d7994))
* **deploy:** record LB-04 rollback drill results ([3a4a754](https://github.com/paruff/uFawkesObs/commit/3a4a754c58faaee49f2e52a5694f8bfa3a2f1cdd))

## [0.3.7-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.6-alpha.1...v0.3.7-alpha.1) (2026-09-02)


### Fixed

* **ci:** align opencode pin to the v1.18.x series used across the family ([bb902d4](https://github.com/paruff/uFawkesObs/commit/bb902d4b569d15f861d19ef4a33230eaab577659))
* **ci:** align opencode pin to the v1.18.x series used across the family ([04972af](https://github.com/paruff/uFawkesObs/commit/04972af0d70618bee22510a7e4d4e5ca80c952b9))
* **dora:** use set -eu in POSIX sh collectors, add shellcheck pre-commit hook ([e795810](https://github.com/paruff/uFawkesObs/commit/e7958102c3a687faefed54b026d4a1659c074c03))
* resolve audit medium findings M-1, M-2, M-3 ([1aef6de](https://github.com/paruff/uFawkesObs/commit/1aef6de3bc3a988042ff0487539cf17f1bc253a7))

## [0.3.6-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.5-alpha.1...v0.3.6-alpha.1) (2026-09-02)


### Fixed

* **ci:** SHA-pin third-party actions and repoint opencode to a live upstream ([5d41220](https://github.com/paruff/uFawkesObs/commit/5d41220a5f2b534237c439072b520fbaf976dbb7))

## [0.3.5-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.4-alpha.1...v0.3.5-alpha.1) (2026-09-02)


### Fixed

* **ci:** gate opencode's issues trigger on author_association ([1b7e991](https://github.com/paruff/uFawkesObs/commit/1b7e9916fc43f9faa8220bb1d3ec55578bae4a5b))
* **ci:** gate opencode's issues trigger on author_association ([200ad15](https://github.com/paruff/uFawkesObs/commit/200ad1512545beaeeda93ce1d6629843239aabb8))
* **security:** reject the REPLACE_ME placeholder in the Grafana guard ([3ec4d4c](https://github.com/paruff/uFawkesObs/commit/3ec4d4cd88ab2c13da6dce9ce15fa0e127dadd36))
* **security:** reject the REPLACE_ME placeholder in the Grafana guard ([be0e5df](https://github.com/paruff/uFawkesObs/commit/be0e5dfec1b3e05436d2f4cc15661c401f35817f))

## [0.3.4-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.3-alpha.1...v0.3.4-alpha.1) (2026-08-31)


### Fixed

* **acceptance:** only stop stack in auto mode if we started it ([2033328](https://github.com/paruff/uFawkesObs/commit/20333286ae490c212b6f6a5d202007f7f734ac5b))
* **acceptance:** only stop stack in auto mode if we started it ([#310](https://github.com/paruff/uFawkesObs/issues/310)) ([523c95c](https://github.com/paruff/uFawkesObs/commit/523c95c2b1743cb60022a66e27b90e99d916ea8f))
* **acceptance:** only tear down the stack if this session started it ([c4ed384](https://github.com/paruff/uFawkesObs/commit/c4ed38484b15f5a08909093dd9448e745269a2fc))
* **acceptance:** only tear down the stack if this session started it ([ae774c0](https://github.com/paruff/uFawkesObs/commit/ae774c03226ba6ef0d0018429b97e7ef82ad6e6f)), closes [#310](https://github.com/paruff/uFawkesObs/issues/310)
* **deploy:** pin detect-changes diff base explicitly for workflow_run ([acbdeae](https://github.com/paruff/uFawkesObs/commit/acbdeaea2664a52e8605b044bfab469a2248618b))
* **deploy:** pin detect-changes diff base explicitly for workflow_run ([eb5cf8c](https://github.com/paruff/uFawkesObs/commit/eb5cf8c77b7fab0befad5d2a788b9e88f9e05656)), closes [#301](https://github.com/paruff/uFawkesObs/issues/301)
* **observability:** seed telemetry-generator traffic and wait for propagation ([5122b6e](https://github.com/paruff/uFawkesObs/commit/5122b6e660d1a1e9bebd7dcf7714af5da4dd2d8e))

## [0.3.3-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.2-alpha.1...v0.3.3-alpha.1) (2026-08-31)


### Fixed

* **acceptance:** raise OBS-CONTRACT-001's Tempo timeout to 30s ([f5f82be](https://github.com/paruff/uFawkesObs/commit/f5f82be73509e28311e508bd3f21455b7adda835))

## [0.3.2-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.1-alpha.1...v0.3.2-alpha.1) (2026-08-31)


### Fixed

* **compose:** document and correctly exempt distroless healthchecks ([e23984f](https://github.com/paruff/uFawkesObs/commit/e23984fe9402ac9d39937886d4a41db945590c59))

## [0.3.1-alpha.1](https://github.com/paruff/uFawkesObs/compare/v0.3.0-alpha.1...v0.3.1-alpha.1) (2026-08-31)


### Added

* **ci:** add Acceptance Full to main-ci-guard, document real gate ([38b23b0](https://github.com/paruff/uFawkesObs/commit/38b23b0b0110650b36e716a42e049c874d7199c9))


### Fixed

* **acceptance:** resolve remaining Acceptance Full failure + add diagnostics ([60f135b](https://github.com/paruff/uFawkesObs/commit/60f135b1a40218da3a92fe7cf8d409e39b24c86c))
* **acceptance:** wait for seeded DORA metric before asserting ([5f2afd5](https://github.com/paruff/uFawkesObs/commit/5f2afd5e2a6bf0a8150b089e1acb1219ab98e8d8))
* **ci:** exclude CHANGELOG.md from markdownlint ([c3e65b3](https://github.com/paruff/uFawkesObs/commit/c3e65b358cd6c71b59f4823082258da44d46daba))
* **ci:** exclude CHANGELOG.md from markdownlint ([db74c9e](https://github.com/paruff/uFawkesObs/commit/db74c9efb33126df4fe995525974c9f6e2380d03))
* **ci:** guard undefined trackingIssue in health-guard script ([0943102](https://github.com/paruff/uFawkesObs/commit/09431024389b8d2ff9c3c3d23edbc8b68b6d4b76))
* **ci:** guard undefined trackingIssue in health-guard script ([e37d643](https://github.com/paruff/uFawkesObs/commit/e37d643fe8e548f8732b32a710330f7653652d3e))
* **ci:** remove duplicate acceptance-smoke job, run smoke standalone ([4e531a5](https://github.com/paruff/uFawkesObs/commit/4e531a53086cd974f2b81e952e0353a57f623ddf))
* **ci:** unblock Release Please with a PAT-capable token ([092bb99](https://github.com/paruff/uFawkesObs/commit/092bb99cfc3d00d6d2c7480e978b665e918e3e76))
* **ci:** unblock Release Please with a PAT-capable token ([ba63659](https://github.com/paruff/uFawkesObs/commit/ba63659dd5656b4e29f86cc42f1f9e1e298cb255))
* **ci:** use the real pushgateway compose service name ([d9ac27e](https://github.com/paruff/uFawkesObs/commit/d9ac27ea065e4c4e035a9531788b2b2e8d0db347))
* **dora:** attribute manual incident events to the real repo ([f2a8697](https://github.com/paruff/uFawkesObs/commit/f2a8697a4a000607442c7e7e17cf4c391f5fc66d))
* **dora:** break FDRT deployment-order ties with row id ([e3adfce](https://github.com/paruff/uFawkesObs/commit/e3adfce92a3bfb8277ab4060f9f52a3eea4e05c7))
* **dora:** close GHA script injection in collectors ([7dc6eb4](https://github.com/paruff/uFawkesObs/commit/7dc6eb4df6593ff11e922f2b35fd08434aa6d40d))
* **dora:** close GHA script injection in reusable collector workflows ([1e18051](https://github.com/paruff/uFawkesObs/commit/1e180514bda02dcfeaabc102d4fb946181a4960a))
* **dora:** close remaining HIGH-severity review findings ([#278](https://github.com/paruff/uFawkesObs/issues/278), [#279](https://github.com/paruff/uFawkesObs/issues/279), [#280](https://github.com/paruff/uFawkesObs/issues/280)) ([417966c](https://github.com/paruff/uFawkesObs/commit/417966cb6399a96d59975e16b454ba1d976e9c36))
* **dora:** close the six MEDIUM review findings ([#281](https://github.com/paruff/uFawkesObs/issues/281)-286) ([342911e](https://github.com/paruff/uFawkesObs/commit/342911ea12af8d36bc2571537cc11c8bf2d8b4d0))
* **dora:** curl-examples.sh doesn't match its own event schemas ([#280](https://github.com/paruff/uFawkesObs/issues/280)) ([e177d5e](https://github.com/paruff/uFawkesObs/commit/e177d5e16da86511cac78f3c4e88ab5deb6f6e10))
* **dora:** escape team_id in Prometheus label/URL output ([#276](https://github.com/paruff/uFawkesObs/issues/276)) ([dc015c8](https://github.com/paruff/uFawkesObs/commit/dc015c8d489848a7e7f8b4c453343fb351a96c7c))
* **dora:** feed Lead Time and FDRT from real deployment events ([ae26c15](https://github.com/paruff/uFawkesObs/commit/ae26c153a9fda91608da57bca7450ef3f1c7e44d))
* **dora:** feed Lead Time and FDRT from real deployment events ([#267](https://github.com/paruff/uFawkesObs/issues/267)) ([4ea41f4](https://github.com/paruff/uFawkesObs/commit/4ea41f4ed2ea356e8ad2268708839b5f86fc4f26))
* **dora:** repoint dora-metrics.json's recording rules at the fed pipeline ([c94d257](https://github.com/paruff/uFawkesObs/commit/c94d257165f937ccc5e62409456ee4afbfdaa020))
* **dora:** repoint dora-metrics.json's recording rules at the fed pipeline ([5a26e20](https://github.com/paruff/uFawkesObs/commit/5a26e206d4b0d6b084a5c185f8edf580e3b68043))
* **dora:** scale regression alert thresholds to the real ratio range ([55ba6bb](https://github.com/paruff/uFawkesObs/commit/55ba6bbe2dec44e44bc3964c4cd86b4e8493edc5))
* **dora:** send DORA_API_KEY from the deploy-event script ([00af213](https://github.com/paruff/uFawkesObs/commit/00af213d764f72ab0b7e589e1f47c4e26be2c37d))
* **dora:** use Pushgateway job@base64 path for team_id ([b36eefc](https://github.com/paruff/uFawkesObs/commit/b36eefcbfb1a3b9bd8a2127ac41022236a7c4d77))
* **dora:** use Pushgateway job@base64 path for team_id ([bb86756](https://github.com/paruff/uFawkesObs/commit/bb86756cb96468f26ec91754fdf80698c9b2f84a))
* **dora:** Woodpecker collector snippet fails schema validation ([#279](https://github.com/paruff/uFawkesObs/issues/279)) ([7f98734](https://github.com/paruff/uFawkesObs/commit/7f98734072f5d898783e8f1493d3dc2f8441e989))


### Docs

* **ci:** correct required-check names to what PR [#298](https://github.com/paruff/uFawkesObs/issues/298) actually shows ([939b240](https://github.com/paruff/uFawkesObs/commit/939b2407712c427283cb268640615c04c72e60ca))
* **ci:** rename Chaos Nightly workflow to Chaos Resilience (Nightly) ([d83e46e](https://github.com/paruff/uFawkesObs/commit/d83e46e181531115efd0ffdd2be882af997e5a52))
* **ci:** rename CI Quality workflow to Quality & Security Gates ([c5fafb4](https://github.com/paruff/uFawkesObs/commit/c5fafb4d3e14b346aa1fe1939ea42f6bdcd332c4))
* **ci:** rename Repo Hygiene workflow and Pre-commit Hooks job ([44452e0](https://github.com/paruff/uFawkesObs/commit/44452e06edcd418c2cf01d6ab746afe3b4107095))
* **dora:** amend ADR-006, the OTLP ingestion model was never built ([ff73c04](https://github.com/paruff/uFawkesObs/commit/ff73c04366da78f1efe87878f1247c0d777aeb21))
* **dora:** document dora-api's fail-open auth default ([a7bc727](https://github.com/paruff/uFawkesObs/commit/a7bc72764bb52800e9bff58ee90b7b1b7c03b20e))


### Changed

* **dora:** collapse _merge_team_results' 5x duplicated logic ([ef8a7bc](https://github.com/paruff/uFawkesObs/commit/ef8a7bc19c553e2220a39c82f517e1759326afdb))


### Chores

* **ci:** consolidate workflow naming into a clear test pyramid ([8100373](https://github.com/paruff/uFawkesObs/commit/81003739b6891d68f481fd5c8093ff2e70074e10))
* **deploy:** comment-only change to prove deploy.yml SSH connectivity ([#182](https://github.com/paruff/uFawkesObs/issues/182)) ([27c1eea](https://github.com/paruff/uFawkesObs/commit/27c1eea65b552fe7c3df54a15c125e6acf04957a))
* **deploy:** prove deploy.yml SSH connectivity before the LB-04 drill ([8c64f0d](https://github.com/paruff/uFawkesObs/commit/8c64f0d1bba75c48823eba553ee72d0700b3623f))
* **dora:** decommission Postgres/resource-plane backend, SQLite only ([ac28c95](https://github.com/paruff/uFawkesObs/commit/ac28c95d70c09e1d1a4137960b9762ba76d76e27))
* **dora:** decommission Postgres/resource-plane backend, SQLite only ([#275](https://github.com/paruff/uFawkesObs/issues/275)) ([08cf915](https://github.com/paruff/uFawkesObs/commit/08cf915ddbf95d5b909345c8c954770a42abf395))
* **make:** align Makefile with the consolidated CI pyramid ([b14347f](https://github.com/paruff/uFawkesObs/commit/b14347ff6362f8759b98d56a49abe0b59cbc8afd))
* **make:** align Makefile with the consolidated CI pyramid ([c1c320f](https://github.com/paruff/uFawkesObs/commit/c1c320fd9e6a50ac532215b548fbab7c1b315362))
* merge main into chore/ci-pyramid-consolidation ([2c160d0](https://github.com/paruff/uFawkesObs/commit/2c160d0debd29502b31682b9c3e842cb948bb9e3))
* **release:** automate releases off the Acceptance Full gate ([e68bae3](https://github.com/paruff/uFawkesObs/commit/e68bae32a23f3dd70f14c932bc6a7bf47293f3df))
* **release:** automate releases off the Acceptance Full gate ([6b491e7](https://github.com/paruff/uFawkesObs/commit/6b491e7cf731bd374c72289925e9b124e1171a64))

## [Unreleased]

## [0.3.0-alpha.1] — 2026-08-31

Checkpoint release ahead of the LB-04 live rollback drill — 25 PRs merged
since v0.2.0. Marked alpha because the drill itself (the thing this release
exists to precede) hasn't run yet; the deploy/rollback mechanism it will
exercise is implemented and unit-tested but not yet live-verified.

### Added

- **Tag-based deploy/rollback redesign** (LB-04, #248): deploy now targets an
  immutable `deploy-<ts>-<sha>` tag instead of `main`'s moving HEAD; rollback
  checks out `deploy-latest-good` instead of reverting and pushing to
  `main` — neither path touches `main`'s branch protection anymore
- Acceptance Full health guard and explicit deploy-skip summaries (#261)
- Service Error/Latency/SLO dashboards (#250, #256)
- Beta feedback channel (#243)
- Regression guards for the rollback SSH credential model (#239)

### Fixed

- **Slack notification recipe for Alertmanager, verified live** (LB-03,
  #262): the previously-merged recipe never actually worked — Alertmanager
  doesn't expand `${VAR}` inside its own config file. Rebuilt on
  `api_url_file` + a Docker Compose secret, confirmed delivering real
  alerts to a real Slack channel
- SLO summary print always showed FAIL for non-latency SLIs (#257)
- DORA Overview dashboard empty in fresh CI (#259); unwired DORA stub
  dashboards removed (#258)
- OBS-SLI-006's 17-day-red gate root-caused and fixed (#252)
- DORA `event_queue` duplicate writes on identical payload (#249)
- Public-release doc audit: broken link, stale Prometheus version, blocked
  LB-04 status corrected (#260)
- CI: opencode `external_directory` write permissions (#247); uFawkesPipe
  reusable workflows bumped to v1.3.0-beta.1 (#241)

### Docs

- LB-02, LB-05, LB-06 marked done in Path to Late Beta (#246, #245)
- `pr-review-block` skill relocated (#244)
- Pre-release cruft removed, stale media-refinery references fixed (#238)

## [0.2.0] — 2026-08-18

### Added

- `good-first-issue` label and GitHub metadata standards (M2-02)
- `.github/dependabot.yml` Docker ecosystem for `compose.yaml` image scanning
- **CONTRIBUTING.md, CODE_OF_CONDUCT.md, GitHub issue templates** (M2-01, issue #71)
- **Cross-plane integration guides** (Milestone 3): uFawkesPipe and uFawkesDevX
  telemetry integration guides, Backstage catalog registration
  (`catalog-info.yaml`), expanded multi-stack integration guide with
  Kubernetes integration section and minimal-startup patterns, and
  `docker-compose.integration.yml` for joining sister-plane stacks
  (issues #76-79, #54; PR #131, #133, #134, #135, #136, #138)
- **DORA metrics & ecosystem integration** (Milestone 4): `docs/adr/ADR-006-dora-metric-definitions.md`
  data contract, `dora` compose profile wiring `otel-collector-dora` to
  uFawkesDORA's ingestion API and uFawkesRes's shared PostgreSQL, 5 Prometheus
  DORA recording rules (deployment frequency, lead time, change failure rate,
  FDRT, and DORA-2026's 5th metric — rework rate) with paired alert rules, and
  a provisioned Grafana DORA metrics dashboard (issues #80-83, #51-53; PR #147,
  #148, #154, #149/#155)
- **`dora` profile is now self-contained by default (SQLite-backed)**: `dora-api` and `dora-compute` store events in a local SQLite file under `./data/dora` with no external database required, matching the same metric math as the Postgres backend. A new `resource-plane` profile plus `compose.resource-plane.override.yaml` swaps in the shared uFawkesRes Postgres instance instead (`make up-dora-resource-plane`), gated behind `DORA_POSTGRES_URL`. See AGENTS.md §10.
- **Acceptance test suite**: BDD-style acceptance tests across 7 phases (SLOs,
  synthetic workload generators, chaos/failure-injection scenarios, evidence
  capture, CI integration) plus a nightly chaos test workflow
  (`.github/workflows/ci-chaos-nightly.yml`)
- **GitOps lifecycle gates**: post-deployment verification and automatic
  rollback on failed smoke tests (PR #166)
- `AGENTS.md` template guidance for reuse across repos (PR #150)
- `docs/product/` and `docs/features/` directories separating product-level
  discovery/spec/design docs from per-feature pipeline output (repo hygiene)

### Changed

- `.github/FUNDING.yml` syntax to GitHub array format
- **Prometheus upgraded** from v2.55.1 → v3.5.4 (PR #136)
- DORA scope narrowed per `docs/reviews/M4-02-ecosystem-review.md`: DevLake +
  MySQL moved to uFawkesDORA's own stack; uFawkesObs's DORA responsibility is
  now limited to the data contract, recording rules, and dashboard
- `compose.yaml`'s `otel-collector-dora.DORA_POSTGRES_URL` no longer has a
  hardcoded credential fallback — now a required `.env` value, documented in
  `.env.example`

### Fixed

- `dora-api`, `dora-compute`, and `dora-db-init` now join
  `fawkes-backbone-net` (where uFawkesRes's shared Postgres actually lives),
  fixing a structural network gap that prevented the `resource-plane`
  profile from reaching its database despite valid credentials (PR #237)
- Stale `media-refinery` app references in `docs/OBSERVABILITY_STATUS.md`
  corrected to `telemetry-generator` (the actual demo app)
- Reconciled `docs/plan.md` status column against real GitHub issue state
  (multiple tasks were done but still shown pending)
- **Closed superseded/duplicate backlog issues as part of LB-07 (#185):** #51–#54
  (OBS-DORA DevLake design) and M4 tracking issues #80–#83 closed as superseded
  by the M4 rework, linking `docs/reviews/M4-02-ecosystem-review.md`; #71 closure
  verified and documented. `docs/plan.md` status column now matches
  `gh issue list --state all` as of 2026-08-12.

## [0.1.0] — 2026-06-28

### Added

- **Initial observability stack:** Docker Compose with OpenTelemetry Collector v0.120.0,
  Prometheus v2.55.1, Alertmanager v0.28.0, Tempo v2.10.5, Loki v3.3.2, Alloy v1.12.2,
  and Grafana v12.3.7
- **OTel AI metrics pipeline:** `metrics/ai` pipeline with `filter/ai` + `attributes/ai`
  processors for LLM telemetry routing (issue #55)
- **Prometheus AI recording rules:** `ai:llm_token_rate:rate5m`,
  `ai:suggestion_latency:percentile99`, `ai:suggestion_acceptance_rate:ratio`,
  `ai:rework_rate:ratio` — all guarded with `or vector(0)` (issue #56)
- **Prometheus AI alert rules:** 8 alerts covering P99 latency spikes, acceptance drops,
  rework rate increases, token rate anomalies, and composite capability degradation —
  grouped by DORA 2025 performance bands
- **Grafana AI capabilities dashboard:** 9-panel dashboard with DORA 2025 thresholds —
  latency P99/P50, token rate, acceptance rate, rework rate, and alertlist (issue #57)
- **AI observability documentation:** `docs/ai-observability-guide.md` with architecture
  diagram, metrics/alert/dashboard reference, and instrumentation guide (issue #58)
- **AI runbook:** `docs/ai-runbook.md` with step-by-step remediation for all 8 alerts (issue #56)
- **ADR-001:** Loki version upgrade decision (v2.9.10 → v3.3.2)
- **ADR-004:** Grafana 12.x migration decision (v10.4.5 → v12.3.7)
- **Unit tests:** schema version guards and static assertion tests
- **CI/CD pipeline:** Phase 1 (lint, validate-config, smoke, test, security) and Phase 2
  (reusable workflows via uFawkesPipe@v1.1.0, supply chain, coverage thresholds)
- **Repository skeleton:** `.github/` templates (issue templates, PR template, Copilot
  instructions), `.gitignore`, Makefile with common commands
- **Scripts:** `start.sh`, `stop.sh`, `healthcheck.sh`, `smoke-test.sh`, `pr-create.sh`,
  Makefile pr shortcut
- **Docs:** ARCHITECTURE.md, CHANGE_IMPACT_MAP.md, KNOWN_LIMITATIONS.md, AGENTS.md,
  ADR README, multi-stack-integration.md

### Changed

- **Loki upgraded** from v2.9.10 → v3.3.2 with config migration for schema v13 and
  removed legacy `boltdb_shipper` (PR #116)
- **Grafana upgraded** from v10.4.5 → v12.3.7 with dashboard JSON migration to
  `schemaVersion: 40` and `uid`-based datasource references (PR #115)
- **Alertmanager upgraded** from v0.27.0 → v0.28.0 for CVE fixes (PR #114)
- **Tempo upgraded** from v2.5.0 → v2.10.5 (PR #100)
- **README version table** synced to match `compose.yaml` (PR #117)
- **CI consolidated** from 10 workflows to 4 (PR #106)
- **Reusable workflows** migrated to uFawkesPipe@v1.1.0 (PR #121)
- **Pre-release cleanup:** naming, docs, compose labels (PR #113)
- **ADRs, ARCHITECTURE.md, obs-stack skill** synced to match `compose.yaml` versions (PR #125)
- **AGENTS.md, OTel collector skill, CHANGE_IMPACT_MAP.md** updated with AI observability
  documentation (PR #127)

### Fixed

- `ai-rules.yml` path — moved to `config/prometheus/rules/` to match Docker volume mount
  (PR #124)
- CI main failures: Trivy action version, Gitleaks v3 migration, dependency review
  (PR #110)
- Pre-commit hook failures: trailing whitespace, markdownlint (PR #106)
- Shellcheck SC2001 warnings in scripts (PR #112)

### Dependencies

- Bumped `actions/cache` 5→6, `actions/checkout` 4→6/6→7, `actions/setup-python` 5→6,
  `actions/upload-artifact` 4→7, `actions/github-script` 7→9, `webfactory/ssh-agent`
  0.9.0→0.10.0, `aquasecurity/trivy-action` 0.35.0→0.36.0, `dorny/paths-filter` 3→4,
  `actions/dependency-review-action` 4→5

[Unreleased]: https://github.com/paruff/uFawkesObs/compare/v0.3.0-alpha.1...HEAD
[0.3.0-alpha.1]: https://github.com/paruff/uFawkesObs/compare/v0.2.0...v0.3.0-alpha.1
[0.2.0]: https://github.com/paruff/uFawkesObs/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/paruff/uFawkesObs/releases/tag/v0.1.0
