# REVIEW.md — uFawkesObs Review Policy

Policy for every PR review: agentic review (Claude Code `reviewer` agent,
Code Review, `@claude`) and human review. It defines *what* gets checked
and *who* must approve. The checklist itself lives in one place:

- **Checklist:** [`.agents/agents/review.md`](.agents/agents/review.md) —
  run it in order (size gate, architecture, tests, security surface,
  AI-Assisted Review Block, author uncertainty).
- **Path rules:** `.claude/rules/*.md` for every path the diff touches.
- **PR format:** [`docs/PR_STANDARD.md`](docs/PR_STANDARD.md) — Conventional
  Commit title and the **AI-Assisted Review Block** (AGENTS.md §7).

## Findings

Report each finding with file:line, what breaks, a concrete failure
scenario, and severity. Rank the most severe first. If you can't verify
something without running the stack, say so rather than approving it.

| Severity | Meaning | Merge |
|---|---|---|
| **Blocker** | Breaks a hard rule (AGENTS.md §5 NEVER list, `.claude/rules/`), leaks a secret, or breaks deploy/rollback | No |
| **Major** | Wrong behavior, missing test for changed behavior, or a §5 "MUST Ask Before" change without sign-off | No, until resolved or the maintainer explicitly accepts it |
| **Minor** | Clarity, naming, docs drift | Yes; author decides |

## Human approval required

Agentic review is enough for docs, tests, and routine config (MODEL_POLICY
Grades B/C). The maintainer (`.github/CODEOWNERS`) must review before merge
when the PR touches:

- `.github/workflows/**`, `.claude/settings.json`, `.claude/hooks/**` —
  pipeline and agent guardrails
- `compose.yaml` image versions, ports, services, volumes, or env vars
  (AGENTS.md §5)
- `config/**`, `dashboards/**` — pushes to `main` deploy to the live host
  (AGENTS.md §8)
- anything security-related: auth, credentials, exposed ports, `SECURITY.md`

## Agents never

Approve their own PR, merge, apply `large-pr-approved`, or mark a review
APPROVED when a required check is red.
