# AI-SDLC index

One folder per feature under `docs/ai-sdlc/<feature>/`. Find the feature below,
then open its intent, spec or plan.

## The chain

`intent.md` (why) → `spec.md` (what, with acceptance criteria) → `plan.md`
(how it is verified; links issues, lists no tasks).

- A PR that changes `apps/`, `config/`, `dashboards/`, `dora/`, `evals/`,
  `inspec/` or `scripts/` must include a `plan.md` with a `## Verification
  Strategy`. Every `spec.md` needs an `intent.md` in the branch history.
  CI enforces both (`scripts/check-artifact-chain.sh`).
- Many older features have only a plan. That is allowed.
- **Status lives on [Project #7](https://github.com/users/paruff/projects/7),
  not in these files.** The `Status:` line in a file is informational.
- Repo-wide intent: [`INTENT.md`](../../INTENT.md). Rules: [`AGENTS.md`](../../AGENTS.md).

## Features

### Suite and releases

| Feature | About | Intent | Spec | Plan |
|---|---|---|---|---|
| `v1.0.0` | The v1.0.0 contract and release gates | [intent](v1.0.0/intent.md) | [spec](v1.0.0/spec.md) | [plan](v1.0.0/plan.md) |
| `dora-contract` | The five DORA metrics measurable from real pipelines (#719). **D1 to D3 are in its spec** | [intent](dora-contract/intent.md) | [spec](dora-contract/spec.md) | [plan](dora-contract/plan.md) |

### DORA pipeline

| Feature | About | Intent | Spec | Plan |
|---|---|---|---|---|
| `dora-backfill` | Runner-free backfill from GitHub PR history | - | - | [plan](dora-backfill/plan.md) |
| `cfr-rollback` | Change-failure-rate triggered rollback | - | - | [plan](cfr-rollback/plan.md) |
| `dora-current-state` | Current-state DORA docs describe the running stack | - | - | [plan](dora-current-state/plan.md) |
| `delete-emit-dora-event` | Delete the unused `emit-dora-event.sh` (#734) | - | - | [plan](delete-emit-dora-event/plan.md) |
| `rework-rate-comment` | Correct the rework-rate comments in the rules file | - | - | [plan](rework-rate-comment/plan.md) |
| `timestamp-offset` | Require a UTC offset on event timestamps | - | - | [plan](timestamp-offset/plan.md) |

### Alerts and SLOs

| Feature | About | Intent | Spec | Plan |
|---|---|---|---|---|
| `healthy-default-alerts` | A healthy default install fires no alerts | - | - | [plan](healthy-default-alerts/plan.md) |
| `slo-burn-rate` | SLO burn-rate alerts | - | - | [plan](slo-burn-rate/plan.md) |
| `replace-alertmanager-discord` | Native `discord_configs` instead of the bridge | - | - | [plan](replace-alertmanager-discord/plan.md) |
| `sigma-breach-intent` | A sigma-band breach opens an intent issue (Stage 6) | [intent](sigma-breach-intent/intent.md) | - | [plan](sigma-breach-intent/plan.md) |

### Telemetry and dashboards

| Feature | About | Intent | Spec | Plan |
|---|---|---|---|---|
| `host-metrics-dashboard` | Host-metrics dashboard for OTLP agents | - | - | [plan](host-metrics-dashboard/plan.md) |
| `otel-collector-0.162` | Bump otel-collector-contrib to 0.162.0 | - | - | [plan](otel-collector-0.162/plan.md) |
| `ci-host-metrics-exclusion` | Unbreak Acceptance Full on main | - | - | [plan](ci-host-metrics-exclusion/plan.md) |

### Process and tooling

| Feature | About | Intent | Spec | Plan |
|---|---|---|---|---|
| `artifact-chain` | Enforce the artifact chain in CI | [intent](artifact-chain/intent.md) | - | [plan](artifact-chain/plan.md) |
| `shift-left-adoption` | Adopt uFawkesPipe's shared shift-left hooks | - | - | [plan](shift-left-adoption/plan.md) |
| `ruff-0.17` | Adopt ruff v0.17 | - | - | [plan](ruff-0.17/plan.md) |
| `configurable-host-ports` | Configurable host ports for Grafana and the telemetry generator, and the InSpec ports control that reads them | - | - | [plan](configurable-host-ports/plan.md) |
| `audit-medium-low` | Medium and low audit findings (AF-02 06 09 10 14) | - | - | [plan](audit-medium-low/plan.md) |

## Decisions

| Where | What |
|---|---|
| [`dora-contract/spec.md`](dora-contract/spec.md#design), under **Decisions** | D1 `deployment_intent`, D2 `_pct` metric names, D3 `pr` and `incident` events. Confirmed by the owner on 2026-11-18. Follow-ups: #728, #729, #730 |

## Adding a feature

Make `docs/ai-sdlc/<feature>/`, add the files, and add a row above. A unit test
(`tests/unit/test_ai_sdlc_index.py`) fails when a folder is missing from this
table or a link is broken.
