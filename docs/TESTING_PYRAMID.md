# Testing Pyramid — Testcontainers + InSpec

> Plan for improving test reliability and confidence beyond what static
> config parsing and a shared, polled `docker compose up` can catch. Not
> yet implemented — tracked as issues, linked below. See
> [`DETERMINISM.md`](DETERMINISM.md) for the related build/CI-reproducibility
> work this complements (that doc is about *the same environment every
> time*; this one is about *catching more with each run*).

## Where This Comes From

Two real gaps found during this repo's own determinism work:

1. The integration tier (`tests/integration/`) runs against one long-lived,
   shared `docker compose up` stack per CI run, woken with fixed `sleep N`
   waits. Tests share mutable state with each other by construction — a
   test that leaves something behind can leak into the next one, and nothing
   isolates a flaky container restart to the test that triggered it.
2. `tests/unit/test_compose_versions.py` checks the *declared* `compose.yaml`
   — image pins, port bindings — but never the *actual running* container.
   A pull that silently fell back to a cached older image, or a healthcheck
   that's declared but doesn't actually pass, isn't caught by parsing YAML.

## The Pyramid

```
        ▲  Chaos (nightly, existing)          — kill/restart real containers
        │  Acceptance (pytest-bdd, existing)  — cross-service scenarios
        │  Contract (NEW — InSpec)            — is the RUNNING stack conformant?
        │  Integration (Testcontainers)       — per-test hermetic service pairs
        ▼  Unit (existing)                    — static parsing, no containers
```

### Unit — unchanged

Already fast, deterministic, no containers. Nothing to change here.

### Integration — migrate to Testcontainers

