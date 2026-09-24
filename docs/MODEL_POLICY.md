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
| **S** | (configure per environment) | — | — | Use for critical paths: PromQL rules, OTEL AI pipeline, Grafana DORA panels |
| **A** | (configure per environment) | — | — | Standard development: compose, Alloy, OTEL standard pipelines |
| **B** | (configure per environment) | — | — | Routine tasks: docs, runbooks, simple YAML |
| **C** | (configure per environment) | — | — | Trivial edits only |
| **F** | (same as C) | — | — | Emergency fallback |

### The Real Routing Constraint: No Shell Access

Some agent dispatch paths run with shell access denied by design — the
agent can't run tests, start the stack, or verify anything locally, only
edit files and open a PR, leaving CI as the sole verification before a
human looks at it. **This constraint, not raw model strength, is what
actually decides what's safely delegable to a no-shell dispatch path.**
The current concrete instance of this in this repo:
`.github/workflows/opencode.yml` dispatches every agent session with
`OPENCODE_PERMISSION: '{"bash": "deny"}'` — but the routing logic below
applies to any orchestrator with the same no-shell property, not
specifically to OpenCode.

- **Safe to route at Grade B/C**, including a free/low-cost tier meeting
  Grade B's benchmark thresholds as the default there: work where the
  spec fully constrains the outcome and CI can catch a wrong answer — a
  single YAML edit, a version bump, a doc fix, a narrowly-scoped test fix
  with an existing test asserting it.
- **Escalate to Grade S/A regardless of task size**: anything needing
  live-system verification (the agent can't run `make up` to check),
  CI/deploy pipeline changes (a wrong workflow edit breaks merges for
  everyone, and the agent can't dry-run it), security decisions, or
  cross-file architectural work where CI's test coverage can't fully
  express correctness.

### Fallback Chain

```
Grade S → Grade A → Grade B → Grade F
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
| 2026-09-24 | All | OpenCode grade-based | Platform/provider-agnostic grade-based | Removed remaining OpenCode/MiMo-specific product names from routing prose and enforcement notes (#346); grade definitions and routing logic now name no orchestrator or model by default, only benchmark thresholds and dispatch-mode properties (e.g. no-shell access) | This file's diff |

---

## Model Policy Enforcement

- The agent orchestrator's own config file sets the fallback chain and default model (currently `opencode.json`, for this repo's OpenCode dispatch) — swap this line if the orchestrator changes, the grade definitions above don't need to
- Agent YAML files specify grades for operational agents (test, review, etc.)
- If a Grade S provider requires a local proxy or gateway service to reach it, confirm that service is actually running before dispatching to that grade — this repo has no such service wired into `compose.yaml` today

---

## See Also

- `AGENTS.md` §3 — Context Files (references this file)
- `AGENTS.md` §4 — Architecture Rules (OTEL AI pipeline changes require Grade S)
- `.agents/agents/otel-collector.md` — OTel agent constraints
- `docs/ai-observability-guide.md` — AI pipeline architecture and instrumentation
