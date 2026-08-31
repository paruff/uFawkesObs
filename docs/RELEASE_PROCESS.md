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
