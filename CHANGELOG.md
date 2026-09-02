# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
