# uFawkesObs's Contract Surface

> **Scope:** This document describes what uFawkesObs currently expects to
> *receive* from other planes and instrumented services, based on its actual
> implementation as of this writing. It is not a bilateral spec other planes
> are bound by, and it is not the suite's shared source of truth — see
> "Where this goes next" at the end.

uFawkesObs is the consumer side of two contracts:

1. **DORA events** — deployment, PR, incident, and rework events POSTed to
   the ingestion API (`dora/ingestion/`), which now lives in this repo (the
   standalone uFawkesDORA repo was consolidated in — see `AGENTS.md` §10).
2. **OTLP telemetry** — traces, metrics, and logs sent by instrumented
   services to the OpenTelemetry Collector (`config/otel/collector.yaml`).

---

## 1. DORA Event Ingestion

### Endpoints

Implemented in `dora/ingestion/api/main.py`. The service listens on
`127.0.0.1:8088` by default (`compose.yaml`, `dora-api` service, `dora`
profile).

| Method | Path           | Purpose                                              |
| ------ | -------------- | ----------------------------------------------------- |
| `POST` | `/event`       | Accept one event, validate, enqueue. `201` on success. |
| `POST` | `/event/batch` | Accept multiple events in one transaction — all-or-nothing: if any event fails validation, none are enqueued. `201` on success. |
| `GET`  | `/health`      | `{"status": "ok", "queue_depth": N}`. Open.           |
| `GET`  | `/metrics`     | Prometheus text of the computed DORA metrics. Open, like every other `/metrics` in the stack. |

Validation failures return `422` with field-level detail
(`dora/ingestion/api/validator.py`):

```json
{
  "detail": [
    {"loc": ["body", "environment"], "msg": "'environment' is a required property", "type": "value_error"}
  ]
}
```

**Authentication:** when `DORA_API_KEY` is set, `POST /event` and
`POST /event/batch` require `Authorization: Bearer $DORA_API_KEY` and return
`401` without it (`dora/ingestion/api/auth.py`, constant-time compare). When
the key is unset (the local default) ingestion is open. `GET /metrics` and
`GET /health` are never authenticated.

### Event types and required fields

Each event is a flat JSON object validated against a Draft-07 schema in
`dora/events/`. `event_type` is the routing discriminant
(`dora/ingestion/api/validator.py:EVENT_TYPE_SCHEMA_MAP`), and every schema
sets `"additionalProperties": false` — extra fields are rejected, not
ignored.

#### `deployment` — `dora/events/deployment-event.schema.json`

Drives Deployment Frequency, Lead Time, Change Failure Rate, and FDRT.
Lead Time has no other input: a deployment without `first_commit_at` or
`pr_merged_at` produces no Lead Time sample. `deployed_at` is when the deploy
finished, and compute windows and orders on it, not on ingest time.

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | Pattern `^\d+\.\d+$`, e.g. `"1.0"` |
| `event_type` | const `"deployment"` | yes | |
| `repo` | string | yes | e.g. `"org/repo-name"` |
| `service` | string | yes | Component name within the repo |
| `environment` | string | yes | e.g. `"production"`, `"staging"` |
| `commit_sha` | string | yes | Full 40-char SHA (`^[0-9a-f]{40}$`) |
| `deployed_at` | string (date-time) | yes | ISO 8601 |
| `status` | enum | yes | `success` \| `failed` \| `rollback` |
| `pipeline_url` | string (uri) | yes | Link to the CI run |
| `deploy_duration_seconds` | integer ≥ 0 | no | |
| `ai_assisted` | boolean | no | |
| `first_commit_at` | string (date-time) | no | First commit of the change set. The exact start of Lead Time; preferred over `pr_merged_at` |
| `pr_merged_at` | string (date-time) | no | PR merge time. Lead Time start when `first_commit_at` is absent, and then the metric is flagged as a proxy |
| `deployment_intent` | enum | no | `planned` \| `unplanned_rework`. Accepted and stored; no metric reads it yet. Added in schema `1.1` |

#### `pr` — `dora/events/pr-event.schema.json`

Accepted and stored. No metric reads it today (see `docs/ai-sdlc/dora-contract/spec.md`, D3).

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | |
| `event_type` | const `"pr"` | yes | |
| `repo` | string | yes | |
| `pr_number` | integer ≥ 1 | yes | |
| `commit_sha` | string | yes | 40-char SHA |
| `status` | enum | yes | `opened` \| `merged` \| `closed` |
| `occurred_at` | string (date-time) | yes | |
| `first_commit_at` | string (date-time) | yes | |
| `lines_added` / `lines_deleted` | integer ≥ 0 | no | |
| `ai_assisted` | boolean | no | |

#### `incident` — `dora/events/incident-event.schema.json`

