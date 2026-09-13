# Model Selection Policy — uFawkesObs

> Budget-aware model routing for uFawkesObs. This file is referenced from `AGENTS.md §3` and `.agents/agents/otel-collector.md`.

---

## Budget Context

uFawkesObs uses **OpenCode** with a multi-tier model fallback chain. Models are selected automatically based on availability and rate limits.

**Cost model:** NVIDIA NIM models are self-hosted (zero marginal cost). Gemini has a generous free quota. OpenCode Zen provides a free-tier fallback.

---

## Model Ladder

| Level | Model | Provider | Cost | Rule |
|-------|-------|----------|------|------|
| L0 — Primary | nvidia/qwen3-coder-480b-a35b-instruct | NVIDIA NIM (local proxy) | 0 | Default for all tasks when nim-proxy is running |
| L1 — Secondary | nvidia/nemotron-3-ultra-550b-a55b | NVIDIA NIM (local proxy) | 0 | Larger reasoning model; used when primary is rate-limited |
| L2 — Fallback | google/gemini-2.5-flash | Google | 0 (free quota) | Used when NVIDIA NIM is unavailable |
| L3 — Last resort | opencode-zen/deepseek-v4-flash-free | OpenCode Zen | 0 (free tier) | Used when all other providers are unavailable |
| AVOID | Claude Opus / Sonnet | Anthropic | Paid | Not in fallback chain; avoid for cost reasons |

---

## Fallback Chain

```
nvidia-primary → nvidia-secondary → gemini-fallback → opencode-zen-fallback
```

The fallback triggers on: `rate_limit`, `timeout`, `server_error`.

---

## Task → Model Routing Table

| Task type | Model | Notes |
|-----------|-------|-------|
| Single YAML edit (version bump, label, port) | Any | Simple edits work with any model |
| Docker Compose multi-service edit | nvidia-primary | Large context benefits from larger model |
| Alloy River syntax (cAdvisor, node-exporter) | nvidia-primary | Specify River config syntax explicitly |
| Prometheus scrape config addition | Any | Simple YAML block addition |
| OTEL Collector standard pipeline edit | nvidia-primary | Standard receiver/processor/exporter changes |
| **OTEL Collector AI/LLM pipeline (`gen_ai.*`)** | **nvidia-primary** | **Adding new AI exporters risks breaking existing pipelines** |
| Version upgrade (Prometheus / Loki / Tempo) | Any | Single version string; must include breaking change notes |
| Version upgrade (Grafana) | nvidia-primary | Grafana upgrades sometimes require dashboard JSON migration |
| **PromQL recording rules** | **nvidia-primary** | **Free models may produce `vector()` arithmetic errors** |
| **PromQL alerting rules (DORA)** | **nvidia-primary** | **Same — vector arithmetic and threshold logic** |
| **Grafana dashboard JSON — DORA panels** | **nvidia-primary** | **Structured output quality matters for dashboard JSON** |
| Cross-plane documentation (Markdown) | Any | Simple text generation |
| Observability runbooks | Any | Must include exact LogQL queries, kubectl commands, Grafana dashboard links |

---

## Required Issue Body Format

Every issue assigned to the coding agent **must** include this block:

```
**Suggested model:** [nvidia-primary / nvidia-secondary / gemini-fallback / opencode-zen-fallback]
**Task type:** [YAML edit / Docker Compose / PromQL / Grafana JSON / OTEL / docs]
**Files to edit:** [explicit list — agent must not create new files unless listed here]
**Reference file:** [path to existing config to use as pattern]
**Do not touch:** [files or services outside the scope of this issue]
**Breaking changes to check:** [version-specific migration notes if applicable]
**Acceptance criteria:**
- [ ] [measurable criterion 1]
- [ ] [measurable criterion 2]
```

---

## Escalation Rule

If rework rate for a task type exceeds **20% after 5 completed PRs** with the recommended model:

1. **First** — improve the issue body: add file targets, reference configs, breaking change notes
2. **If still above 20%** — escalate to the next model tier
3. **Document** the decision in this section with date and evidence

---

## Model Policy Enforcement

- `opencode.json` configures the fallback chain and default model
- Agent YAML files specify models for operational agents (test, review, etc.)
- The NVIDIA NIM proxy (`nim-proxy` service in compose.yaml) must be running for primary models

---

## See Also

- `AGENTS.md` §3 — Context Files (references this file)
- `AGENTS.md` §4 — Architecture Rules (OTEL AI pipeline changes require primary model)
- `.agents/agents/otel-collector.md` — OTel agent constraints
- `docs/ai-observability-guide.md` — AI pipeline architecture and instrumentation
