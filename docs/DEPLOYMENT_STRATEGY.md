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
When `post-deploy-verify` fails in `deploy.yml`, the `rollback` job:
1. SSHs into the target host
2. Runs `git revert HEAD --no-edit`
3. Pushes the revert to `origin main`
4. Runs `make up` to restart the previous stack

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
