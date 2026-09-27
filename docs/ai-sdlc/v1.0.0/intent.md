# Intent: uFawkesObs v1.0.0

**Owner:** @paruff | **Created:** 2026-09-27 | **Status:** Draft
**Chain:** `intent.md` → [`spec.md`](spec.md) → [`plan.md`](plan.md)
**Suite plan:** [uFawkes.dev `docs/ai-sdlc/suite-release/`](https://github.com/paruff/uFawkes.dev/tree/main/docs/ai-sdlc/suite-release)
**Live status:** [uFawkes Suite Release Project](https://github.com/users/paruff/projects/7), Release = "Obs 1.0"

## Problem

uFawkesObs has shipped betas up to `v0.4.2-beta.1`, and none of them
promises anything. A team evaluating it can't tell what will stay stable
when they upgrade, and there's no stated line between a fix and a break.
That blocks the adoption goal in [`VISION.md`](../../../VISION.md): small
teams running their own observability stack need to know an upgrade won't
break their setup.

## Goal

Ship `v1.0.0`, the first stable release, with a written public contract.
Announce it on LinkedIn, ufawkes.dev, and dev.to. Anyone reading the
announcement should find docs that match what they install.

## Decisions (from @paruff, 2026-09-27)

- **Contract scope:** semver covers compose service names, published ports,
  and documented `.env.example` variables. A breaking change to any of
  these needs a major version. Grafana datasource UIDs, dashboard UIDs, and
  DORA metric names are **not** covered; they may change in a minor
  release if the release notes say so.
- **Announcement:** run the uFawkesAI `release` agent after the release
  exists. It drafts the GitHub Release, the ufawkes.dev page update, and
  the dev.to and LinkedIn posts.
- **Adoption measure:** GitHub stars and forks, plus issues and PRs from
  anyone other than @paruff. The post-release `measure:` issue tracks both.
- **Mechanics stay as they are:** release-please's standing release PR,
  merged by a human (`docs/RELEASE_PROCESS.md`). Agents never merge.

## What 1.0 does *not* prove

The riskiest assumption in `VISION.md` is still untested: whether a 3–15
person team will accept operating its own stack. Only the onboarding-speed
sub-claim has been validated (93s). 1.0 is a stability promise, not
evidence that the assumption holds. The adoption measure above is the
first real signal.

## Open questions

1. **Target date.** Until one is set, the release is gate-driven.
2. **Are Makefile targets and compose profile names part of the
   contract?** Today they aren't. But the README and Dojo labs call
   `make init`, `make up`, and `make up-dora`, and select profiles by
   name (`core`, `dora`, `apps`, `notifications`). Leaving them out means
   renaming one is a "minor" change that still breaks every tutorial.
3. **Which v1.0.0 milestone candidates block the release.** #381 is already
   labeled `release-blocker`. #469, #470, #473, #393, and #182 are
   candidates, and deciding which of them block is your call.
