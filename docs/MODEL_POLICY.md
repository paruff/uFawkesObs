# Model Selection Policy — uFawkesObs

> Grade-based model routing for uFawkesObs. This file is referenced from `AGENTS.md §3` and `.agents/agents/otel-collector.md`.
>
> **Design principle:** Task routing uses stable *grade definitions* (which rarely change). The *current model mapping* updates frequently as models improve. When a model updates or a new one appears, only the mapping table changes.

---

## Grade Definitions

Grades are defined by minimum benchmark requirements, not specific model names. Any model meeting the thresholds qualifies for that grade.

| Grade | Name | Min SWE-bench Verified | Min Context Window | When to Use |
|-------|------|------------------------|-------------------|-------------|
| **S** | Critical | ≥90% | ≥128k | High-stakes, complex reasoning: PromQL rules, OTEL pipeline changes, architectural decisions |
| **A** | Production | ≥70% | ≥64k | Standard development: Docker Compose edits, Alloy config, version upgrades |
| **B** | Routine | ≥50% | ≥32k | Simple tasks: YAML edits, markdown, documentation, runbooks |
| **C** | Lightweight | Any | Any | Trivial edits: label changes, typo fixes, whitespace |
| **F** | Fallback | Free tier only | Any | Emergency: when all other providers are unavailable |

### Benchmark References

| Benchmark | What It Tests | Source | Update Frequency |
|-----------|---------------|--------|------------------|
| [SWE-bench Verified](https://www.swebench.com/) | Real GitHub bugs (500 problems) | vals.ai leaderboard | Monthly |
| [SWE-bench Pro](https://www.swebench.com/) | Harder enterprise bugs (1,865 problems) | Scale AI | Quarterly |
| [HumanEval](https://github.com/openai/human-eval) | Code generation (164 problems) | OpenAI | Static |
| [LiveCodeBench](https://livecodebench.github.io/) | Dynamic coding ( contamination-resistant) | Academic | Monthly |

> **Why SWE-bench Verified?** It's the best predictor of real-world coding ability (source: [SOTA progression](https://www.codesota.com/browse/computer-code/code-generation/swe-bench)). Scores ≥90% indicate frontier reasoning; ≥70% indicates production-grade; ≥50% indicates competent for simple tasks.

---

## Current Model Mapping

> **⚠️ Update this table when models change.** The grade definitions above are stable; only this mapping updates.

| Grade | Primary Model | Provider | Fallbacks | Notes |
|-------|---------------|----------|-----------|-------|
| **S** | nvidia/qwen3-coder-480b-a35b-instruct | NVIDIA NIM (local proxy) | nvidia/nemotron-3-ultra-550b-a55b | Largest available model; use for critical paths |
| **A** | google/gemini-2.5-pro | Google | opencode-zen/deepseek-v4 | Strong reasoning, good for standard dev work |
| **B** | google/gemini-2.5-flash | Google | opencode-zen/deepseek-v4-flash-free | Fast, sufficient for simple tasks |
| **C** | opencode-zen/deepseek-v4-flash-free | OpenCode Zen | — | Trivial edits only |
| **F** | (same as C) | — | — | Emergency fallback |

### Fallback Chain

```
Grade S (NVIDIA NIM primary) → Grade S (NVIDIA NIM secondary) → Grade A (Gemini Pro) → Grade B (Gemini Flash) → Grade F (OpenCode Zen)
```

Triggers: `rate_limit`, `timeout`, `server_error`

---

## Task → Grade Routing

> **Stable — rarely changes.** This table defines which grade is required for each task type.

| Task Type | Grade | Reason |
|-----------|-------|--------|
| **PromQL recording rules** | S | Vector arithmetic, missing `or vector(0)` guards require strong reasoning |
| **PromQL alerting rules (DORA)** | S | Threshold logic and edge cases require frontier reasoning |
| **OTEL Collector AI/LLM pipeline (`gen_ai.*`)** | S | Breaking changes risk production; requires careful guard clauses |
| **Grafana dashboard JSON — DORA panels** | S | Complex panel math, datasource references, template variables |
| **Grafana dashboard JSON — AI/LLM panels** | S | Same as DORA — structured output quality matters |
| Docker Compose multi-service edit | A | Multi-file coordination, known patterns |
| Alloy River syntax (cAdvisor, node-exporter) | A | Domain-specific config, needs accuracy |
| OTEL Collector standard pipeline edit | A | Standard receiver/processor/exporter changes |
| Version upgrade (Prometheus / Loki / Tempo) | B | Single version string, but needs breaking change notes |
| Version upgrade (Grafana) | B | Sometimes requires dashboard JSON migration |
| Prometheus scrape config addition | B | Simple YAML block addition |
| Cross-plane documentation (Markdown) | B | Text generation |
| Observability runbooks | B | Must include exact LogQL queries, kubectl commands |
| Single YAML edit (version bump, label, port) | C | Trivial, any model works |
| Label changes | C | Trivial |
| Typo fixes | C | Trivial |

---

## Required Issue Body Format

Every issue assigned to the coding agent **must** include this block:

```
**Grade:** [S / A / B / C]
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

If rework rate for a task type exceeds **20% after 5 completed PRs** with the recommended grade:

1. **First** — improve the issue body: add file targets, reference configs, breaking change notes
2. **If still above 20%** — escalate to the next grade tier
3. **Document** the decision in this section with date and evidence

---

## Grade Update Process

When a model updates or a new model appears:

1. **Check benchmarks:** Verify the model meets grade thresholds at [swebench.com](https://www.swebench.com/) or [vals.ai](https://vals.ai/benchmarks/swebench)
2. **Update mapping:** Change only the "Current Model Mapping" table above
3. **Test:** Run 3 issues through the new model at the intended grade
4. **Validate:** Check PR revision count (target: ≤1 revision per PR)
5. **Document:** Add entry to escalation log below if grade changed

### Escalation Log

| Date | Task Type | Old Grade | New Grade | Reason | Evidence |
|------|-----------|-----------|-----------|--------|----------|
| 2026-09-13 | All | Copilot-specific | OpenCode grade-based | Initial migration from Copilot model ladder | — |

---

## Model Policy Enforcement

- `opencode.json` configures the fallback chain and default model
- Agent YAML files specify grades for operational agents (test, review, etc.)
- The NVIDIA NIM proxy (`nim-proxy` service in compose.yaml) must be running for Grade S models

---

## See Also

- `AGENTS.md` §3 — Context Files (references this file)
- `AGENTS.md` §4 — Architecture Rules (OTEL AI pipeline changes require Grade S)
- `.agents/agents/otel-collector.md` — OTel agent constraints
- `docs/ai-observability-guide.md` — AI pipeline architecture and instrumentation
