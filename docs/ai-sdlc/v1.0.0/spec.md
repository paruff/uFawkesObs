# Spec: uFawkesObs v1.0.0

**Traces to:** [`intent.md`](intent.md) | **Plan:** [`plan.md`](plan.md)
**Status:** Draft | **Revision:** 1

## Requirements

| ID | Requirement | Tracked in |
|---|---|---|
| REL-01 | The public contract below is published with the release, and the release notes link to it | This file |
| REL-02 | `make init && make up` on a clean Linux host and a clean macOS host reaches a healthy stack within 15 minutes, with metrics, logs, and traces visible in Grafana, following only the README | #494 (RG-1) |
| REL-03 | The README states that DORA uses SQLite by default | #495 (RG-2) |
| REL-04 | Someone new to the repo completes the README Quick Start without help | #496 (RG-3) |
| REL-05 | The GitHub Release carries the changelog excerpt, a source tarball, and its SHA256 | #497 (RG-4) |
| REL-06 | Upgrade notes from 0.4.x cover every contract-affecting change | #498 |
| REL-07 | The `v1.0.0` milestone has no open issue labeled `release-blocker` | [milestone](https://github.com/paruff/uFawkesObs/milestone/1) |
| REL-08 | The GitHub Release, the ufawkes.dev Obs page, the dev.to post, and the LinkedIn post all show the same version and link to the same release notes | Suite AC-OBS-04 |

The existing functional and non-functional requirements (OBS-F##, OBS-N##)
in [`docs/product/spec.md`](../../product/spec.md) still apply. 1.0 adds no
new product features.

## Design

1.0 changes no architecture. Topology, principles, and decisions stay as
described in [`docs/product/design.md`](../../product/design.md),
[`docs/ARCHITECTURE.md`](../../ARCHITECTURE.md), and
[`docs/adr/`](../../adr/). What 1.0 adds is the contract below and the
semver rules that apply to it.

### Public contract

This table was re-verified against `origin/main` at `155ef5a`
(`docker compose --env-file .env.example --profile '*' config`): all 11
services, their profiles, every published port and all 7 `.env.example`
variables match. The tagged `compose.yaml` and `.env.example` remain
authoritative.

**Compose services and published ports**

| Service | Profile | Published (host bind → container) |
|---|---|---|
| `grafana` | core | `*:3000→3000` |
| `otel-collector` | core | `*:4317→4317` (OTLP gRPC), `*:4318→4318` (OTLP HTTP), `127.0.0.1:8888`, `127.0.0.1:8889` |
| `prometheus` | core | `127.0.0.1:9090` |
| `loki` | core | `127.0.0.1:3100`, `127.0.0.1:9096` |
| `tempo` | core | `127.0.0.1:3200`, `9095`, `14250`, `14268`, `9411` (all `127.0.0.1`) |
| `alertmanager` | core | `127.0.0.1:9093` |
| `alloy` | core | `127.0.0.1:12345` |
| `node-exporter` | core | `127.0.0.1:9100` |
| `dora-api` | dora | `127.0.0.1:8088` |
| `alertmanager-discord` | notifications | none |
| `telemetry-generator` | apps | `*:5001→5000` |

**`.env.example` variables:** `GRAFANA_ADMIN_USER`,
`GRAFANA_ADMIN_PASSWORD`, `DORA_COMPUTE_WINDOW_DAYS`,
`DORA_COMPUTE_INTERVAL_SECONDS`, `DORA_API_KEY`, `SLACK_WEBHOOK_URL`,
`DISCORD_WEBHOOK_URL`

### Semver rules

| Change | Version bump |
|---|---|
| Rename or remove a service; change a published host port; move a port from `127.0.0.1` to all interfaces or back; rename or remove an `.env.example` variable or change its meaning | **Major** |
| Add a service, a published port, or an optional `.env.example` variable. Adding services, ports, or variables still needs PM sign-off (AGENTS.md §5). | Minor |
| Change a datasource UID, a dashboard UID, or a DORA metric name (not covered, but it must be called out in the release notes) | Minor |
| Image bumps and config fixes that keep the contract intact | Patch |

Makefile targets and compose profile names are **not** in the contract
yet; see intent open question 2.

## Concerns

| Risk | Handling |
|---|---|
| #381: the GitOps deploy path is broken | It's already a release-blocker. Either fix it, or state in the release notes that GitOps deploy is outside the 1.0 contract. |
| Users build on uncovered surfaces (UIDs, metric names) and a minor release breaks them | The release notes list every change to an uncovered surface, and the contract says plainly what isn't covered |
| The contract table drifts from the tagged files | The table is a review aid; the tagged files are authoritative; re-verify at the rc (plan step 4) |
| The riskiest assumption (operational burden) is untested | Out of scope for 1.0; the adoption measure is the first signal (intent) |

## Acceptance Criteria

- **AC-01:** REL-02 and REL-04 pass on the rc, with real run transcripts
  linked in the release notes.
- **AC-02:** REL-07 holds. The milestone shows zero open `release-blocker`
  issues.
- **AC-03:** REL-01, REL-03, REL-05, and REL-06 are met, each verified by
  its tracking issue's stated check.
- **AC-04:** REL-08 holds. Four live URLs show the same version.
