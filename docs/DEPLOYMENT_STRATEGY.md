# Deployment Strategy — uFawkesObs

> The target delivery model for uFawkesObs. This is a living document;
> update it as the deployment model evolves.

---

## Current Model (SSH Push)

uFawkesObs currently deploys via SSH push to a single host. The process:

1. **Push to `main`** triggers `deploy.yml`
2. **Path detection** determines what changed (config vs compose)
3. **Config-only changes**: `git pull` on target → Prometheus `/-/reload` + Alloy `SIGHUP`
4. **Compose/non-reloadable changes**: `git pull` → `make up` (full compose restart)
5. **Post-deployment verification**: smoke tests against the live instance
6. **Rollback on failure**: `git revert` + optional restart

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
| **Rollback** | All | Automated on gate failure | `git revert` + `make up` |

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

When `post-deploy-verify` fails in `deploy.yml`, the `rollback` job
(`paruff/ufawkespipe/.github/workflows/reusable-rollback.yml@v1.2.0`):
1. SSHs into the target host
2. Runs `git revert HEAD --no-edit`
3. Pushes the revert to `origin main`
4. Runs `make up` to restart the previous stack

> **Not yet proven.** This path is documented and wired in CI but has never
> been exercised end-to-end against a real host. It is **unproven** until a
> live rollback drill records successful results (LB-04). See
> [Rollback Drill (LB-04)](#rollback-drill-lb-04) below.

### Rollback Drill (LB-04)

The end-to-end drill is defined in
[`docs/ROLLBACK_DRILL.md`](ROLLBACK_DRILL.md) — an executable procedure that
pushes a deliberately-bad commit to a non-prod host, confirms
`post-deploy-verify` catches it, confirms the `rollback` job fires
automatically, and confirms the host returns to a healthy previous state.

Status: **PENDING** — runbook ready, live drill not yet executed against a real
target host ([issue #182](https://github.com/paruff/uFawkesObs/issues/182)).

2026-08-11: static enablement review (guard tests + wiring verification)
confirmed the drill's fault-injection path (`config/otel/**` →
`deploy-compose-restart` → `post-deploy-verify` → `rollback`) is wired in
`deploy.yml`, and cleared the suspected runner-token blocker in
[issue #193](https://github.com/paruff/uFawkesObs/issues/193) (the revert+push
runs on the target host, not the runner). The live drill still must prove host
push credentials and `main` branch protection permit the revert.

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

# Revert the last deploy commit
git revert HEAD --no-edit
git push origin main

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
