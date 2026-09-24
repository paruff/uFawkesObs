# INTENT — Read This Before Touching Anything

**uFawkesObs** is the observability plane of the Fawkes IDP family: OpenTelemetry,
Prometheus, Tempo, Loki, Grafana, and Alloy, delivered as Docker Compose with
GitOps reconciliation over SSH to a real host.

## The one thing to know

This is not a demo repo. A push to `main` that touches `config/**`,
`compose.yaml`, `.env.example`, or `dashboards/**` triggers a real deploy to a
real machine over SSH. Treat every change to those paths as production-facing,
even during local iteration — see `.claude/rules/` for the path-scoped
invariants and the `gitops-reconcile` skill for how the deploy actually works.

## What "done" means here

- Declarative config, not scripts with logic in them.
- Every service has a real healthcheck; nothing runs on `latest`.
- Merges are human-gated. Agents open PRs; agents never merge, never push to
  `main`, never apply `large-pr-approved`.
- A fix isn't done until it's verified against the actually-running stack, not
  just against parsed YAML — see `docs/TESTING_PYRAMID.md`.

## Where to go next

| Need | Read |
|---|---|
| Full governance, PM–agent contract, planning cascade | `AGENTS.md` |
| Path-specific invariants (compose, config, scripts, tests, dashboards) | `.claude/rules/` |
| How GitOps reconciliation and deploy actually work | `.agents/skills/gitops-reconcile/SKILL.md` |
| Why a technology choice was made | `docs/adr/README.md` |
| North Star, non-goals | `VISION.md` |
| What's ready to work on right now | `EXECUTION_QUEUE.md` |

## Explicit non-goals

Don't add Kubernetes, don't reintroduce the retired uFawkesRes Postgres
integration, don't build progressive delivery before `docs/DEPLOYMENT_STRATEGY.md`
says the model exists. See `VISION.md` for the full list.
