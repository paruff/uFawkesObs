# Build & CI Determinism — uFawkesObs

> What makes a run of this repo reproducible: same commit in → same result
> out, regardless of when or how many times it runs. Findings from a
> concrete audit, 2026-09-23. Tracked as a P2 backlog item in
> [`../EXECUTION_QUEUE.md`](../EXECUTION_QUEUE.md); this doc is the
> reference for *what* and *why*, not live status.

## Already Solid

- Every Docker image in `compose.yaml` is version-pinned — no `latest` tags
  (enforced by `AGENTS.md` §4).
- Third-party GitHub Actions are SHA-pinned (`webfactory/ssh-agent@e838...`,
  `dorny/paths-filter@ceb8...`), not floating version tags.
- `tests/unit/requirements.lock.txt` — exact pins for the highest-traffic
  test path (PR #392, 2026-09-23).
- DORA compute interval already made consistent between local and CI
  (#359) — was previously racier locally than in CI with identical code.

## Now (cheap, low-risk — do these next)

1. **Extend the lock-file pattern to the other 5 `requirements*.txt` files**
   (`tests/integration/`, `tests/acceptance/`, `dora/compute/`,
   `dora/ingestion/`, `apps/telemetry-generator/`). Same mechanical process
   as #392: install in a clean venv, `pip freeze`, wire the consuming
   `Makefile` target / CI step to the lock. Already tracked as a P2 item.
2. **Pin `paruff/ufawkespipe` reusable workflows to a stable release, not a
   beta tag** — currently `@v1.4.0-beta.1` / `@v1.2.0` for several jobs
   (#352, already filed). A beta tag can be moved by its maintainer more
   readily than a proper release tag.
3. **Pin GitHub Actions runner images**, not `ubuntu-latest` — used in 22
   places across `.github/workflows/`. GitHub silently updates what
   "latest" resolves to (new preinstalled tool versions, sometimes new
   defaults) with zero change to this repo; a workflow that passed
   yesterday can fail today with an identical diff. Pin to a specific image
   (e.g. `ubuntu-24.04`) instead. **This needs your sign-off** — it touches
   CI/CD config across every workflow file (AGENTS.md §5) and is a genuine
   multi-file change, not something to land silently.
4. **Pin Python to an exact patch version**, not just minor
   (`python-version: "3.12"` → `"3.12.7"` or similar) — same class of gap
   as #3, same sign-off need, much smaller diff (2 files).

## Should (needs more design, but no new dependency)

1. **A `make relock` target** that regenerates every lock file in one
   command, so keeping locks current isn't a manual venv dance per file —
   reduces the risk of a lock silently drifting from its source
   `requirements.txt` (already noted as a gap in #392's own PR description).
2. **Digest-pin Docker images**, not just version tags
   (`prom/prometheus:v3.5.4` → `prom/prometheus:v3.5.4@sha256:...`). A
   version tag is conventionally stable but not cryptographically
   immutable — a registry-side re-push under the same tag (rare, but it
   happens) would go undetected. This is the actual gold-standard fix for
   "same tag, different image" risk, not a Now item because it's a much
   larger diff (every service in `compose.yaml`) and needs a documented
   process for updating digests when a version bumps.
3. **Replace fixed `sleep N` waits with condition-based polling** in CI —
   `ci-tests.yml` (7 occurrences), `ci-acceptance-full.yml`,
   `ci-acceptance-smoke.yml`, `ci-chaos-nightly.yml`, `opencode.yml` each
   have at least one. A fixed sleep is either too short (flaky under load)
   or too long (wastes CI minutes every single run) — polling for the
   actual ready-condition (already the pattern in most of `wait-healthy.sh`
   and the "Wait for services" steps) is strictly better and is this
   repo's own established pattern elsewhere; it just isn't used
   everywhere yet.
4. **A Dependabot/Renovate policy specifically for lock files** — pinning
   without a renewal mechanism just freezes today's versions forever,
   including their eventual known CVEs. Determinism and staying current
   are in tension; this needs an explicit policy, not just the pins.

## Future (larger, aspirational — not a near-term ask)

1. **Cosign/Sigstore verification of pulled images** — ties into
   uFawkesPipe's existing `security` profile (Trivy, DefectDojo). Verifies
   the digest-pinned image wasn't tampered with in transit or at rest, not
   just that it matches what was pinned.
2. **Hermetic/reproducible builds** (Nix or similar) for the `dora/` Python
   services and `apps/telemetry-generator` — full bit-for-bit build
   reproducibility, not just pinned dependency versions. Meaningfully more
   infrastructure than this repo's "boring technology" principle
   (`README.md`) calls for today; revisit if the DORA services grow more
   complex or ship as standalone artifacts.
3. **Self-hosted or pinned-image CI runners** as the more permanent fix for
   the `ubuntu-latest` problem, if GitHub-hosted runner drift becomes a
   recurring source of red CI rather than a one-off. A pinned runner image
   tag (Now #3, above) is the lighter-weight fix to try first.

## Test Suite Determinism (audit, 2026-09-23)

Findings from auditing `tests/` itself, separate from the build/CI
determinism above — coverage was 75% on `dora/` at audit time (`make
test-unit`; see `tests/README.md` for the pyramid, `tests/acceptance/README.md`
for how to run each tier).

**Now-tier finding, already filed:**

- `find_repo_root()` in `tests/unit/test_dora_event_schemas.py` hardcodes
  the checkout directory name (`#383`) — fails from any clone/worktree not
  literally named `uFawkesObs`. Confirmed live: reproduced by running the
  suite from a differently-named worktree.

**Should:**

1. **No coverage threshold enforced.** 75% is measured (#343/PR #382) but
   nothing fails CI if it drops — a future PR could silently regress
   coverage with no signal. Add a `--cov-fail-under=<threshold>` to `make
   test-unit` / `ci-tests.yml`'s Unit Tests job once a sensible floor is
   picked (75% itself, or slightly below to leave room, given `main.py`'s
   0% is a legitimate gap covered at a different test tier, not a bug to
   chase in unit tests specifically).

**Future (lower priority, no live bug found):**

1. **Coverage scope is narrow** — only `dora/` is instrumented. `scripts/`,
   `apps/telemetry-generator/`, and the acceptance step-definitions have no
   coverage visibility. Plausibly correct as-is (much of that surface is
   bash/config, not amenable to `--cov`), but worth naming as a known blind
   spot rather than an assumed non-issue.
2. **No test-order randomization** (e.g. `pytest-randomly`). Pytest here
   runs in file-discovery order by default. No evidence of an order-
   dependent test today, so this isn't chasing a real bug — it's an absent
   safety net that would otherwise catch a future test that only passes
   because an earlier one mutated shared state.

## Why This Matters Here Specifically

Two real incidents this session motivated this audit, not a hypothetical:

- **The stranded coverage-measurement fix (#343)** existed correctly on a
  branch for 10 days before anyone noticed it never reached `main` — partly
  because nothing measured coverage at all, so there was no signal that
  something was missing.
- **PR #386's CI failures**, root-caused via `systematic-debugging`: three
  workflows had promised ("will be populated from GitHub Secrets") wiring
  that was never implemented, silently masked by a default value for as
  long as that default existed. Once the default was correctly removed,
  every one of those latent gaps surfaced at once. Non-determinism doesn't
  announce itself — it hides behind whatever happens to make it not matter
  yet.
