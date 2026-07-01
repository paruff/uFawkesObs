# Model Selection Policy — uFawkesObs

> Budget-aware model routing for uFawkesObs. This file is referenced from `AGENTS.md §3` and `.agents/agents/otel-collector.md`.

---

## Budget Context

uFawkesObs operates within the **shared uFawkesAI Copilot Pro budget**: **300 premium requests/month across all repos**.

> **Cost model:** The coding agent uses exactly 1 premium request per session × the model multiplier. GPT-4.1 has 0× multiplier — completely free and is the default for all tasks.

---

## Model Ladder

| Level | Model | Multiplier | Rule |
|-------|-------|------------|------|
| L0 — Free default | GPT-4.1 | 0× | Use for ALL tasks unless explicitly listed otherwise |
| L0 — Free lightweight | GPT-5 mini | 0× | Single-file YAML edits: version bumps, label changes, one-line additions |
| L1 — Trial (Grafana only) | Gemini 3 Flash | 0.33× | Trial ONLY for Grafana dashboard JSON — see trial note below |
| L2 — Justified premium | GPT-5.1-Codex | 1× | PromQL rules, Grafana JSON if Gemini trial fails; requires `model:gpt-5.1-codex` label |
| PROHIBITED | Claude Opus 4.6 fast | 30× | Never — 30× multiplier. Blocked without explicit written budget approval |
| AVOID | Claude Opus / Sonnet | 1–3× | No uFawkesObs task type justifies these models |

---

## Task → Model Routing Table

| Task type | Model | Cost | Notes |
|-----------|-------|------|-------|
| Single YAML edit (version bump, label, port) | GPT-5 mini | 0 | |
| Docker Compose multi-service edit | GPT-4.1 | 0 | |
| Alloy River syntax (cAdvisor, node-exporter) | GPT-4.1 | 0 | Specify River config syntax explicitly — not Prometheus config syntax |
| Prometheus scrape config addition | GPT-5 mini | 0 | Simple YAML block addition; provide existing scrape config as reference |
| DevLake Docker Compose integration | GPT-4.1 | 0 | Large block but known pattern; provide DevLake docs link in issue |
| OTEL Collector standard pipeline edit | GPT-4.1 | 0 | Standard receiver/processor/exporter changes only |
| **OTEL Collector AI/LLM pipeline (`gen_ai.*`)** | **GPT-5.1-Codex** | **1** | **Adding new AI exporters risks breaking existing pipelines; free models miss guard clauses** |
| Version upgrade (Prometheus / Loki / Tempo) | GPT-5 mini | 0 | Single version string in compose.yaml; must include breaking change notes in issue body |
| Version upgrade (Grafana) | GPT-4.1 | 0 | Grafana upgrades sometimes require dashboard JSON migration; GPT-4.1 handles this |
| **PromQL recording rules** | **GPT-5.1-Codex** | **1** | **Free models produce `vector()` arithmetic errors and missing `or vector(0)` guards** |
| **PromQL alerting rules (DORA)** | **GPT-5.1-Codex** | **1** | **Same — vector arithmetic and threshold logic requires Codex** |
| **Grafana dashboard JSON — DORA panels** | **Gemini 3 Flash** | **0.33** | **Trial: measure PR revision count over first 3 uses before committing** |
| **Grafana dashboard JSON — AI/LLM panels** | **GPT-5.1-Codex** | **1** | **AI dashboard JSON is more complex than DORA; start with Codex not Gemini** |
| Cross-plane documentation (Markdown) | GPT-5 mini | 0 | |
| Observability runbooks | GPT-5 mini | 0 | Must include exact LogQL queries, kubectl commands, Grafana dashboard links in issue body |
| Interactive IDE chat (VS Code) | Claude Haiku 4.5 | 0.33 | Chat only — do not assign agent tasks to Haiku |
| Manual PR comment invocation | GPT-4.1 | 0 | Use `@copilot` with no `+model` suffix — omitting the selector defaults to GPT-4.1 free |

---

## Gemini 3 Flash Trial Note (Grafana Dashboard JSON)

Gemini 3 Flash scores 63.8% on SWE-bench vs GPT-5.1-Codex at a higher level, but costs **0.33× vs 1×**. For Grafana dashboard JSON specifically, the structured output quality may be sufficient at lower cost.

**Trial protocol:**

1. Assign the first 3 Grafana JSON issues to Gemini 3 Flash
2. Record PR revision count for each (target: ≤1 revision per PR)
3. If revision count ≤1 across all 3: adopt Gemini 3 Flash for DORA dashboards
4. If revision count >1 on any PR: switch to GPT-5.1-Codex and update this table

**Until the trial is complete, GPT-5.1-Codex remains the safe default for all Grafana JSON.**

---

## Required Issue Body Format

Every issue assigned to the Copilot coding agent **must** include this block:

```
**Suggested model:** [GPT-4.1 / GPT-5 mini / Gemini 3 Flash / GPT-5.1-Codex]
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

## Budget Guardrails

- **Never** use `@copilot +modelname` in PR comments unless GPT-4.1 has already failed on the same task
- Expected premium spend for uFawkesObs: **~8 requests/month** at 20 issues/week:
  - PromQL rules: ~4 sessions at 1× = 4 requests
  - Grafana AI dashboard JSON: ~2 sessions at 1× = 2 requests
  - Grafana DORA JSON (Gemini trial): ~3 sessions at 0.33× = ~1 request
  - IDE chat: ~220 messages/month at 0.33× = ~73 requests (shared with other repos)
- If Gemini 3 Flash trial succeeds, uFawkesObs premium agent spend drops to **~3 requests/month**

---

## Model Policy Enforcement

- `.github/copilot-instructions.md` enforces default model as GPT-4.1
- Agent YAML files specify `model: claude-sonnet-4-6` for operational agents (test, review, etc.) — these are separate from the Copilot coding agent budget
- Premium model usage requires the `model:gpt-5.1-codex` label on the issue/PR

---

## See Also

- `AGENTS.md` §3 — Context Files (references this file)
- `AGENTS.md` §4 — Architecture Rules (OTEL AI pipeline changes require GPT-5.1-Codex)
- `.agents/agents/otel-collector.md` — OTel agent constraints
- `docs/ai-observability-guide.md` — AI pipeline architecture and instrumentation