**Problem it solves:** the shared-stack-plus-`sleep` pattern is exactly the
non-determinism class already fixed once this session (`ci-tests.yml`'s
`apps-test` job, #334's Prometheus-reload case). Testcontainers' `DockerCompose`
wrapper (Python: `testcontainers-python`) gives each test its own container
lifecycle — provisioned fresh, torn down guaranteed via context manager, with
built-in `wait_for_logs`/`wait_for_http` instead of hand-written poll loops.

**What changes:** `tests/integration/` tests currently assume `make up` has
already been run; they'd instead each request the specific service(s) they
need via Testcontainers, scoped to the test's own lifetime. Slower per-test
(no shared warm stack) but each test's failure is now isolated to its own
container — a flaky Prometheus restart in one test can't leave the next
test's Grafana query looking flaky too.

**Scope decision needed:** whole `tests/integration/` at once, or migrate
one service pair first (Prometheus↔OTel Collector is the simplest, no
cross-service state) and use it as the template before doing the rest.

### Contract (new tier) — InSpec

**Problem it solves:** `AGENTS.md` §4 states hard architecture rules —
every service has a `healthcheck:`, no anonymous volumes, no `latest` tags,
explicit networks, specific ports must be localhost-only. Today these are
enforced by a mix of static YAML parsing (`test_compose_versions.py`) and
manual review. Nothing checks them against the *actually running* stack.

**What it adds:** an InSpec profile that runs against a live `make up`
stack and asserts, per service: healthcheck reports healthy (not just
declared), the container's actual bound ports match `docs/ARCHITECTURE.md`'s
public/localhost table, the image running matches the pinned digest (not a
stale cached layer), volumes are named. This directly encodes AGENTS.md §4
as automated, declarative checks instead of relying on review to catch a
violation.

**Why InSpec specifically, not another shell script:** declarative
resource/matcher syntax (`describe docker_container('grafana') do its(:ports)
{ should include ... } end`) gives a specific pass/fail diff per assertion,
the same "fails on the actual signal" property that made the digest-aware
test fix (this session, PRs #401/#410) more useful than a bare boolean.

### Acceptance and Chaos — unchanged for now

Both already exercise cross-service, real-stack behavior in ways
Testcontainers' per-test isolation model doesn't fit well (a BDD scenario
or a chaos experiment inherently wants one running "world"). Revisit only
if the shared-stack pattern here starts showing the same symptoms integration
testing did.

## Rollout Order

1. Spike: one Testcontainers-based test replacing one existing
   `tests/integration/` file, to validate the approach fits this repo's
   actual service set before committing to a full migration.
2. InSpec profile covering AGENTS.md §4's rules, run manually first (not yet
   gating CI) to see what it actually catches against the current stack.
3. Wire the InSpec profile into CI as a new required check, once the
   manual run shows it's not noisy.
4. Migrate `tests/integration/` to Testcontainers, service by service.
5. Re-audit `docs/DETERMINISM.md` and this doc together once both land —
   Testcontainers' per-test isolation may make some of the "Should"-tier
   `sleep`-audit findings moot rather than needing individual fixes.

## Findings — InSpec Manual Run (2026-09-23)

Per #414's own instruction, ran `make test-conformance` manually against a
live `make up` (`core` profile) stack before wiring anything into CI:

- **30 controls passed, 0 failures** across all 8 `core`-profile services
  (otel-collector, tempo, loki, alloy, prometheus, alertmanager, grafana,
  node-exporter) — every declared healthcheck reports `healthy`, every
  running container's image matches its pinned `@sha256` digest exactly,
  every declared port mapping is actually bound as declared, and no
  anonymous volumes exist on any container.
- **8 controls skipped**, not failed — `telemetry-generator` (`apps`
  profile), `dora-api` (`dora` profile), and `alertmanager-discord`
  (`notifications` profile) weren't running at check time, so their
  controls' `only_if` guard skipped rather than reporting a false failure.
- **Net finding: nothing found.** The `core` stack's actually-running
  containers are fully conformant with AGENTS.md §4 as declared in
  `compose.yaml` right now — no drift between declared and live state. That
  itself is the useful signal: the profile is confirmed non-noisy against a
  known-good stack, which is the precondition #415 sets for gating CI on it.

## Tracking

- [x] [#413](https://github.com/paruff/uFawkesObs/issues/413) — Testcontainers spike: migrate one integration test file (on `main`)
- [x] [#414](https://github.com/paruff/uFawkesObs/issues/414) — InSpec profile for AGENTS.md §4 conformance (on `main`)
- [ ] [#415](https://github.com/paruff/uFawkesObs/issues/415) — Wire InSpec profile into CI (depends on #414). CI job on `main`, reporting on every PR. Still needed: adding it to branch protection's required checks (maintainer action, AGENTS.md §5) once its false-positive rate is confirmed low across real runs.
- [ ] [#416](https://github.com/paruff/uFawkesObs/issues/416) — Migrate remaining `tests/integration/` to Testcontainers (depends on #413). File-by-file status (each a separate PR, kept under the 400-line gate):
  - [x] `test_otel_collector_testcontainers.py` — spike, #413 (new file, alongside the original) (on `main`)
  - [x] `test_tempo_integration.py` — single-service, no `depends_on:` (PR open)
  - [x] `test_loki_integration.py` — single-service, no `depends_on:` for Loki itself. `TestAlloyIntegration` in this same file left unmigrated -- Alloy depends on both Loki and Prometheus, so it belongs with the `test_alloy_and_dashboards.py` entry below instead (PR open)
  - [ ] `test_grafana_integration.py` — depends on Prometheus being scraped
  - [ ] `test_dashboards.py` / `test_alloy_and_dashboards.py` — cross-service (Grafana+Prometheus+Tempo+Loki+Alloy all need to actually flow data) — hardest, do last
  - [ ] rest of `test_otel_collector.py` / `test_prometheus_scraping.py` — retire the originals once their Testcontainers replacements cover the same assertions
  - [ ] simplify `ci-tests.yml`'s Integration Tests job (drop the shared `docker compose up` / fixed-sleep waits) once nothing left in the job needs them
- [ ] [#417](https://github.com/paruff/uFawkesObs/issues/417) — Update `tests/README.md`'s pyramid diagram (depends on all above). `tests/README.md` now has a 5-tier overview and `docs/DETERMINISM.md` has a re-audit note; both marked partial/in-progress since #416's file-by-file migration isn't finished yet. Revisit once that checklist is fully checked off.
