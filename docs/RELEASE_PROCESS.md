# Release Process

Automated via [release-please](https://github.com/googleapis/release-please)
(issue [#264](https://github.com/paruff/uFawkesObs/issues/264)). This
replaces the fully-manual process that produced only 1 release in the 13
days between v0.2.0 and v0.3.0-alpha.1 despite continuous merges.

## How it works

1. Every time `Acceptance Full (Post-Merge)` passes on `main` — the same
   gate `deploy.yml` uses to decide whether to reconcile — `.github/workflows/release-please.yml`
   runs `googleapis/release-please-action`.
2. It scans [Conventional Commits](./PR_STANDARD.md) since the last
   release and maintains a **standing "release PR"** proposing the next
   version bump and CHANGELOG entry. It updates that same PR on every
   subsequent qualifying merge rather than opening a new one each time.
3. **Nothing is released automatically.** A human reviews and merges the
   release PR when ready. On the next `Acceptance Full` pass after that
   merge, release-please detects it and creates the actual git tag +
   GitHub Release.

This is deliberately *not* "release on every merge" — trivial changes
(a typo fix, a comment) don't force a version bump on their own; they
just accumulate in the standing PR until someone decides to cut it.

## Required setup: `RELEASE_PLEASE_TOKEN`

Two real issues were found and fixed live (2026-08-31) while diagnosing a
failing `Release Please` run:

1. **"GitHub Actions is not permitted to create or approve pull
   requests."** — the repo's Settings → Actions → General → Workflow
   permissions had "Allow GitHub Actions to create and approve pull
   requests" disabled. Fixed via the repo's Actions permissions API
   (`can_approve_pull_request_reviews: true`) — this only needed doing
   once, not a recurring setup step.
2. **The release PR never gets its required checks to run.** GitHub
   suppresses `pull_request`-triggered workflows for PRs opened/updated
   with the default `GITHUB_TOKEN` (anti-recursion protection) —
   confirmed live: the release PR sat with zero of `Pre-commit Hooks`,
   `Security`, `Unit Tests`, etc. ever starting, so it could never
   satisfy the required-status-checks ruleset and would stay permanently
   unmergeable. A Personal Access Token isn't subject to this
   restriction.

**To fix #2** (one-time, human action — cannot be done via API):

1. Create a **fine-grained PAT** scoped to this repo only:
   GitHub → Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token.
   - Repository access: **Only select repositories** → `paruff/uFawkesObs`
   - Permissions: **Contents: Read and write**, **Pull requests: Read and write**
   - Expiration: set a reminder to rotate it before it expires (fine-grained
     tokens can't be non-expiring)
2. Add it as a repo secret: Settings → Secrets and variables → Actions →
   New repository secret → name it `RELEASE_PLEASE_TOKEN`, paste the token.
3. Nothing else to change — `release-please.yml` already references
   `secrets.RELEASE_PLEASE_TOKEN` with a fallback to the default token, so
   it degrades to today's (broken-for-this-purpose) behavior until the
   secret exists, and picks it up automatically once it does.

## Version bumps

Derived from commit type, per [Conventional Commits](./PR_STANDARD.md) —
no extra author effort:

| Commit type | Bump |
|---|---|
| `fix:` | patch |
| `feat:` | minor (not major — see below) |
| `feat!:` / `BREAKING CHANGE:` | would normally be major, but... |

`release-please-config.json` sets `bump-minor-pre-major: true` and
`bump-patch-for-minor-pre-major: true` — while the project is pre-1.0
(matching [`docs/PATH_TO_LATE_BETA.md`](./PATH_TO_LATE_BETA.md)'s
maturity model), even a breaking change bumps minor, not major. This
avoids an accidental jump to `v1.0.0` before the project is actually
ready to call itself stable.

## Prerelease flag

`release-please-config.json` currently sets `"prerelease": true` —
every release this produces is marked a GitHub prerelease, matching the
project's current alpha/pre-late-beta status. **Once late beta is
reached** (all seven `LB-*` items in `docs/PATH_TO_LATE_BETA.md` closed),
flip this to `false` so releases stop being marked prerelease. This is a
manual one-line config change, not automatic — release-please has no
way to know when "late beta" is reached.

## Keeping the manifest in sync with manual releases

`.release-please-manifest.json` is release-please's own record of "the
last version I processed." If a release is ever cut manually (bypassing
this automation — as `v0.3.0-alpha.1` was, since it predates this
workflow), **update the manifest file to match** in the same PR, or
release-please's next run will propose the same changes again, not
knowing they were already shipped.

## CHANGELOG format

`release-please-config.json`'s `changelog-sections` maps Conventional
Commit types to this file's existing category names (`feat` → Added,
`fix` → Fixed, `docs` → Docs, `refactor`/`perf` → Changed) so new
automated entries read consistently with the hand-written `v0.1.0`,
`v0.2.0`, and `v0.3.0-alpha.1` entries above them. `test`, `ci`, and
`build` commits are excluded from the changelog entirely (`"hidden": true`)
— they're real work, but not something a downstream adopter reading
release notes needs to see.
