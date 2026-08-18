# Findings: uFawkesRes status in the uFawkes suite

## Decision (2026-08-18)

**Retired from the active uFawkes (Compose-tier) suite** — option (b) below,
scoped to Fawkes-tier only. uFawkesRes is no longer a promoted dependency of
the small-team uFawkes stack; the `dora` profile stays self-contained
(SQLite) by default. The repo itself is not archived and this repo's
optional `resource-plane` Compose profile (`compose.resource-plane.override.yaml`)
still works unchanged for teams that want shared Postgres — retirement is a
suite-positioning decision, not a deprecation of the integration code. See
`README.md` § Part of the Fawkes IDP and `AGENTS.md` §10 for where this is
now reflected.

> Findings note below, not a decision record — no ADR number assigned.
> Originally written to resolve a discrepancy flagged in the "Suite
> Alignment & Dojo Integration" task brief (2026-08-18): this repo's README
> family table listed `uFawkesRes` as a live plane, but ufawkes.dev's public
> stack list does not mention it. The findings and options below are
> unchanged from that investigation; only the decision above is new.

## What was verified

- **`paruff/uFawkesRes` exists and is not archived.** `gh repo view`
  confirms `isArchived: false`, description "Resource plane — shared
  Postgres, Valkey, Traefik, and Authelia for the uFawkes suite" (note: the
  description itself says "for the uFawkes suite," i.e. it self-identifies
  as a Compose-tier plane, not Fawkes/Kubernetes-only).
- **Last push: 2026-07-18** (`feat: add GitOps lifecycle gates to
  uFawkesRes`), about a month before this note was written. No GitHub
  releases exist for the repo (`gh release list` returns empty). So it's
  not dormant/abandoned, but it's also not at a tagged/versioned state —
  consistent with an early-stage or actively-being-built repo rather than
  a mature, stable plane.
- **ufawkes.dev does not mention uFawkesRes anywhere checked.** The
  homepage lists three main stacks — Obs, Pipe, DevX — plus Dojo as a
  learning environment. Neither "Res," "Sec," nor "AI" appear as distinct
  planes. The `/obs/` subpage (uFawkesObs's own dedicated page on the
  site) mentions Prometheus, Grafana, and Jenkins integration, but no
  mention of uFawkesRes, "resource plane," shared Postgres, Valkey,
  Traefik, or Authelia — despite uFawkesObs's own `AGENTS.md` and
  Compose profiles depending on it for one specific feature (see below).
- **uFawkesObs's actual code relationship with Res is real but now
  optional.** `AGENTS.md` §10, `compose.resource-plane.override.yaml`,
  and `.env.example`'s `DORA_POSTGRES_URL` all wire up uFawkesRes's shared
  Postgres as the backing store for DORA metric snapshots — but only when
  the `resource-plane` Compose profile is explicitly activated. As of the
  recent SQLite-backend work (PR #220), the `dora` profile is
  self-contained by default and needs no Res dependency at all. So the
  *current* code already treats Res as opt-in, not a hard requirement —
  which weakens the case that Res must be a load-bearing plane for every
  uFawkes (Compose-tier) adopter.
- **`catalog-info.yaml`** (this repo's Backstage descriptor) still lists
  `uFawkesRes` in the `System`'s `links` and `spec.dependsOn` as if it
  were a required, permanent dependency — this predates the SQLite work
  and hasn't been updated to reflect that Res is now opt-in.

## What was not verified / TODO

- **TODO:** Whether ufawkes.dev has any page beyond the homepage and
  `/obs/` that might reference Res (e.g. a full architecture/stack
  overview page) was not exhaustively checked — only those two pages were
  fetched. If a human wants full certainty, check `/pipe/` and `/devx/`
  too, and check whether ufawkes.dev has a sitemap or "all stacks" page.
- **TODO:** Whether uFawkesRes has an internal roadmap, issue tracker
  activity, or contributor discussion indicating planned/active vs.
  stalled status — only commit/release metadata was checked via the
  GitHub API, not issues or discussions.
- **TODO:** Whether the Fawkes (Kubernetes) monolith repo documents Res
  as one of *its* required components — not checked in this note (out of
  scope for Task 1; Task 4 of the same brief covers Fawkes architecture
  comparison and may surface this incidentally).

## Options

**(a) Res is real and still-evolving — add it to ufawkes.dev's public
stack list.** Rationale: it exists, isn't archived, has recent commits,
and this repo's own working code already depends on it for one real
feature (DORA Postgres snapshots). The gap may simply be that ufawkes.dev
hasn't caught up to a newer plane yet, not that Res was deliberately
excluded. Downside: if Res isn't actually ready for public promotion
(no releases, no docs page prepared), adding it prematurely could send
adopters to an unfinished repo.

**(b) Res is Fawkes (Kubernetes)-tier only, not a uFawkes (Compose)-tier
plane, for the small-team target audience.** Rationale: uFawkesObs's own
code already treats Res as strictly optional (opt-in `resource-plane`
profile, SQLite default) — the small-team persona this repo's
`docs/product/discovery-draft.md`/`docs/PATH_TO_LATE_BETA.md` target
(3–15 person teams) may not need a shared Postgres/Valkey/Traefik/Authelia
resource plane at all; that need may only really bite at Fawkes
(Kubernetes, larger-team) scale. Under this option, the README's family
table should either drop the Res row for the uFawkes-tier table or
annotate it as "Fawkes-tier only, optional for uFawkes." This is the
option most consistent with what's actually implemented in this repo
today.

**(c) Res is deprecated / being folded elsewhere.** No evidence found for
this — Res has recent commits (last month) and isn't archived, unlike
uFawkesDORA (confirmed archived, folded into uFawkesObs) or the
uFawkesSec question raised in Task 2 of the same brief. Listed for
completeness but not supported by current findings; would need explicit
confirmation from whoever owns the uFawkesRes repo before acting on it.

## Recommendation (not a decision)

Option (b) is the best fit for what's *actually implemented* today: Res
is real, active, and correctly wired into uFawkesObs's Compose profiles,
but as an **opt-in** integration, not a load-bearing one — which is
inconsistent with the README's family table currently presenting it
alongside Obs/Pipe/DevX as if it were an equally-required plane for every
uFawkes adopter. That said, whether Res *should* graduate to a fully
promoted, ufawkes.dev-listed plane (option a) is a product-tier call about
roadmap and readiness, not something this note can resolve — flagging for
a human decision per the task brief's ground rules.

## Next step

A human should decide between (a)/(b)/(c) (or a variant), then a follow-up
PR can update the README family table, `catalog-info.yaml`, and
optionally ufawkes.dev to match.
