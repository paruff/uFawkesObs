# GitOps Reconciliation (CI-Triggered)

uFawkesObs now reconciles runtime state from Git on every push to `main` for deploy-relevant paths.

## Trigger Scope

Workflow: `.github/workflows/deploy.yml`

It runs on pushes to `main` when one or more of these paths change:

- `config/**`
- `compose.yaml`
- `.env.example`
- `dashboards/**`

Docs-only changes do not trigger reconciliation.

## Reconciliation Modes

### 1) Config reload path (automatic)

If `compose.yaml` did **not** change, the workflow SSHes into the deploy host and runs:

1. `git pull --ff-only origin main`
2. `curl -X POST http://localhost:9090/-/reload` (Prometheus config reload)
3. `SIGHUP` to Alloy (triggers Alloy config reload)
4. `./scripts/wait-healthy.sh`

### 2) Compose restart path (manual approval required)

If `compose.yaml` changed, the workflow uses job `deploy-compose-restart` with environment
`compose-restart` and requires reviewer approval via GitHub Environment protection rules.

After approval, it SSHes into the deploy host and runs:

1. `git pull --ff-only origin main`
2. `make up` (includes `check-env.sh`)
3. `./scripts/wait-healthy.sh`

## Required Secrets and Variables

Configure in **GitHub → Settings → Secrets and variables → Actions**:

### Required secrets

- `DEPLOY_HOST`: SSH host (IP or DNS)
- `DEPLOY_USER`: SSH username
- `DEPLOY_KEY`: private SSH key (PEM/OpenSSH)

If any required secret is missing, the workflow exits with an explicit error.

### Optional repository variable

- `DEPLOY_PATH`: absolute path of the uFawkesObs clone on the target host  
  Default if unset: `$HOME/<repo-name>`

### Optional secret (recommended)

- `DEPLOY_HOST_KEY`: full host key line for `known_hosts` (for example:
  `deploy.example.com ssh-ed25519 AAAAC3...`)  
  If unset, the workflow falls back to `ssh-keyscan` (TOFU behavior).

## Commit Audit Summary

Each run posts a commit comment to the triggering SHA with:

- reconciliation mode (`config-reload` or `compose-restart`)
- services reloaded/restarted
- health check result
- workflow run URL

This provides an auditable Git → runtime reconciliation record on each deployed commit.
