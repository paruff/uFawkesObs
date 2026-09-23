# Prepare for Public Release — uFawkesObs

> Feeds into the H2 horizon in [`../MILESTONES.md`](../MILESTONES.md), alongside
> [`PATH_TO_LATE_BETA.md`](PATH_TO_LATE_BETA.md). Late beta is about a small
> team relying on this for real; this doc is about a stranger cloning it
> without a maintainer in the room. Update status as issues close.

## Where This Sits

`docs/PATH_TO_LATE_BETA.md` tracks whether a 3–15 person team that already
trusts the maintainers can run this for real. Public release adds a
different bar: the person cloning it has no relationship with the project,
may run it on a host reachable from the internet, and has no one to ask
before something leaks. Late beta and public release can complete in either
order, but **both gate a public announcement** — shipping public-facing
docs/marketing while either has open blockers below is not recommended.

## Blockers (must fix before any public "clone and run" announcement)

| ID | Finding | Issue | Evidence |
|----|---------|-------|----------|
| PR-01 | Grafana ships with `[auth.anonymous] enabled = true` in the checked-in `config/grafana/grafana.ini`. Anyone who can reach port 3000 reads every dashboard — metrics, logs, traces — with **zero credentials**. Setting a strong `GRAFANA_ADMIN_PASSWORD` does not close this; it's a separate always-on bypass. Live-confirmed 2026-09-23 against `make up` with the repo's own `.env` defaults (`curl http://localhost:3000/api/search` returned the full dashboard list, unauthenticated). | [#380](https://github.com/paruff/uFawkesObs/issues/380) | `config/grafana/grafana.ini`, live curl output in the issue |
| PR-02 | GitOps deploy to `main` is currently broken — the last two `deploy.yml` runs (2026-09-18) failed on `Host key verification failed` (remote host identification changed). Nothing alerts on this failure mode, so it went unnoticed for days. Whatever is on the live deploy host right now predates the current `main`. | [#381](https://github.com/paruff/uFawkesObs/issues/381) | `gh run view` failed-job log |
| PR-03 | LB-02 is recorded DONE but only 6 of 14 published ports are actually localhost-bound; Alloy's unauthenticated UI (12345), node-exporter (9100, host-level metrics), and the Jaeger/Zipkin/gRPC receivers are open on `0.0.0.0` by default. Needs a port-by-port keep/restrict decision (requires PM sign-off per AGENTS.md §5 — exposed ports are a "must ask" change). | [#335](https://github.com/paruff/uFawkesObs/issues/335) | Issue body has the full port matrix |
| PR-04 | Rollback has never been exercised against a real deploy target — `DEPLOY_PATH` still points at a maintainer workstation, not the sandbox host the runbook requires. A stranger's first production incident would be the first real test of the rollback path. | [#182](https://github.com/paruff/uFawkesObs/issues/182) | `docs/ROLLBACK_DRILL.md` precondition 0 |

## High-Value Fixes (don't block release, meaningfully reduce first-contact risk)

| Finding | Issue / Note |
|---|---|
| `docker compose up` (without `make up`) skips `scripts/check-env.sh`, so the default-credentials guard is opt-in, not structural. Making `GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:?set in .env}` in `compose.yaml` would make Compose itself refuse to start without a password, independent of which entry point someone uses. | Not yet filed — raise with PM sign-off, since it changes startup behavior per AGENTS.md §5. |
| DORA ingestion API (`dora-api`, port 8088) accepts unauthenticated requests when `DORA_API_KEY` is unset (`dora/ingestion/api/auth.py`). Currently only reachable on localhost, so this is contingent on PR-03's port decision holding. | Tracked implicitly by #335; call out explicitly if 8088 binding ever changes. |
| README is 602 lines — a stranger's first read, not a reference doc. | [#345](https://github.com/paruff/uFawkesObs/issues/345) |
| No coverage measurement despite an 80% mandate in this repo's own testing rule. | [#343](https://github.com/paruff/uFawkesObs/issues/343) |
| Chaos nightly hasn't run since 2026-08-28 (~4 weeks) — worth confirming the schedule trigger still fires before calling the pipeline stable. | Not yet filed — verify trigger config first; may be a non-issue if intentionally paused. |

## Already Resolved (verified, not re-tracked)

- Rollback job's inability to push its revert to `main` (`GITHUB_TOKEN` permissions + missing checkout) — fixed, [#193](https://github.com/paruff/uFawkesObs/issues/193) closed 2026-08-19.
- LB-01, LB-03, LB-05, LB-06 — see `docs/PATH_TO_LATE_BETA.md` for detail; those hold up under this review.

## Local Verification Method

The findings above marked "live-confirmed" were checked against a real running stack, not inferred from config alone:

```bash
make up                                    # starts core profile with repo .env
docker compose ps --format '{{.Name}}\t{{.Ports}}'   # actual bound ports, not just compose.yaml intent
curl -s http://localhost:3000/api/search   # anonymous-access probe
make down
```

This is the same method to use for re-verifying PR-01/PR-03 once fixed — a
static read of `compose.yaml` or `grafana.ini` isn't sufficient evidence
that a port is actually closed or auth is actually enforced, because
Grafana's ini and Compose's env defaults can each override the other
silently (see PR-01: the admin password was correctly set and still didn't
matter).

## Exit Criteria

Public release readiness is reached when PR-01 through PR-04 are closed and
this doc's status header reflects that. At that point this can be linked
from the same beta feedback channel LB-06 set up
([discussion #242](https://github.com/paruff/uFawkesObs/discussions/242))
before any wider announcement.
