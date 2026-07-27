# Feature-Level Docs

Each subdirectory here is one feature's discovery/spec/design/tasks output
from the `discover → spec → design → plan` pipeline (AGENTS.md §2),
preserved after the feature ships — distinct from the transient root-level
`design.md` / `specification.md` / `tasks.json` that the feature-flow
pipeline overwrites while a feature is in progress (see `.gitignore`).

Convention: `docs/features/<feature-slug>/{discovery-draft,spec,design}.md`
and `tasks.json`, mirroring the file names used in `docs/product/`.

Product-level (whole-repo) discovery/spec/design/tasks live in
[`docs/product/`](../product/) instead.

## Index

- [`chaos-failure-injection/`](chaos-failure-injection/) — Phase 5 chaos
  and failure-injection acceptance tests (shipped; see
  `tests/acceptance/features/chaos_resilience.feature`,
  `.github/workflows/ci-chaos-nightly.yml`).
