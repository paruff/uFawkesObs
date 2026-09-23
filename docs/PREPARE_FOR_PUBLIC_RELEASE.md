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
| ~~PR-01~~ | ✅ **FIXED** — `config/grafana/grafana.ini`'s `[auth.anonymous] enabled` changed to `false`. Live-reverified after the fix: `curl http://localhost:3000/api/org` now returns 401, real credentials still return 200. | [#380](https://github.com/paruff/uFawkesObs/issues/380), PR #387 (merged) | `config/grafana/grafana.ini` |
| PR-02 | **Still blocked — cannot be fixed remotely, and it's worse than first thought.** Pulled the actual fingerprint from all 4 failed `deploy.yml` runs: **four different fingerprints across four attempts**, including two 6 minutes apart on the same day. This is not a one-time host rebuild. Two explanations, both need the maintainer's direct access to the host to resolve: (1) the deploy target's SSH host keys aren't persisted across restarts (benign but needs fixing at the host), or (2) `DEPLOY_HOST` resolves to a genuinely different machine each time. **Do not re-pin `DEPLOY_HOST_KEY` to silence this without confirming which explanation is true** — that's exactly the failure mode strict host-key checking exists to catch. | [#381](https://github.com/paruff/uFawkesObs/issues/381) | 4-fingerprint table posted to the issue 2026-09-23 |
| ~~PR-03~~ | ✅ **FIXED** (PM sign-off given 2026-09-23) — applied #335's own recommendation as-is. `8888`/`8889`/`9095`/`9096`/`9100`/`12345`/`14250`/`14268`/`9411` now bind to `127.0.0.1`; `3000` (Grafana UI) and `4317`/`4318` (OTLP ingest) stay public by design. Live-reverified: `docker compose ps` shows every changed port as `127.0.0.1:*`, `./scripts/wait-healthy.sh` still passes. | [#335](https://github.com/paruff/uFawkesObs/issues/335), PR #389 | `compose.yaml`, `docs/ARCHITECTURE.md` |
| PR-04 | **Still blocked — needs real infrastructure, not code.** Rollback has never been exercised against a real deploy target; `DEPLOY_PATH` still points at a maintainer workstation. This directly connects to PR-02's finding: a personal workstation's SSH identity is far less stable than a dedicated sandbox host, which may itself be *why* PR-02 keeps changing. Provisioning a real, always-on sandbox host is the actual unblock here — nothing I can do without one. | [#182](https://github.com/paruff/uFawkesObs/issues/182) | `docs/ROLLBACK_DRILL.md` precondition 0 |

## High-Value Fixes (don't block release, meaningfully reduce first-contact risk)

| Finding | Issue / Note |
|---|---|
| `docker compose up` (without `make up`) skips `scripts/check-env.sh`, so the default-credentials guard is opt-in, not structural. Making `GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:?set in .env}` in `compose.yaml` would make Compose itself refuse to start without a password, independent of which entry point someone uses. | **Awaiting PM sign-off** (AGENTS.md §5 — changing an env var default/startup behavior is a "must ask" change). Not yet filed as an issue. |
| DORA ingestion API (`dora-api`, port 8088) accepts unauthenticated requests when `DORA_API_KEY` is unset (`dora/ingestion/api/auth.py`). Currently only reachable on localhost, so this is contingent on PR-03's port decision holding. | Tracked implicitly by #335; call out explicitly if 8088 binding ever changes. |
| ~~README is 602 lines — a stranger's first read, not a reference doc.~~ | ✅ **DONE** — [#345](https://github.com/paruff/uFawkesObs/issues/345), PR #384. README is now 107 lines; detail moved to `docs/ARCHITECTURE.md`, new `docs/TROUBLESHOOTING.md`, and new `tests/acceptance/README.md`, not deleted. |
| ~~No coverage measurement despite an 80% mandate in this repo's own testing rule.~~ | ✅ **DONE** — [#343](https://github.com/paruff/uFawkesObs/issues/343), PR #382. The fix existed once already (commit `8af8619`) but was silently stranded — pushed to a branch *after* its PR (#362) had already merged, so it never reached `main` despite that PR claiming "Closes #343." Recovered via cherry-pick and verified: 595 unit tests pass, 75% coverage on `dora/`. See [#383](https://github.com/paruff/uFawkesObs/issues/383) for a related portability bug found while verifying this. |
| ~~Chaos nightly hasn't run since 2026-08-28 (~4 weeks)~~ | **False alarm, corrected 2026-09-23** — re-checked directly by workflow ID rather than the branch-filtered run list used originally: it has run successfully every night through today. No action needed. |

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
