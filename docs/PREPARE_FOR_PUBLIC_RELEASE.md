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

> **Live status lives in [`../EXECUTION_QUEUE.md`](../EXECUTION_QUEUE.md) now**
> — this table used to carry its own status and drifted from the queue. This
> defines *what each blocker is*; go to the queue for *is it done* and the
> exact unblock steps for PR-02/PR-04.

| ID | Finding | Issue |
|----|---------|-------|
| PR-01 | Grafana's `[auth.anonymous]` must default to `false` — anyone reaching port 3000 could otherwise read every dashboard with zero credentials. | [#380](https://github.com/paruff/uFawkesObs/issues/380) |
| PR-02 | GitOps deploy must connect reliably — the deploy host's presented SSH identity must be stable and verified, not silently re-trusted on every mismatch. | [#381](https://github.com/paruff/uFawkesObs/issues/381) |
| PR-03 | Only ports meant to be public should be published on all interfaces; internal/scrape-only ports must bind to localhost. | [#335](https://github.com/paruff/uFawkesObs/issues/335) |
| PR-04 | Rollback must be proven against a real deploy target, not just documented. | [#182](https://github.com/paruff/uFawkesObs/issues/182) |

## High-Value Fixes (don't block release, meaningfully reduce first-contact risk)

> Tracked in [`../EXECUTION_QUEUE.md`](../EXECUTION_QUEUE.md) P2 section, not
> here.

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