Accepted and stored. No metric reads it today: recovery time is the gap between a failed deployment and the next success (D3).

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | |
| `event_type` | const `"incident"` | yes | |
| `incident_id` | string | yes | e.g. a PagerDuty ID |
| `repo` | string | yes | |
| `service` | string | yes | |
| `status` | enum | yes | `opened` \| `resolved` |
| `occurred_at` | string (date-time) | yes | |
| `linked_deployment_sha` | string | no | 40-char SHA, if known |
| `severity` | string | no | e.g. `"SEV1"` |

#### `rework` — `dora/events/rework-event.schema.json`

Drives Rework Rate — deployments that are remediation, not forward
progress.

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | |
| `event_type` | const `"rework"` | yes | |
| `repo` | string | yes | |
| `deployment_sha` | string | yes | 40-char SHA |
| `rework_type` | enum | yes | `hotfix` \| `rollback` \| `patch` |
| `triggered_at` | string (date-time) | yes | |
| `user_visible` | boolean | yes | Distinguishes user-visible rework from internal/corrective changes |

### Working examples

`dora/collectors/` has concrete, tested payload examples per platform —
these are the actual contract in executable form, more reliable than any
prose summary:

- `dora/collectors/github/dora-deployment-event.yml` — reusable GitHub
  Actions workflow (`workflow_call`) that builds and POSTs a `deployment`
  event from `github.sha`, the time the deploy finished, and the lead-time
  inputs. It sends the bearer token when `DORA_API_KEY` is set and fails the
  step on a 4xx.
- `dora/collectors/github/dora-pr-event.yml` — same, for `pr` events.
- `dora/collectors/generic/curl-examples.sh` — raw `curl` examples for all
  four event types, plus a field-mapping table for GitLab CI, CircleCI,
  Jenkins, and Woodpecker CI variable names.
- `dora/collectors/woodpecker/pipeline-snippet.yml` — Woodpecker-specific
  pipeline step.
- `dora/collectors/manual-incident/declare-incident.sh` /
  `resolve-incident.sh` — scripts for manually emitting `incident` events
  (opened/resolved) outside of CI, e.g. from an on-call tool.

### Queueing (implementation detail, not part of the wire contract)

`dora/ingestion/api/queue.py` is a thin facade over `queue_sqlite.py` —
SQLite is the only backend. `POST /event` enqueues synchronously and
returns immediately — `dora/compute/` processes the queue asynchronously
to compute the five DORA metrics.

---

## 2. OTLP Telemetry Conventions

### Receivers

One Collector instance runs, accepting standard OTLP on these ports
(`config/otel/collector.yaml`, `core` profile):

| Protocol | Endpoint |
|---|---|
| OTLP gRPC | `0.0.0.0:4317` |
| OTLP HTTP | `0.0.0.0:4318` |

Send traces, metrics, and logs to this collector — there is no
schema-level difference between receivers, only downstream routing
differs (see below).

### No enforced resource-attribute schema

Neither collector config declares a `resourcedetection` or `schema`
processor that rejects telemetry missing specific resource attributes
(e.g. `service.name`). Any well-formed OTLP payload is accepted; Grafana
dashboards and Prometheus labels will simply be sparser if conventional
attributes like `service.name` are omitted. There is no required minimum
attribute set enforced by Obs today — this is a gap if strict conventions
are wanted later, not a currently-implemented requirement.

### Metric routing conventions (`config/otel/collector.yaml`)

The main collector has two metrics pipelines:

- `metrics` — the default pipeline; every metric received goes to
  Prometheus (`app_metrics` namespace) and `debug` (stdout logging).
- `metrics/ai` — a **name-based filter**, not an attribute-based one: any
  metric whose name matches `gen_ai\..*`, `llm\..*`, `openllmetry\..*`, or
  `ai\..*` (case-sensitive regex, `filter/ai` processor) additionally gets
  routed through `attributes/ai`, which inserts two fixed labels
  (`ai.environment=development`, `ai.platform=fawkes-idp`) before export.
  **Convention for AI-observability metrics: prefix the metric name with
  one of those four namespaces** if you want it captured by this pipeline.

Traces always export to Tempo (`otlp/tempo`, insecure gRPC on `tempo:4317`)
and logs always export to Loki (`loki`, HTTP push to
`loki:3100/loki/api/v1/push`) — no filtering on either.

### `otel-collector-dora` — removed

The container was removed (issue #266): nothing emitted the `dora.*` / `cicd.*`
signals it filtered on, and Prometheus never scraped it. Its inert config
(`config/otel/collector-dora.yaml`) was deleted in #750. DORA ingestion is
REST-only via `dora-api` (`POST /event`); see ADR-006 to rebuild an OTLP path.

## Where this goes next

The plan (not yet implemented) is for **uFawkesPipe** to host the
suite-wide, machine-readable version of these contracts — the JSON
Schemas as source of truth, likely alongside its own CI/CD event emission
code — with **ufawkes.dev** rendering the human-readable page from that
shared source. This document is Obs's own snapshot of what it currently
implements as the consumer, not that shared location; if Pipe's future
schemas diverge from `dora/events/*.schema.json`, this doc (and the
schemas here) are what Obs actually enforces until reconciled.
