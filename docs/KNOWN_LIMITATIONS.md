# Known Limitations — uFawkesObs

> Check this before reporting a bug. These are known issues that are not bugs in uFawkesObs itself.
> Update this file when a new limitation is confirmed or a workaround is found.

---

## Security & Authentication

### No TLS Between Internal Services

**Limitation:** All communication between services (OTEL Collector → Tempo, Alloy → Loki, etc.)
uses plaintext HTTP/gRPC with `insecure: true`. This is intentional for a local development setup.

**Impact:** Not suitable for production without adding mutual TLS.

**Workaround:** For production, add TLS certificates and update all exporter/endpoint configs
in `config/otel/collector.yaml`, `config/alloy/config.river`, and Grafana datasource URLs.

---

### No Authentication on Loki, Tempo, Prometheus, Alertmanager

**Limitation:** These backends still accept unauthenticated requests.
By default, `compose.yaml` now binds their HTTP ports to localhost only:

- Tempo: `127.0.0.1:3200:3200`
- Loki: `127.0.0.1:3100:3100`
- Prometheus: `127.0.0.1:9090:9090`
- Alertmanager: `127.0.0.1:9093:9093`

**Impact:** Default localhost-only bindings reduce accidental exposure on shared/cloud hosts.
If you re-expose these ports to `0.0.0.0`, anyone with network access can read or write
telemetry/alerting data unless you add access controls.

**Workaround / Opt-out path:** Only re-expose when intentionally needed, and place a reverse
proxy with authentication in front (for example OAuth2/OIDC, basic auth, or mTLS). Prefer a
Compose override file instead of editing the default:

```yaml
# compose.remote-access.override.yaml
services:
  tempo:
    ports:
      - "0.0.0.0:3200:3200"
  loki:
    ports:
      - "0.0.0.0:3100:3100"
  prometheus:
    ports:
      - "0.0.0.0:9090:9090"
  alertmanager:
    ports:
      - "0.0.0.0:9093:9093"
```

```bash
docker compose -f compose.yaml -f compose.remote-access.override.yaml --profile core up -d
```

Also enable service-level auth where available (for example `auth_enabled: true` in
`config/loki/loki.yaml` for multi-tenant Loki setups).

---

### No Authentication on DORA Ingestion API by Default

**Limitation:** `dora-api`'s `/event` and `/event/batch` endpoints only enforce
the `Authorization: Bearer <DORA_API_KEY>` header when `DORA_API_KEY` is set in
`.env` — unset (the default) leaves ingestion open to anything that can reach
`http://localhost:8088` (see `dora/ingestion/api/auth.py`). Mitigated by the
same localhost-only binding as the other backends (`127.0.0.1:8088:8088` in
`compose.yaml`), but it's a real gap if that port is ever re-exposed the way
the section above describes for Loki/Tempo/Prometheus/Alertmanager.

**Impact:** On a shared host, or if the port is re-exposed, anyone who can
reach it can submit fabricated deployment/incident/PR/rework events, skewing
DORA metrics.

**Workaround / Opt-out path:** Set `DORA_API_KEY` in `.env` — it's supported
today, just not required. There is no fail-fast check enforcing it (unlike
`GRAFANA_ADMIN_PASSWORD`, which `scripts/check-env.sh` refuses to start
without); making it required-by-default would be a breaking change for
existing deployments and hasn't been made yet.

---

## Data Storage

### Local Filesystem Storage Only

**Limitation:** All persistent data (metrics, traces, logs) is stored on the local filesystem
under `./data/`. There is no object storage backend configured.

**Impact:**

- Data is lost if the host disk fails
- No horizontal scaling
- Tempo local storage is limited by disk capacity

**Workaround:** For production, configure object storage (S3, GCS) in each service's config.

---

### Tempo Storage Quota

**Limitation:** Tempo is configured with local storage. There is no automatic size limit on
trace storage beyond the host disk capacity.

**Impact:** Long-running deployments may fill the disk.

**Workaround:** Monitor `./data/tempo` disk usage. Set `max_block_bytes` in
`config/tempo/tempo.yaml` to limit storage.

---

## Operational

### Directory Permissions Require UID Alignment

**Limitation:** Container processes run as specific non-root UIDs (Grafana: 472,
Prometheus/Alertmanager: 65534, Loki/Tempo: 10001) that differ from the host user.
On Linux, the host-side `data/` directories must be owned by those UIDs for
containers to write persistent data.

**Impact:** First-time setup requires an extra step on Linux hosts.

**Workaround:** Run `make init` to create directories with `755` permissions. On Linux,
follow the printed `chown` commands to assign correct ownership. On Docker Desktop
(macOS/Windows) `make init` alone is sufficient.

`chmod -R 777 data/` is a last-resort workaround for localhost machines only and
should never be used in shared or networked environments. See
[docs/production-hardening.md](production-hardening.md) for details.

---

### Single-Node Deployment Only

**Limitation:** `compose.yaml` deploys all services on a single Docker host. There is no
built-in support for distributing services across multiple nodes.

**Impact:** No high-availability for any individual service.

**Workaround:** For HA, migrate to Kubernetes or use managed cloud observability services.

---

## Alloy (Log Collection)

### Docker Socket Access Required

**Limitation:** Alloy requires read access to `/var/run/docker.sock` to discover and collect
container logs. On some Docker Desktop configurations, the socket path may differ.

