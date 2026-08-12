# Rollback Drill — uFawkesObs

> **Status: PENDING** — runbook ready; the live drill has not been executed
> against a real target host yet. See [LB-04](https://github.com/paruff/uFawkesObs/issues/182).
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

### 3. Main is pushable

The drill pushes a deliberately-bad commit to `main`, and the automated
rollback pushes a revert to `main`. Both must be permitted:

- The rollback's `git push origin main` executes **on the target host over
  SSH** — the host pushes with its own cloned `origin` credential, not a runner
  token. The host must therefore already hold a working **push credential**
  for `origin` (verify with `git fetch origin main` from the host).
- Check branch protection on `main` (Settings → Branches). If it rejects the
  host's push or a direct push path, the drill **cannot run as automated** —
  use the manual fallback in [Safety & Cleanup](#safety--cleanup) and file a
  follow-up issue.

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

### Step 2 — Push the bad commit to main

```bash
git push origin drill/lb04-bad-deploy:main
```

> Expected: **Acceptance Full (Post-Merge)** starts on the bad SHA (deploy.yml
> has been acceptance-gated since LB-05/#183 — it no longer triggers directly
> on `push`). When that workflow completes, a run of **GitOps Reconciliation
> Deploy** starts on the bad SHA; `detect-changes` →
> `deploy-compose-restart` waits on the `compose-restart` environment approval.

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

- The `rollback` job (`uses: paruff/ufawkespipe/.github/workflows/reusable-rollback.yml@v1.2.0`)
  must start **automatically** (no human trigger) within seconds of
  `post-deploy-verify` failing.
- Expected inside the rollback job:
  1. SSH to target.
  2. `git revert --no-edit HEAD` — reverts the bad commit **locally**.
  3. `git push origin main` — the revert must reach `main`.
  4. `make up` — previous stack restarts.

### Step 6 — Confirm recovery

- The rollback push creates a **new** deploy run on the revert SHA; that run's
  `post-deploy-verify` must pass.
- On the host, confirm the previous healthy state:
  ```bash
  ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "${DEPLOY_PATH:-$HOME/uFawkesObs}/scripts/wait-healthy.sh" && echo RECOVERED
  docker compose ps
  ```
- Confirm `main` is clean and CI is green again:
  ```bash
  git fetch origin main && git log origin/main --oneline -3   # HEAD~1 == pre-drill SHA
  gh run list --limit 5
  ```

**Drill success criteria (all must hold):**

1. `post-deploy-verify` caught the bad deploy (job failed).
2. `rollback` fired automatically — no human pressed the button.
3. The host returned to a healthy previous state.
4. `main` self-healed: it contains the revert, and the post-revert deploy
   verified green.

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
| 2 | | Bad commit pushed to main | deploy run starts | | |
| 3 | | `compose-restart` env approved | deploy proceeds | | |
| 4 | | OTel Collector container | crashes at boot | | |
| 5 | | `post-deploy-verify` | FAILS (wait-healthy timeout) | | |
| 6 | | `rollback` job | auto-starts | | |
| 7 | | `git revert` on host | local revert applied | | |
| 8 | | `git push origin main` (revert) | main reverted | | |
| 9 | | `make up` after revert | previous stack restarts | | |
| 10 | | Recovery `wait-healthy.sh` | exit 0 | | |
| 11 | | Post-revert deploy verify | PASS | | |
| 12 | | `main` CI | green | | |

**Timing:** note seconds from Step 2 push → Step 5 rollback start, and from
Step 5 → Step 6 recovery. These go into the results table.

---

## Results & Follow-Up

After the drill, fill in the summary and link it from
`docs/DEPLOYMENT_STRATEGY.md` (Rollback Drill section) and this file's status
line.

```markdown
## Drill Results — <date> (run <RUN_ID>)

- Host: <non-prod host>
- Pre-drill SHA: <...>  Post-revert SHA: <...>
- Time to rollback start: <s>   Time to recovery: <s>
- post-deploy-verify caught the break: yes/no
- rollback fired automatically: yes/no
- Host returned to healthy: yes/no
- main self-healed: yes/no
- Gaps found: <list>
```

**Rules for gaps** (from issue #182):

- Any gap found gets its **own follow-up issue** — do not silently patch it in
  the same PR that documents the drill.
- Every gap issue must reference this drill's run URL and the failing evidence
  row(s).

### Static review of the suspected gap — 2026-08-11 (LB-04 enablement)

The suspected gap below was re-checked statically during LB-04 enablement
(`tests/unit/test_deploy_pipeline.py` and `tests/unit/test_deploy_docs.py`).

**Verdict: issue #193's two stated reasons are refuted.** The rollback job's
`git revert` + `git push origin main` execute **on the target host over SSH,
not on the runner** — the git commands are shipped through an `ssh … bash -s`
heredoc in `reusable-rollback.yml@v1.2.0`. Consequences:

- The runner's `GITHUB_TOKEN` (downgraded to `contents: read`) is **not** the
  credential that pushes; the host pushes with its own `origin` credential, so
  the token-permission concern does **not** gate the drill.
- The missing `actions/checkout` on the runner is irrelevant to the push for
  the same reason; the steps that need `DEPLOY_KEY` read it directly from the
  `secrets:` pass-through, which read-only permissions do not block.

**Remaining live-drill unknowns (only the live run can clear these):**

- [ ] The target host holds a working **push credential** for `origin`.
- [ ] `main` branch protection lets the host's revert push land.

Evidence rows 6–9 in the Evidence Log exist to record these against the run.
Tracked in [issue #193](https://github.com/paruff/uFawkesObs/issues/193) —
the live drill confirms or refutes the remaining unknowns.

---

## Safety & Cleanup

- **Never run against a production host.** Verify `DEPLOY_HOST` first
  (Preconditions).
- The drill deliberately puts a broken commit on `main`. If automated rollback
  does **not** fire or does not complete, restore manually **immediately**:

  ```bash
  # From a clean checkout of main:
  git revert --no-edit HEAD
  git push origin main
  # On the target host:
  ssh "${DEPLOY_USER}@${DEPLOY_HOST}"
  cd "${DEPLOY_PATH:-$HOME/uFawkesObs}"
  git pull --ff-only origin main
  make up
  ./scripts/wait-healthy.sh
  ```

- After the drill, confirm the local drill branch is deleted and `main` has no
  leftover drill artifacts:
  ```bash
  git branch -D drill/lb04-bad-deploy
  git fetch origin main && git diff --stat origin/main@{1} origin/main || true
  ```
- If any step could not be completed, leave LB-04 **PENDING** and file a
  follow-up issue describing the blocker. Do not mark the drill done.
