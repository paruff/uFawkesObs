# Quick Start Walkthrough

A line-by-line companion to the [README Quick Start](../README.md#quick-start),
written for someone who has never run this repo before. Each step shows the
command, what it does, what you should see, and where to go if you don't.
Every timing quoted here comes from the measured clean-install run in
[RG-1 (#494)](https://github.com/paruff/uFawkesObs/issues/494) — macOS 15.8,
colima, warm image cache. Expect longer first boots on a cold cache: image
pulls are not included in those numbers.

If a step fails and this page doesn't cover it, that's a gap — please
[file an issue](https://github.com/paruff/uFawkesObs/issues/new/choose)
so the next reader doesn't hit it too.

---

## Step 0 — Check your prerequisites

| Check | Command | What you need |
|---|---|---|
| Docker Engine | `docker version` | 20.10+ (Client **and** Server lines both print) |
| Docker Compose | `docker compose version` | v2.0+ |
| make | `make --version` | any GNU Make (macOS ships it with the Xcode Command Line Tools) |
| git | `git --version` | any |
| Free RAM | — | ~4 GB free while the stack runs |
| Ports | — | 3000, 9090, 9093, 3100, 3200, 4317, 4318, 9100, 12345 free |

Full port/credential table:
[docs/ARCHITECTURE.md — Ports & Access](ARCHITECTURE.md#ports--access).

No Docker yet? Docker Desktop (macOS/Windows) or engine + Compose plugin
(Linux) both work; the RG-1 run used [colima](https://github.com/abiosoft/colima).

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/paruff/uFawkesObs.git
cd uFawkesObs
```

Expected: standard git clone output, ending in `warning: ...` or silence.
You are now in the repo root — every command below runs from there.

---

## Step 2 — Create your `.env`

```bash
cp .env.example .env
$EDITOR .env
```

Two variables matter to the Quick Start:

| Variable | Purpose | Default in `.env.example` |
|---|---|---|
| `GRAFANA_ADMIN_USER` | Grafana login user | `admin` |
| `GRAFANA_ADMIN_PASSWORD` | Grafana login password | `REPLACE_ME` — **you must change this** |

`make up` refuses to start while the password is still a placeholder. If you
skip this step you get exactly this, not a cryptic failure later:

```
❌ Refusing to start: GRAFANA_ADMIN_PASSWORD is missing or insecure.
Set a non-default Grafana admin password before starting the stack.
```

(`scripts/check-env.sh` enforces this; the other `.env` values — DORA,
Slack/Discord webhooks — are optional for the core stack.)

---

## Step 3 — Create the data directories

```bash
make init
```

What it does: creates `data/{grafana,prometheus,alertmanager,loki,tempo,alloy}`
(mode 755) and `data/dora` (mode 777 — SQLite file, see
[ADR-007](adr/ADR-007-dora-consolidation.md)).

Expected output ends with:

```
✅ data/ directories ready
```

On **Linux**, also run the `chown` commands `make init` prints if containers
later complain about permissions — container UIDs differ from your user.
On macOS with Docker Desktop/colima the clone lives under your home directory
and the chown step is normally not needed.

---

## Step 4 — Start the stack

```bash
make up
```

What it does: `docker compose --profile core --profile apps up -d` — the
core observability stack plus the demo `telemetry-generator` app that emits
metrics, logs, and traces.

- **First boot pulls images** and can take several minutes on a cold cache.
  The RG-1 run measured **42 s total** (init → healthy) against an already
  warm image cache.
- Check progress with `docker compose ps`. The app comes up alongside the
  core services and is the source of the live traces/logs/metrics you see in
  Grafana; **otel-collector and tempo deliberately have no compose
  healthcheck** (distroless images) — the next step probes them over HTTP
  instead, so their blank health column is not a failure.

---

## Step 5 — Wait until everything is healthy

```bash
./scripts/wait-healthy.sh
```

Probes all seven HTTP endpoints (Prometheus, Grafana, Loki, Tempo, Alloy,
OTel Collector, Alertmanager) and exits 0 when they all answer. Typical
result: green on the first pass in ~15 s, Tempo the slowest (~17 s).

- Stuck? The default timeout is 120 s — raise it with
  `WAIT_TIMEOUT=300 ./scripts/wait-healthy.sh`.
- A service that never comes up: `docker compose logs <service>` —
  permission errors under `./data/` are the most common cause (re-run
  `make init`, see Step 3).

---

## Step 6 — Open Grafana

Open <http://localhost:3000> and log in with the `GRAFANA_ADMIN_USER` /
`GRAFANA_ADMIN_PASSWORD` you set in Step 2. Datasources (Prometheus, Loki,
Tempo, Alertmanager) are pre-provisioned — there is nothing to configure.

---

## Step 7 — Prove the three signals

| Signal | Where | Query / action | Expect |
|---|---|---|---|
| Metrics | Grafana → Explore → **Prometheus** | `up` | One series per scraped target, all value `1` |
| Logs | Grafana → Explore → **Loki** | `{compose_project!=""}` | Streams from the stack's own containers (project label is your directory name lowercased, e.g. `ufawkesobs`) |
| Traces | Grafana → Explore → **Tempo** | start the generator first (below) | A waterfall for a generator request trace |

The default `make up` already starts the demo app, so you don't need to add a
second step. If you later stop it, bring it back with:

```bash
docker compose --profile apps up -d telemetry-generator
```

Then wait ~30 s, generate some traffic through it, and search Tempo for
`telemetry-generator` traces. When you're done, stop it with:

```bash
docker compose --profile apps stop telemetry-generator
```

---

## The profiles, in one place

| Command | Profiles started | What you get |
|---|---|---|
| `make up` | `core` + `apps` | The default quick-start stack: observability services plus the demo telemetry generator for live metrics/logs/traces |
| `make up-apps` | `core` + `apps` | Explicit app-profile helper for the same stack; use it when you want the app profile by name, but `make up` remains the recommended default |
| `make up-dora` | `core` + `dora` | + DORA metrics API (self-contained, SQLite-only — no external database) |
| `make up-full` | `core` + `apps` + `dora` | Everything the full acceptance suite expects |

Details: [ARCHITECTURE.md — Profiles](ARCHITECTURE.md#profiles).

---

## Stop and clean up

```bash
docker compose down              # stop, keep data
docker compose down -v           # stop, remove volumes
rm -rf data/prometheus/* data/grafana/* data/tempo/* data/loki/* \
       data/alertmanager/* data/alloy/*
make init                        # recreate empty data dirs
```

---

## When something goes wrong

| Symptom | First move |
|---|---|
| A container is `unhealthy` or restarting | `docker compose logs <service>` |
| Permission errors on `./data/` | Re-run `make init`; on Linux apply the printed `chown` |
| Port already allocated | Free the port or see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| `wait-healthy.sh` times out | `WAIT_TIMEOUT=300 ./scripts/wait-healthy.sh`, then check logs |
| Something worked yesterday, not today | [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) |

More: [TROUBLESHOOTING.md](TROUBLESHOOTING.md). Still stuck? Ask in
[GitHub Discussions](https://github.com/paruff/uFawkesObs/discussions) or the
[Beta Feedback thread](https://github.com/paruff/uFawkesObs/discussions/242) —
one sentence about what you hit is enough, and it becomes a new issue.

---

## Where to go next

- [DAY_ONE.md](DAY_ONE.md) — your first 30 minutes: what started, what to click
- [ARCHITECTURE.md](ARCHITECTURE.md) — how the services connect
- [production-hardening.md](production-hardening.md) — before exposing anything beyond localhost
- [CONTRIBUTING.md](../CONTRIBUTING.md) — reporting bugs and sending changes
