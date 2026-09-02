# Rollback Drill — uFawkesObs

> **Status: PARTIALLY EXERCISED** — the rollback *mechanism* was demonstrated
> working against the local Docker instance on 2026-09-02 (see
> [Drill Results](#drill-results--2026-09-02-local-instance)). The full
> procedure below — SSH transport, `compose-restart` environment approval,
> `workflow_run` triggering — has **not** been run and LB-04 is not closed.
>
> The 2026-08-30 blocker has cleared: `DEPLOY_HOST`, `DEPLOY_USER`,
> `DEPLOY_KEY` and `DEPLOY_HOST_KEY` are now set, and `DEPLOY_PATH` is
> configured. Note that `DEPLOY_PATH` currently points at a path on the
> maintainer's own machine, so Precondition 1's "throwaway / sandbox host,
> not production" is still unsatisfied for the full drill.
> See [LB-04](https://github.com/paruff/uFawkesObs/issues/182).
>
> Part of the Path to Late Beta plan — `docs/PATH_TO_LATE_BETA.md`.

This document is the **executable** procedure for deliberately breaking a
non-production deployment and confirming the automated rollback path
(`post-deploy-verify` → `rollback`) actually restores the host. It exists
because the rollback machinery in `deploy.yml` has never been exercised
end-to-end, and a beta adopter must be able to trust that rollback works the
one time it is needed.

The drill is run by a human (PM or infra owner) with GitHub repo admin access
and SSH access to the non-prod target host. **Never run this against a host
that carries production traffic.**

---

## Preconditions

Before starting, confirm all of the following. If any is missing, **stop** and
resolve it before running the drill.

### 1. A non-prod target host

- `DEPLOY_HOST` / `DEPLOY_USER` / `DEPLOY_KEY` / `DEPLOY_HOST_KEY` repo
  secrets must point at a **throwaway / sandbox host**, not production.
- `DEPLOY_PATH` repo variable set to the absolute clone path on that host.
- Confirm the current production host is **not** the drill host:
  ```bash
  gh secret list                       # repo-level secrets
  gh variable list                     # repo-level variables
  ```
  Verify `DEPLOY_HOST` resolves to the sandbox.

### 2. Healthy baseline

On the target host, the stack must already be healthy at the commit you are
about to break:

```bash
ssh "${DEPLOY_USER}@${DEPLOY_HOST}"
cd "${DEPLOY_PATH:-$HOME/uFawkesObs}"
git status --short          # clean
git log --oneline -3        # note the current HEAD
docker compose ps           # all services running
./scripts/wait-healthy.sh   # exit 0
```

### 3. Host can fetch tags

Deploy and rollback are both tag-based (LB-04 redesign) — rollback checks
out `deploy-latest-good` on the host and **does not push to main**, so main's
branch protection has no bearing on rollback at all. The only requirement:

- The target host's clone must have a working `origin` remote it can
  **fetch** from (verify with `git fetch --tags origin` from the host — no
  push credential is needed for this step).
- Landing the bad commit on `main` (Step 2 below) still goes through the
  normal PR path, since branch protection requires a PR + review to reach
  `main` — the drill no longer force-pushes directly to `main`.

### 4. Environment approval ready

The compose-restart deploy path requires GitHub Environment approval
(`environment: compose-restart`). During the drill a human must be ready to
**approve** that environment when prompted.

### 5. Timing baseline

Record the current time and the deploy run numbers so the drill can be timed:

```bash
date -u +%FT%TZ
gh run list --workflow="GitOps Reconciliation Deploy" --limit 3
```

### 6. Notify / schedule

The drill intentionally turns `main` red for a few minutes (a broken commit is
pushed, CI fails, and — if all goes well — the rollback re-reverts it). Pick a
window when no one is merging, and announce it in the team channel.

---

## Bad-Deploy Recipe

Goal: a commit where **the deploy succeeds but `post-deploy-verify` fails**.
That is the only failure mode that triggers the `rollback` job
(`if: failure() && needs.post-deploy-verify.result == 'failure'` in
`deploy.yml`). If the deploy step itself fails, `post-deploy-verify` is skipped
and rollback never fires — so the recipe must not break the deploy step.

**Recommended recipe:** break `config/otel/collector.yaml` with a YAML syntax
error.

Why this works:

- `config/otel/**` is classified as `non_reloadable_config` by
  `detect-changes`, so `deploy-compose-restart` runs (`make up`).
- `docker compose up -d` exits 0 even if the OTel Collector container crashes
  shortly after start — the deploy step **succeeds**.
- `post-deploy-verify` runs `scripts/wait-healthy.sh`, which probes
  `http://localhost:8888/metrics`. The Collector never comes up, so the probe
  times out, `wait-healthy.sh` exits non-zero, and `post-deploy-verify`
  **fails**.
- Rollback triggers, reverts the commit, and restarts the previous stack.

Create the bad commit (example — an unparseable YAML scalar):

```bash
git checkout -b drill/lb04-bad-deploy
printf 'receivers:\n  otlp:\n   protocol: \n    : broken\n' \
  > config/otel/collector.yaml
git add config/otel/collector.yaml
git commit -m "chore(drill): deliberately break otel collector config (LB-04)"
git push origin drill/lb04-bad-deploy
```

Branch protection on `main` requires a PR + review, so this no longer lands
via a direct push — open and merge it like a real change (Step 2 below).

Alternative recipes (same failure mode, choose one):

- Break `config/alertmanager/alertmanager.yml` (also `non_reloadable_config`).
- Override a service `command:` in `compose.yaml` to an invalid flag so the
  container exits at boot (compose path).

Do **not** use a bad Prometheus config as the recipe: Prometheus `/-/reload`
returns 200 even when the reload fails, so `deploy-config-reload` and the
health probe both "pass" and rollback never fires. That is a realistic
false-negative, but it does not exercise the rollback path.

---

## Drill Procedure

Execute in order. Record timestamps and evidence as you go (see
[Evidence Log](#evidence-log)).

### Step 1 — Record baseline

```bash
date -u +%FT%TZ
ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "${DEPLOY_PATH:-$HOME/uFawkesObs}/scripts/wait-healthy.sh" && echo BASELINE_OK
```

### Step 2 — Land the bad commit on main

```bash
gh pr create --base main --head drill/lb04-bad-deploy \
  --title "chore(drill): deliberately break otel collector config (LB-04)" \
  --body "Rollback drill — see docs/ROLLBACK_DRILL.md. Do not squash-merge as a real fix."
gh pr merge --squash --admin   # repo admin self-approve; a non-admin needs a real review
```

> Expected: merging starts **Acceptance Full (Post-Merge)** on the bad SHA
> (deploy.yml has been acceptance-gated since LB-05/#183 — it no longer
> triggers directly on `push`). When that workflow completes, `deploy.yml`'s
> `tag-candidate` job tags and pushes the bad SHA as
> `deploy-<ts>-<sha>`, and a run of **GitOps Reconciliation Deploy** starts;
> `detect-changes` → `deploy-compose-restart` waits on the `compose-restart`
> environment approval.

### Step 3 — Approve the compose-restart environment

In the Actions UI, open the deploy run → **Approve** the `compose-restart`
environment.

### Step 4 — Watch the deploy + verification

Expected sequence on the host (watch via
`ssh … 'cd ${DEPLOY_PATH} && docker compose ps && docker logs --tail 20 otel-collector'`):

1. `git pull --ff-only origin main` brings down the bad commit.
2. `make up` starts the stack; the OTel Collector crashes (`exec … no YAML` /
   config parse error in logs).
3. `post-deploy-verify` runs `wait-healthy.sh`; after the timeout it reports
   `❌ OTel Collector not healthy` and the job **fails**.

### Step 5 — Confirm the rollback fires automatically

- The inline `rollback` job in `deploy.yml` must start **automatically** (no
  human trigger) within seconds of `post-deploy-verify` failing.
- Expected inside the rollback job:
  1. SSH to target.
  2. `git fetch --tags --force origin` — read-only, no push credential used.
  3. `git checkout --detach deploy-latest-good` — the last candidate tag that
     actually passed `post-deploy-verify` (never the just-failed bad one,
     since it was never promoted).
  4. `make up` — that stack restarts.
- Rollback does not push to `main`, and it does not run `git revert`
  anywhere, on the runner or the host — this is what makes it immune to
  main's branch protection.

### Step 6 — Confirm recovery

- On the host, confirm the previous healthy state:
  ```bash
  ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "${DEPLOY_PATH:-$HOME/uFawkesObs}/scripts/wait-healthy.sh" && echo RECOVERED
  docker compose ps
  ```
- **`main` is not automatically fixed** — unlike the old revert-based design,
  the tag-based rollback only recovers the *deployed host*; the bad commit
  stays merged on `main` until a human lands a real fix or revert PR (see
  [Safety & Cleanup](#safety--cleanup)). This is a deliberate trade-off: the
  host recovers immediately and automatically, and the actual code fix goes
  through normal review instead of an unreviewed automated revert.
- Confirm `deploy-latest-good` still points at the pre-drill (good) SHA, not
  the drill's bad one:
  ```bash
  git fetch origin main && git log origin/main --oneline -3   # bad commit still present
  git rev-parse deploy-latest-good   # should equal the pre-drill SHA
  ```

**Drill success criteria (all must hold):**

1. `post-deploy-verify` caught the bad deploy (job failed).
2. `rollback` fired automatically — no human pressed the button.
3. The host returned to a healthy previous state.
4. `deploy-latest-good` was never advanced to the bad commit's tag — it still
   points at the last genuinely good deploy.

---

## Evidence Log

Capture each line into a pastebin/comment on the drill's follow-up issue
(below). The workflow run URL is the primary artifact:

```
Workflow run: https://github.com/paruff/uFawkesObs/actions/runs/<RUN_ID>
```

| # | Timestamp (UTC) | Event | Expected | Observed | Pass/Fail |
|---|---|---|---|---|---|
| 1 | | Baseline `wait-healthy.sh` | exit 0 | | |
| 2 | | Bad commit merged to main via PR | Acceptance Full starts | | |
| 3 | | `tag-candidate` job | pushes `deploy-<ts>-<sha>` for the bad SHA | | |
| 4 | | `compose-restart` env approved | deploy proceeds | | |
| 5 | | OTel Collector container | crashes at boot | | |
| 6 | | `post-deploy-verify` | FAILS (wait-healthy timeout); `deploy-latest-good` NOT advanced | | |
| 7 | | `rollback` job | auto-starts | | |
| 8 | | `git fetch --tags` on host | succeeds (read-only) | | |
| 9 | | `git checkout --detach deploy-latest-good` | checks out last good tag | | |
| 10 | | `make up` after checkout | previous stack restarts | | |
| 11 | | Recovery `wait-healthy.sh` | exit 0 | | |
| 12 | | `deploy-latest-good` after drill | still points at pre-drill SHA | | |

**Timing:** note seconds from Step 2 push → Step 5 rollback start, and from
Step 5 → Step 6 recovery. These go into the results table.

---

## Drill Results — 2026-09-02 (local instance)

A reduced drill run against the **local Docker instance**, not over SSH.

**What it exercised:** the same sequence the `deploy-*` and `rollback` jobs run
on the host — check out a revision, `make up`, gate on `scripts/wait-healthy.sh`,
emit a DORA deployment event.

**What it did not exercise:** the SSH transport, the `compose-restart`
environment approval, and `workflow_run` triggering. Those are the Actions
plumbing *around* the sequence. The full procedure above remains to be run.

**Failure recipe used:** invalid `config/prometheus/prometheus.yaml` plus
`docker compose up -d --force-recreate prometheus`. Note this is *not* the
recipe recommended above — and the warning there still stands: on the
`deploy-config-reload` path, Prometheus `/-/reload` returns 200 even when the
reload fails, so a bad Prometheus config does **not** exercise that path. Here
the container was force-recreated and genuinely failed to start, which is the
compose-restart failure mode.

| # | Event | Expected | Observed | Pass/Fail |
|---|---|---|---|---|
| 1 | Baseline `wait-healthy.sh` | exit 0 | 7/7 core services healthy | **PASS** |
| 2 | Bad config deployed, container recreated | Prometheus fails to start | crash-loop, `cannot unmarshal !!map into string` | **PASS** |
| 3 | Post-deploy verification | exit 1 | `❌ Prometheus not healthy`, exit 1 | **PASS** |
| 4 | DORA `failed` event | recorded | `deployment event sent (status=failed)` | **PASS** |
| 5 | Roll back to known-good revision | config restored | hash matched baseline exactly | **PASS** |
| 6 | Recovery `wait-healthy.sh` | exit 0 | Prometheus healthy in **2s** | **PASS** |
| 7 | DORA recovery event | recorded | **dropped** — see gap 3 | **FAIL** |

**Success criteria 1–3 from the runbook hold:** the bad deploy was caught, and
the rollback returned the host to healthy. Criterion 2 ("rollback fired
automatically") was not tested — the rollback was invoked directly rather than
by `post-deploy-verify` failing.

### Gaps found

Each has its own follow-up issue, per the rules below.

| # | Gap | Issue | Status |
|---|---|---|---|
| 1 | `wait-healthy.sh` required Bash 4; macOS deploy host has 3.2, so the health gate could never pass | [#322](https://github.com/paruff/uFawkesObs/issues/322) | Fixed |
| 2 | `rollback` checks out `deploy-latest-good`, a tag that has never existed | [#323](https://github.com/paruff/uFawkesObs/issues/323) | Guarded; bootstrap still manual |
| 3 | `send-dora-deployment-event.sh` silently drops failed events, unpairing rollback recovery | [#324](https://github.com/paruff/uFawkesObs/issues/324) | Open |

Gaps 1 and 2 were **blocking** — the drill could not run until gap 1 was fixed,
and a rollback could not have succeeded at all with gap 2 unaddressed.

### Note for whoever runs the full drill

Capture exit codes directly (`cmd; rc=$?`), never through a pipe.
`PIPESTATUS` is not portable between bash and zsh and misreported a passing
assertion as a failure on the first run of this drill.

---

## Results & Follow-Up

After the drill, fill in the summary and link it from
`docs/DEPLOYMENT_STRATEGY.md` (Rollback Drill section) and this file's status
line.

```markdown
## Drill Results — <date> (run <RUN_ID>)

- Host: <non-prod host>
- Pre-drill SHA: <...>  Bad candidate tag: <deploy-...>
- Time to rollback start: <s>   Time to recovery: <s>
- post-deploy-verify caught the break: yes/no
- rollback fired automatically: yes/no
- Host returned to healthy: yes/no
- deploy-latest-good still points at the pre-drill SHA: yes/no
- Gaps found: <list>
```

**Rules for gaps** (from issue #182):

- Any gap found gets its **own follow-up issue** — do not silently patch it in
  the same PR that documents the drill.
- Every gap issue must reference this drill's run URL and the failing evidence
  row(s).

### Design history

**2026-08-11 (LB-04 enablement):** a static review found the original
`git revert HEAD` + host push design's suspected gap (issue #193, "does the
runner's `GITHUB_TOKEN` block the push?") was refuted — the push executed on
the target host over SSH, not the runner, so token permissions never gated
it. Two unknowns remained that only a live run could clear: whether the host
held a working push credential, and whether main's branch protection would
let the revert land.

**2026-08-21 (this redesign):** rather than resolve those unknowns, the
mechanism changed so they no longer apply. Rollback now checks out
`deploy-latest-good` on the host instead of reverting and pushing — it
**does not push to main** at all, on the runner or the host. This
structurally eliminates both #193's original concern and its interaction
with branch protection, rather than depending on a specific credential or
protection-rule configuration holding. The only unknown a live drill still
needs to clear: does `deploy-latest-good` actually resolve and check out
cleanly under real network/SSH conditions.

---

## Safety & Cleanup

- **Never run against a production host.** Verify `DEPLOY_HOST` first
  (Preconditions).
- If automated rollback does **not** fire or does not complete, restore the
  host manually **immediately**:

  ```bash
  ssh "${DEPLOY_USER}@${DEPLOY_HOST}"
  cd "${DEPLOY_PATH:-$HOME/uFawkesObs}"
  git fetch --tags --force origin
  git checkout --detach deploy-latest-good
  make up
  ./scripts/wait-healthy.sh
  ```

- **`main` always needs manual cleanup after this drill**, whether or not
  rollback succeeded — the tag-based design deliberately leaves the bad
  commit merged on `main` (see Step 6). Open and merge a normal revert PR:

  ```bash
  git revert --no-edit <bad-commit-sha>
  gh pr create --base main --title "revert: LB-04 drill bad commit" --body "See docs/ROLLBACK_DRILL.md"
  gh pr merge --squash --admin
  ```

- Confirm the drill branch is deleted:
  ```bash
  git push origin --delete drill/lb04-bad-deploy
  git branch -D drill/lb04-bad-deploy
  ```
- If any step could not be completed, leave LB-04 **PENDING** and file a
  follow-up issue describing the blocker. Do not mark the drill done.
