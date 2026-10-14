# RG-1 Clean-Install Verification — Transcript (Linux, 2026-10-14)

Issue: #601 / #494 (RG-1). Spec: REL-02 (`docs/ai-sdlc/v1.0.0/spec.md`).
Evidence for this run: [`rg1-2026-10-14-linux/`](rg1-2026-10-14-linux/) (paths relative to `docs/notes/`).
Companion to the [macOS transcript](rg1-clean-install-transcript-2026-09-30-macos.md).

## Environment

| Fact | Value |
|---|---|
| Host | Ubuntu 24.04.4 LTS (x86_64), a fresh Lima/QEMU VM on an Intel Mac, 4 vCPU, 6 GiB RAM, no host mounts |
| Runtime | Docker 29.1.3 (`docker.io`), Compose 2.40.3 (`docker-compose-v2`), GNU Make 4.3, git 2.43.0, all from Ubuntu's apt |
| Prerequisites | Installed from apt first, per the README's prerequisite line; not timed |
| Under test | fresh `git clone` of `origin/main` @ `16d98e7b54263228b556f546cfe97d5f1738c101` (includes #636, #637, #638) |
| Image cache | **Cold.** The first `make up` pulled every image. |
| Caveat | A VM on a Mac, not bare metal or a cloud host. It is a real Linux kernel and Docker daemon, but x86_64 only. |

## Result

**REL-02 fails on Linux as the README is written; it passes once the printed `chown` step is applied.**

| Step | Outcome | Evidence |
|---|---|---|
| README as written: `make init && make up` | **Fails.** `make up` exits 2 (`dependency failed to start: container loki is unhealthy`). Prometheus, Loki and Tempo crash-loop with `permission denied` creating `/loki/rules`, `/var/tempo/wal`, and the Prometheus query log. | [`01-install.log`](rg1-2026-10-14-linux/01-install.log), [`01-health.txt`](rg1-2026-10-14-linux/01-health.txt) |
| Apply the `chown` commands `make init` prints, then `make up` | **Passes.** All core services healthy; `wait-healthy.sh` reports "All core services are healthy (16s)". | [`02-up-after-chown.log`](rg1-2026-10-14-linux/02-up-after-chown.log), [`02-health.txt`](rg1-2026-10-14-linux/02-health.txt) |

Timeline (UTC): clone done and `.env` set 17:14:11; first attempt failed 17:17:16 (includes the cold image pull); `chown` applied and `make up` started 17:17:54; healthy 17:18:34. About 4m23s from start to healthy including the failed attempt; the fixed path itself took 40 s once images were present. Both are well inside the 15-minute budget.

## Root cause

`make init` creates `data/*` as `755`, owned by the host user. The services run as non-root container users (Grafana 472, Prometheus and Alertmanager 65534, Loki and Tempo 10001), so they cannot write there on Linux. Docker Desktop and colima on macOS map ownership permissively, so the macOS run never saw it. `make init` already prints the correct `chown` commands, but the README Quick Start did not mention them. CI hides the same issue with `chmod -R 777 data/`.

Fix: README Quick Start now shows the Linux `chown` step (this PR). Not done here: making `make init` apply the `chown` itself (needs `sudo`; a design call).

## Signals visible (queried through Grafana's provisioned datasources)

| Signal | Check | Result |
|---|---|---|
| Metrics | `count(up==1)`; `count({__name__=~".+"})` via the `prometheus` datasource | 10 targets up; 8,031 series |
| Logs | Loki `query_range` `{job=~".+"}`, last 10 min | success, 2 streams |
| Traces | Tempo `/api/search` | traces with `rootServiceName=telemetry-generator`, `GET /generate` |

Grafana `/api/health`: 200. Datasources: `alertmanager`, `loki`, `prometheus`, `tempo`.

## Not covered

- Only the `core` profile plus the always-on `telemetry-generator`; no `dora`, `notifications` or `apps` profile run.
- Not a bare-metal or cloud host, and not arm64.
- Acceptance, unit and integration suites were not re-run on Linux; CI covers them on `ubuntu-24.04`.
