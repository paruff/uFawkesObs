# Public Release Prep — Working Guide

Ordered guide to the open work before uFawkesObs goes public, and how to
dispatch each piece. Written 2026-09-12 from a repo review; update as issues
close.

Companions: `docs/PATH_TO_LATE_BETA.md` is the beta-readiness bar,
`docs/ROLLBACK_DRILL.md` the LB-04 procedure, `docs/KNOWN_LIMITATIONS.md` the
disclosed gaps.

---

## Where this stands

Green: every CI workflow on `main`, 591 unit tests, 94 acceptance scenarios,
Apache-2.0 with the full open-source file set, candid limitations docs, every
image version-pinned, third-party actions SHA-pinned.

Not green: the deploy path has not reached a host in ten days (#341), the
rollback path has never been proven end to end (#182), and coverage is
mandated at 80% but measured nowhere (#343).

The honest summary: **the product is in better shape than its release
machinery.**

---

## Order of work

Dependencies first — later items get cheaper, or become verifiable at all,
once the earlier ones land.

### 1. Unblock the pipeline

| # | Item | Who |
|---|---|---|
| [#341](https://github.com/paruff/uFawkesObs/issues/341) | `detect-changes` caret refspec breaks every deploy | Claude — **PR #354 open** |
| [#353](https://github.com/paruff/uFawkesObs/issues/353) | `RELEASE_PLEASE_TOKEN` missing in all five repos | **You only** |

Issue #341 comes first because nothing downstream can be verified while deploys
fail. Merging it also produces the live evidence #301 has always needed.

Issue #353 is five PATs. It is the highest-leverage item only a human can do:
release automation is installed everywhere and inert until the tokens exist,
and in `prei` it additionally means the build/scan/publish cascade has never
once run.

### 2. Prove recovery works

| # | Item | Who |
|---|---|---|
| [#182](https://github.com/paruff/uFawkesObs/issues/182) | LB-04 live rollback drill | You + Claude |
| [#342](https://github.com/paruff/uFawkesObs/issues/342) | LB-04 status contradicts the drill doc | MiMo |

The drill needs a sandbox host — `DEPLOY_PATH` currently points at a
workstation, which fails the runbook's own Precondition 1.
`ROLLBACK_DRILL.md` §0 covers standing up a Synology, including the four
things that would otherwise waste the attempt: runner reachability, `make`
missing on stock DSM, the port 5001 collision with DSM's own web UI, and
UID/permissions on `data/`.

Do #342 first regardless — a five-minute doc fix, and right now the
beta-readiness table tells anyone who reads it the wrong blocker.

### 3. Make the test claims true

| # | Item | Who |
|---|---|---|
| [#343](https://github.com/paruff/uFawkesObs/issues/343) | No coverage measurement despite an 80% mandate | Claude |
| [#344](https://github.com/paruff/uFawkesObs/issues/344) | Document the test pyramid and markers | MiMo |

Measure before setting a threshold. Picking 80% by fiat on day one breaks the
build and teaches everyone to route around the gate.

### 4. Clean the public face

| # | Item | Who |
|---|---|---|
| [#345](https://github.com/paruff/uFawkesObs/issues/345) | README is 602 lines | Claude |
| [#347](https://github.com/paruff/uFawkesObs/issues/347) | Doc-reality sweep: TODO/aspirational markers | MiMo (inventory only) |
| [#348](https://github.com/paruff/uFawkesObs/issues/348) | `docs/plan.md` status drift (LB-07) | MiMo |
| [#349](https://github.com/paruff/uFawkesObs/issues/349) | `DAY ONE.md` → `docs/DAY_ONE.md` | MiMo |
| [#351](https://github.com/paruff/uFawkesObs/issues/351) | Top-level clutter | You decide, MiMo executes |

Issue #347 asks for an **inventory first**, not edits. `KNOWN_LIMITATIONS.md` and
`fawkes-migration.md` were recently corrected and are easy to make worse.

### 5. Remaining correctness work

| # | Item | Who |
|---|---|---|
| [#334](https://github.com/paruff/uFawkesObs/issues/334) | Prometheus `/-/reload` returns 200 without applying | Claude |
| [#324](https://github.com/paruff/uFawkesObs/issues/324) | DORA recovery events silently dropped | Claude |
| [#331](https://github.com/paruff/uFawkesObs/issues/331) | Rework Rate definition alignment | MiMo (docs), Claude (thresholds) |
| [#335](https://github.com/paruff/uFawkesObs/issues/335) | LB-02 port surface half-done | You decide |
| [#350](https://github.com/paruff/uFawkesObs/issues/350) | Two opencode workflow files | Claude |
| [#352](https://github.com/paruff/uFawkesObs/issues/352) | Merge gate on a beta-tagged workflow | Claude |
| [#346](https://github.com/paruff/uFawkesObs/issues/346) | `MODEL_POLICY.md` describes a ladder that no longer exists | You |
| [#357](https://github.com/paruff/uFawkesObs/issues/357) | Harden opencode before allowing test execution | Claude |

Issue #334 matters more than its size suggests: `deploy-config-reload` is built on
that exact call, so config-only deploys can silently no-op and still go green.

Issue #335 needs a decision, not an implementation. Some of those ports **must**
stay open — `otel-collector:4317/4318` is the OTLP ingest other planes use.

---

## Dispatching work to opencode

### Handing an issue to an agent

The workflow triggers on **`opencode` plus one of** `ready-for-dev`,
`good-first-issue`, `feature`, `bug` — and only when the issue author is
OWNER, MEMBER or COLLABORATOR.

```bash
gh issue edit <n> --add-label opencode,ready-for-dev
```

Issues tagged `model:mimo-v2.5` were assessed as safe to route this way. The
`opencode` label is deliberately **not** pre-applied: adding it dispatches an
agent immediately, and that should be your call.

Override the model for one run:

```bash
gh workflow run opencode.yaml -f issue_number=<n> -f model=xiaomi/mimo-v2.5
```

### What decides MiMo vs Claude

Not model strength. The agent runs with **`bash` restricted to parsing tools**
(ruff, yamllint, shellcheck, markdownlint, read-only git). It cannot run
tests, start the stack, or verify anything by executing it — CI on its PR is
the verification.

So the question per issue is: **can this be specified precisely enough that
correctness is checkable without running it?**

**Route to MiMo** when inputs are enumerable and output is checkable by
reading: doc reconciliation, renames with a greppable blast radius, building a
table from files already in the repo, inventories.

**Keep with Claude** when the task needs live verification, touches CI or
deploy, involves a security decision, spans files in ways a spec cannot pin
down, or where being wrong is expensive.

### What the agent may run

```
git status|diff|log|show|rev-parse|ls-files
ruff check     ruff format --check
yamllint       shellcheck            markdownlint
```

Everything else is denied. `pytest`, `make test-*`, `pre-commit run` and
`docker` are excluded deliberately: they execute repo code — *including files
the agent just wrote* — so an allowlist cannot contain them. #357 covers the
hardening (OIDC-scoped token, egress policy) that would make test execution
defensible.

Treat the allowlist as a guardrail against mistakes, **not a security
boundary**. The step's `env:` carries `OPENCODE_API_KEY` and `GITHUB_TOKEN`,
so anything bash spawns inherits them, and trailing wildcards admit command
chaining. The real containment is the author gate.

**Practical consequence:** never paste untrusted text — an outside bug report,
a customer log, a stack trace from a stranger — into an issue body an agent
will process. Summarise it in your own words instead.

---

## Definition of done for "public release"

1. `main` green across all workflows **and** a deploy that actually reached a host
2. Rollback proven end to end against a sandbox (#182 closed on evidence)
3. No documented claim contradicted by the system (#342, #347, #348)
4. Coverage measured and reported, with the number stated honestly
5. README readable in two minutes
6. Release automation functional — PATs in place (#353)

Items 1 and 2 are the ones that would embarrass you publicly. The rest is
polish that makes the repo pleasant rather than credible.
