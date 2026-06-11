# Agent Instructions — uFawkesObs (Obstackd)

> **TOKEN COST:** Every line here is billed on every interaction. Keep it lean.
> Skills live in `.agents/skills/` — load on demand only.
> **DORA basis:** Cap 6 (Fast Feedback Loops) + Cap 2 (Healthy Data Ecosystems)

---

## 1. AI Policy

- AI agents implement. Humans decide.
- No AI-generated config merges without human review and approval.
- **Data policy:** No production credentials, kubeconfig, or real service endpoints in AI prompts. Config examples use placeholder values only.

---

## 2. Project Identity

**Product:** uFawkesObs (Obstackd) — self-hosted GitOps-first observability plane for the Fawkes IDP family. Delivers OpenTelemetry, Prometheus, Alertmanager, Tempo, Loki, Alloy, and Grafana via Docker Compose.
**Stack:** Docker Compose · OTel Collector v0.103.1 · Prometheus v2.52.0 · Alertmanager v0.27.0 · Tempo v2.5.0 · Loki v2.9.10 · Alloy v1.12.2 · Grafana v10.4.5 · Python (telemetry-generator) · YAML · Shell
**Key constraints:** Must run on Docker Compose locally. No Kubernetes required for standalone use. Config files in `config/` are the GitOps source of truth — no manual edits to running containers.

---

## 3. Architecture

```
config/           → GitOps source of truth for all service config (do not hand-edit running containers)
dashboards/       → Grafana dashboard JSON provisioned automatically on startup
apps/telemetry-generator/ → Python test signal emitter
scripts/          → Shell automation (start, stop, reset, health-check)
tests/            → Smoke tests validating stack health
docs/             → Architecture decisions and runbooks
```

**Hard rules:**

- All config changes go in `config/` and are applied via `docker compose up -d --force-recreate`.
- No credentials in `config/` — use `.env` (gitignored) with `.env.example` as the template.
- Dashboards in `dashboards/` must be JSON — no manual Grafana UI edits that aren't exported back.
- Alloy replaces Promtail — do not add Promtail config.

---

## 4. Five Hard Rules

1. No credentials or real endpoints in any committed file.
2. No manual `docker exec` changes — all config via `config/` and Compose.
3. No merging your own PR.
4. No modifying `AGENTS.md` without maintainer approval.
5. No adding new Compose services without an ADR in `docs/`.

---

## 5. Token Budget

Before any task touching > 3 files:

1. State scope in one sentence.
2. List files you plan to read.
3. Confirm: "Proceed? (moderate/high token cost)"

---

## 6. Agents — `.agents/agents/`

`@obs-stack` config and troubleshooting · `@dashboard` Grafana dashboard authoring · `@alerting` Prometheus alert rules · `@dora` DORA metric interpretation · `@docs` ADRs and runbooks · `@test` smoke test authoring · `@review` PR review · `@security` secrets and config audit

Max **3 concurrent agent tasks**. Each on its own branch. No agent merges its own PR.

---

## 7. Skills — `.agents/skills/` (load on demand)

`obs-stack/` stack config and troubleshooting · `dashboard-authoring/` Grafana JSON patterns · `alerting/` PromQL alert rules · `dora-metrics/` DORA metric queries · `security-review/` pre-merge checklist · `lang-python/` telemetry-generator work · `lang-shell/` scripts/ work · `adr-writer/` architecture decisions

---

## 8. Context Files (read before generating config or code)

Read in this order: `docs/architecture.md` (stack design) → `.env.example` (all env vars) → `config/otel-collector-config.yaml` (routing rules) → `docs/KNOWN_LIMITATIONS.md` (do not make these worse).