**Impact:** Alloy may fail to start or collect no logs if the socket is not accessible.

**Workaround:** Verify that `/var/run/docker.sock` exists on the host. On macOS with Docker
Desktop, the socket may be at `/var/run/docker.sock` via a symlink. Check
`docker compose logs alloy` for permission errors.

---

### Alloy Positions File

**Limitation:** Alloy tracks log read positions in `/var/lib/alloy/positions.yaml` (persisted
in `./data/alloy`). If the positions file is deleted or corrupted, Alloy will re-read all
container logs from the beginning.

**Impact:** Duplicate log entries in Loki after an Alloy data directory reset.

**Workaround:** This resolves itself after the log retention period. To prevent: do not
delete `./data/alloy` while containers are running.

---

## Grafana

### Default Credentials

**Limitation:** `compose.yaml` falls back to `admin`/`admin` when
`GRAFANA_ADMIN_PASSWORD` is unset. The `make up` family of targets blocks this:
`scripts/check-env.sh` refuses to start when the password is empty, `admin`,
`changeme`, or still a `REPLACE_ME*` placeholder. Starting the stack with a raw
`docker compose --profile core up -d` bypasses that guard entirely and applies
the weak default.

**Impact:** Anyone who can reach port 3000 — which is published on all
interfaces, not just localhost — can log in as admin on a stack started outside
`make up`.

**Workaround:** Set `GRAFANA_ADMIN_PASSWORD` in `.env` before first run and
start the stack with `make up` (or `up-apps` / `up-dora` / `up-full`), never a
bare `docker compose up`. The `.env` file is gitignored and will not be
committed.

**Note:** until 2026-09-02 the guard's rejection list held only
`REPLACE_ME_set_a_real_password_here` while `.env.example` shipped
`REPLACE_ME`, so `cp .env.example .env` passed the check and produced an admin
password that is public in this repository. Anyone who ran the stack before
that fix should rotate the Grafana admin password.

---

### Duplicate Dashboard Provisioning Path (Legacy Provider)

**Limitation:** Two Grafana dashboard provisioning mechanisms run side by side:
`config/grafana/provisioning/dashboards/new-dashboards.yaml` provisions
`dashboards/platform/` and `dashboards/services/` (the structure AGENTS.md §4
mandates), while `config/grafana/provisioning/dashboards/dashboards.yaml` — a
provider literally named `"legacy"` — separately provisions 8 JSON files from
`config/grafana/dashboards/` into an "Application" folder. The legacy
provisioner was deliberately restored after an earlier attempt to remove it
(commit `9df6428`), so it is live, not dead code — but it means dashboard
JSON lives in two directories under two different conventions (UID naming,
`dashboards/` layout) instead of one.

**Impact:** Contributors adding a dashboard must know which of the two
mechanisms applies; the "Application" folder's dashboards don't follow the
`ufawkesobs-<slug>` UID convention AGENTS.md §4 requires for platform
dashboards.

**Workaround:** None yet. Consolidating `config/grafana/dashboards/*.json`
into `dashboards/platform/` or `dashboards/services/` (renaming UIDs to the
`ufawkesobs-<slug>` convention and updating any cross-dashboard links) and
removing the legacy provisioner is tracked as follow-up work, not yet
scheduled.

---

### Dashboard UIDs Must Be Stable

**Limitation:** Cross-dashboard links use UIDs. If a dashboard is re-imported with a
different UID, those links will break.

**Impact:** Broken "Open in" links between dashboards.

**Workaround:** Always export dashboards from Grafana UI and keep the `uid` field set to a
stable value in the JSON. Never let Grafana auto-generate UIDs.

---

## Prometheus

### 30-Day Retention Only

**Limitation:** Prometheus is configured with `--storage.tsdb.retention.time=30d`. Metrics
older than 30 days are automatically deleted.

**Impact:** No long-term metrics history beyond 30 days.

**Workaround:** Enable remote-write to a long-term storage backend (Thanos, Cortex, Mimir),
or increase `--storage.tsdb.retention.time` (requires more disk).

---

## Alertmanager

### Webhook Receiver Only (No Email/Slack/Discord Enabled by Default)

**Limitation:** The default `config/alertmanager/alertmanager.yml` uses a webhook receiver
for testing. No email, Slack, or Discord integration is enabled out of the box
(the recipes are present but commented out, and the Discord bridge is gated
behind the `notifications` profile).

**Impact:** Alerts are not sent to a human notification channel by default.

**Workaround:** Enable the tested Slack or Discord recipes documented in
[`docs/alertmanager-operations.md`](alertmanager-operations.md) — set
`SLACK_WEBHOOK_URL` and/or `DISCORD_WEBHOOK_URL` in `.env`, uncomment the
receiver/route, and (for Discord) start the bridge with
`docker compose --profile core --profile notifications up -d`.
See [Alertmanager docs](https://prometheus.io/docs/alerting/latest/configuration/).

---

## Telemetry Generator (`apps` profile)

### Demo Application Only

**Limitation:** The `telemetry-generator` service (`apps` profile) is a demo application
for testing the telemetry pipeline. It is not intended for production use.

**Impact:** Do not rely on it for production telemetry.

**Workaround:** Replace with your own instrumented application. See
`apps/telemetry-generator/README.md` for the telemetry patterns it uses.
