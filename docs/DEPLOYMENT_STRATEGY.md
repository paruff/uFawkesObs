# Deployment Strategy — uFawkesObs

> The target delivery model for uFawkesObs. This is a living document;
> update it as the deployment model evolves.

---

## Current Model (SSH Push)

uFawkesObs currently deploys via SSH push to a single host. The process:

1. **Merge to `main`** passes Acceptance Full, which triggers `deploy.yml`
2. **Tag the candidate**: an immutable `deploy-<UTC-ts>-<sha>` tag is created
   and pushed, pinned to the exact verified commit — this is what gets
   deployed, not whatever `main` happens to be by the time the job runs
3. **Path detection** determines what changed (config vs compose)
4. **Config-only changes**: target host checks out the candidate tag →
   Prometheus `/-/reload` + Alloy `SIGHUP`
5. **Compose/non-reloadable changes**: target host checks out the candidate
   tag → `make up` (full compose restart)
6. **Post-deployment verification**: smoke tests against the live instance;
   on success, `deploy-latest-good` is force-pushed to the candidate SHA
7. **Rollback on failure**: target host checks out `deploy-latest-good` →
   `make up`. No `git revert`, no push to `main` — rollback only ever reads
   an already-published tag (LB-04 redesign, [#182](https://github.com/paruff/uFawkesObs/issues/182))

### Limitations of Current Model

| Limitation | Impact |
|---|---|
| Single host (no canary) | Any bad deploy affects all users |
| Manual rollback (scripted, not automated at platform level) | Recovery depends on SSH access |
| No staging environment | Changes go directly to production |
| No traffic splitting | Cannot A/B test config changes |

---

## Target Model (Progressive Delivery)

When uFawkesObs serves production traffic, deploy will follow a staged model:

```
┌─────────┐     ┌──────────┐     ┌────────────┐     ┌──────────┐
│  Canary  │ ──→ │ Staging  │ ──→ │ Production │ ──→ │ Rollback │
│ (1 host) │     │ (1 host) │     │ (N hosts)  │     │ (any)    │
└─────────┘     └──────────┘     └────────────┘     └──────────┘
     │               │                │                  │
     └── automated   └── automated    └── manual gate    └── automated
         health          health            (human          revert +
         checks          checks             approval)      restart
```

### Stage Details

| Stage | Hosts | Gate | Automation |
|---|---|---|---|
| **Canary** | 1 host | Automated health checks | Deploy → verify → promote or rollback |
| **Staging** | 1 host | Automated health checks + smoke tests | Same as canary |
| **Production** | N hosts (behind LB) | Human approval required | Deploy to subset, verify, full rollout |
| **Rollback** | All | Automated on gate failure | checkout `deploy-latest-good` + `make up` |

### Prerequisites for Progressive Delivery

Before implementing the target model:

1. [ ] **Multi-host inventory** — Ansible or similar for managing multiple targets
2. [ ] **Load balancer** — Front all hosts with a reverse proxy (nginx, Caddy, etc.)
3. [ ] **Health check endpoint** per service (most already have `/ready` or `/health`)
4. [ ] **Observability gate** — Automated Prometheus alert evaluation as a deploy gate
5. [ ] **Staging environment** — Second host or namespace with production-like config

---

## Rollback Procedure

### Automated (Current)

When `post-deploy-verify` fails in `deploy.yml`, the inline `rollback` job:
1. SSHs into the target host
2. Fetches tags and checks out `deploy-latest-good` (the most recent
   candidate tag that actually passed `post-deploy-verify`)
3. Runs `make up` to restart that stack

No `git revert`, no push — rollback is purely read-only from git's
perspective (fetch + checkout), on the runner and on the host. This is a
deliberate redesign (LB-04, [#182](https://github.com/paruff/uFawkesObs/issues/182)):
the previous `git revert HEAD` + push-to-`main` design was structurally
incompatible with the branch protection enabled on `main` (required PR
review blocks any direct push, including the host's revert). Rollback never
touching `main` makes that conflict structurally impossible rather than a
static argument to re-check on every branch-protection change.

> **Not yet proven.** This path is wired and unit-tested (`tests/unit/
> test_deploy_pipeline.py::TestTagBasedDeployRollback`) but has never been
> exercised end-to-end against a real host. It is **unproven** until a live
> rollback drill records successful results. See
> [Rollback Drill (LB-04)](#rollback-drill-lb-04) below.

### Rollback Drill (LB-04)

The end-to-end drill is defined in
[`docs/ROLLBACK_DRILL.md`](ROLLBACK_DRILL.md) — an executable procedure that
pushes a deliberately-bad commit to a non-prod host, confirms
`post-deploy-verify` catches it, confirms the `rollback` job fires
automatically, and confirms the host returns to a healthy previous state.

Status: **PENDING** — runbook ready, live drill not yet executed against a real
target host ([issue #182](https://github.com/paruff/uFawkesObs/issues/182)).
An OCI Compute sandbox host is being provisioned as the drill target.

2026-08-21: redesigned deploy/rollback to be tag-based instead of
`git revert`-based, since the original design's host-side push to `main`
would have been rejected by the branch protection enabled this session. The
new design has no push path to `main` at all — see "Automated (Current)"
above. This supersedes the 2026-08-11 static review of
[issue #193](https://github.com/paruff/uFawkesObs/issues/193) (that review's
"does the push run on the runner or the host" question no longer applies,
since rollback doesn't push anywhere). The only remaining live-drill unknown
is whether `deploy-latest-good` actually resolves and checks out cleanly
under real network/SSH conditions.

| Drill date | Host | Pre-drill SHA | Time to rollback | Recovered? | Gaps |
|---|---|---|---|---|---|
| _pending_ | — | — | — | — | — |

Any gap found during the drill gets its own follow-up issue; results and
corrections land back in `docs/ROLLBACK_DRILL.md`.

### Manual (Fallback)

```bash
# SSH into target host
ssh user@host

# Navigate to repo
cd /path/to/uFawkesObs

# Check out the last known-good deploy tag
git fetch --tags --force origin
git checkout --detach deploy-latest-good

# Restart the stack
make up
```

---

## Environment-Specific Config

Currently all environments use the same `compose.yaml` and config files.
When multi-environment support is added:

| Env | Config Source | Overrides |
|---|---|---|
| Canary | `config/` | Canary-specific scrape targets |
| Staging | `config/` | Staging Grafana datasources |
| Production | `config/` | Production secrets, scrape targets |

Config files remain **declarative** and **environment-agnostic** at the file level.
Environment overrides use Docker Compose's `-f` / `--profile` mechanism, not
separate config trees.
