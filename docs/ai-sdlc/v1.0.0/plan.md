# Plan: uFawkesObs v1.0.0

**Traces to:** [`spec.md`](spec.md) → [`intent.md`](intent.md)
**Status:** Draft | **Revision:** 1

This plan is gate-driven, not date-driven. Status lives in the issues and
in the [uFawkes Suite Release Project](https://github.com/users/paruff/projects/7),
not in this file. Every merge is human-gated (AGENTS.md §5).

## Sequence

1. **Decide the open questions in `intent.md`:** whether Makefile targets
   and profile names join the contract, and which milestone candidates are
   `release-blocker`s.
2. **Fix the blockers**, starting with #381 (the GitOps deploy path). #393
   and #182 depend on #381, per `EXECUTION_QUEUE.md`.
3. **Land the documentation and CI goals:** #495 (SQLite in the README),
   #497 (release assets; needs PM sign-off, since it's CI), and #498
   (upgrade notes).
4. **Cut `v1.0.0-rc.1`** through the release-please flow
   (`docs/RELEASE_PROCESS.md`). Re-verify the contract table in
   `spec.md` against the rc tag.
5. **Run the rc on clean machines:**
   - #494: a clean-host install on Linux and on macOS
   - #496: a new-user walkthrough

   File every gap found as an issue in the `v1.0.0` milestone.
6. **Merge the release-please PR for `v1.0.0`.** The GitHub Release is
   created on the next `Acceptance Full` pass.
7. **Announce.** Run the uFawkesAI `release` agent. It updates the
   ufawkes.dev page and drafts the dev.to and LinkedIn posts. You review
   and publish.
8. **Measure.** The release agent files the `measure:` issue. Point it at
   GitHub stars and forks, and at issues and PRs from anyone other than
   @paruff.

## Verification Strategy

| Criterion | Evidence | Step |
|---|---|---|
| AC-01 (REL-02, REL-04) | Real clean-host transcripts (Linux and macOS), plus walkthrough notes, linked from the release notes | 5 |
| AC-02 (REL-07) | The [`v1.0.0` milestone](https://github.com/paruff/uFawkesObs/milestone/1) filtered on `label:release-blocker` shows 0 open | 2, before step 6 |
| AC-03 (REL-01, 03, 05, 06) | Contract table re-verified at the rc; `grep -qi sqlite README.md`; `gh release view v1.0.0 --json assets` lists the tarball and `.sha256`; upgrade notes linked | 3, 4, 6 |
| AC-04 (REL-08) | Four live URLs (GitHub Release, ufawkes.dev, dev.to, LinkedIn) recorded on the Obs 1.0 Project item, all showing `v1.0.0` | 7 |
