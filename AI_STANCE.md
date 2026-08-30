# AI Stance — uFawkesObs

> Last reviewed: 2026-08-10
> Next review due: 2026-11-10 (quarterly)
> Owner: paruff
> Suite: uFawkesAI
> DORA AI Capability: 1 — Clear and communicated AI stance

## Expectation of use

AI-assisted development is expected in this repo. We use AI tools to clear
bottlenecks in the product lifecycle — drafting config, writing tests, reviewing
changes. AI does not replace human judgment on alerting rules, security
configuration, or architecture decisions. All AI assistance is logged via
opencode session history.

## Organizational support

- Permitted tools: listed below
- Skill suite: uFawkesAI `.agents/skills/` — load relevant skills before each session
- Context corpus: maintained via the context-engineering skill (load at session start)
- Questions or policy concerns: file a GitHub issue with label `ai-policy`
- Policy reviews: quarterly

## Permitted tools

| Tool | Model / version | Scope |
|---|---|---|
| opencode | latest stable | Primary agentic development tool |
| Claude | claude-sonnet-4-6 | Skill authoring, code review, content generation |
| GitHub Copilot | current | IDE code completion |
| graphify | confirm variant before use | Context corpus building |
| ponytail | latest stable | YAGNI enforcement in agent sessions |

## Three-bucket classification

### Prohibited

- Sending credentials, populated `.env` files, or telemetry data containing
  PII to public AI models
- Committing AI-generated code without pre-commit hooks passing (`make test`)
- Bypassing branch protection rules on AI guidance
- Publishing AI-generated security disclosures or CVE responses without
  qualified human review

**uFawkesObs-specific prohibition:**
AI-generated Prometheus alerting rules or Alertmanager routing configs require
human review and a test case before merge. Alerts trigger real pagers —
false positives have a real operational cost.

### Permitted with guardrails

| Use | Guardrail |
|---|---|
| AI-generated code merged to main | Human review required; at least one test covering the change |
| AI-generated Grafana dashboard JSON | Human must verify queries return correct data against a running stack |
| AI-assisted OpenTelemetry Collector config | Config unit test (`pytest tests/unit/`) must pass |
| AI-generated release notes | Human review before publishing to GitHub Releases |
| AI-generated documentation | Human review for accuracy; no fabricated version numbers or commands |
| opencode sessions modifying infrastructure | Load AGENTS.md and this file at session start |
| graphify corpus built from this repo | Corpus must exclude files containing secrets or credential material |

### Allowed

- AI-assisted code completion for any file not in the Prohibited scope
- AI-generated first drafts of docs, blog posts, issue descriptions
- AI-assisted GitHub issue triage and label suggestions
- AI-generated test stubs (human completes and verifies against a running stack)
- Asking AI tools to explain existing configuration or architecture

## Role applicability

This stance applies to: **human contributors AND AI agents** (opencode sessions,
GitHub Actions opencode workflow, any automated agent invocation in this repo).

Agents must:

1. Load `ai-stance` skill and verify this document exists before beginning work
2. Log the session via opencode session history
3. Flag any action that falls into the Prohibited bucket and halt — do not
   proceed without explicit human authorization for prohibited actions
4. Never generate or suggest `chmod -R 777` as a solution — direct to
   `docs/production-hardening.md` instead

## Why this matters for uFawkesObs specifically

uFawkesObs is the telemetry substrate for the entire uFawkes suite. A
misconfigured alerting rule or broken Prometheus scrape config can silently
drop observability for every downstream plane. The guardrails above exist
because the cost of an unreviewed AI error here propagates further than it
would in a self-contained application.
