# MILESTONES.md — uFawkesObs

> **Horizon:** Months | **Owner:** Maintainer | **Review:** Per milestone completion
> **Feeds into:** [`VISION.md`](VISION.md) ← source | [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) → next tier

---

## Horizon Map

| Horizon | Timeframe | Theme | Status |
|---|---|---|---|
| **H1** | 2026-Q2–Q3 | Core substrate, repo hardening, cross-plane docs, DORA integration | ✅ Complete |
| **H2** | 2026-Q3–Q4 | Late beta gates, rollback drill, test pyramid, docs reconciliation | 🟡 In Progress |
| **H3** | 2027+ | Kubernetes deployment, Helm charts, multi-host progressive delivery | 🔲 Backlog |

---

## H1 — Core Substrate (Complete)

**Goal:** Ship a working observability stack that a small team can clone and run.

| Milestone | Theme | Deliverables | Status | Release |
|---|---|---|---|---|
| **M1** | Substrate Core | Docker Compose stack (OTel, Prometheus, Alertmanager, Tempo, Loki, Alloy, Grafana) with unit/integration test gates | ✅ Done | v0.1.0 |
| **M2** | Repo Hardening | CONTRIBUTING.md, CODE_OF_CONDUCT.md, issue templates, ARCHITECTURE.md, KNOWN_LIMITATIONS.md, repo badges | ✅ Done | v0.2.0 |
| **M3** | Cross-Plane Docs | uFawkesPipe integration guide, uFawkesDevX integration guide, Backstage catalog registration, multi-stack network join | ✅ Done | v0.2.0 |
| **M4** | DORA & Ecosystem | DORA data contract (ADR-006), Prometheus DORA recording rules, Grafana DORA dashboard, uFawkesDORA/uFawkesRes wiring | ✅ Done | v0.3.0 |

**H1 exit criteria (all met):**
- [x] `make up` brings up a healthy stack with live dashboards
- [x] Unit, integration, and acceptance test gates pass in CI
- [x] Cross-plane integration guides exist for uFawkesPipe and uFawkesDevX
- [x] DORA metrics flow from deployment events through to Grafana dashboard

---

## H2 — Late Beta (In Progress)

**Goal:** Close the gaps that would burn a beta adopter on first contact.

| Milestone | Theme | Deliverables | Status | Issue |
|---|---|---|---|---|
| **LB-01** | Onboarding baseline | Measure `time_to_first_signal_minutes` | ✅ Done (93s) | [#179](https://github.com/paruff/uFawkesObs/issues/179) |
| **LB-02** | Localhost ports | Bind Loki/Tempo/Prometheus/Alertmanager to 127.0.0.1 | ✅ Done | [#180](https://github.com/paruff/uFawkesObs/issues/180) |
| **LB-03** | Alert channel | Tested Slack notification for Alertmanager | ✅ Done | [#181](https://github.com/paruff/uFawkesObs/issues/181) |
| **LB-04** | Rollback drill | Run and document a live rollback drill | 🟡 In Progress | [#182](https://github.com/paruff/uFawkesObs/issues/182) |
| **LB-05** | Deploy stability | Investigate GitOps Reconciliation transient failure | ✅ Done | [#183](https://github.com/paruff/uFawkesObs/issues/183) |
| **LB-06** | Feedback channel | Beta feedback discussion | ✅ Done | [#184](https://github.com/paruff/uFawkesObs/issues/184) |
| **LB-07** | Plan reconciliation | Reconcile docs/plan.md status drift | ✅ Done | [#185](https://github.com/paruff/uFawkesObs/issues/185) |

### H2 Documentation Reconciliation (PR #362 — Merged)

| Task | Issue | Status | Commit |
|---|---|---|---|
| Doc-reality sweep: classify aspirational markers | [#347](https://github.com/paruff/uFawkesObs/issues/347) | ✅ Done | `docs/doc-reality-sweep-inventory.md` |
| Reconcile docs/plan.md status drift | [#348](https://github.com/paruff/uFawkesObs/issues/348) | ✅ Done | `docs/plan.md` |
| Document test pyramid and marker taxonomy | [#344](https://github.com/paruff/uFawkesObs/issues/344) | ✅ Done | `tests/README.md` |
| Rename DAY ONE.md to docs/DAY_ONE.md | [#349](https://github.com/paruff/uFawkesObs/issues/349) | ✅ Done | `docs/DAY_ONE.md` |
| Relocate top-level clutter | [#351](https://github.com/paruff/uFawkesObs/issues/351) | ✅ Done | `docs/AI_STANCE.md`, `config/docker-compose.integration.yml` |
| Fix LB-04 status in PATH_TO_LATE_BETA.md | [#342](https://github.com/paruff/uFawkesObs/issues/342) | ✅ Done | `docs/PATH_TO_LATE_BETA.md` |
| Update MODEL_POLICY.md to grade-based system | [#346](https://github.com/paruff/uFawkesObs/issues/346) | ✅ Done | `docs/MODEL_POLICY.md` |
| Consolidate opencode workflow files | [#350](https://github.com/paruff/uFawkesObs/issues/350) | ✅ Done | `.github/workflows/opencode.yml` |
| Update main-ci-guard to stable version | [#352](https://github.com/paruff/uFawkesObs/issues/352) | ✅ Done | `.github/workflows/main-ci-guard.yml` |
| Make DORA acceptance test deterministic | [#359](https://github.com/paruff/uFawkesObs/issues/359) | ✅ Done | `tests/acceptance/steps/dashboard_steps.py` |
| Restructure README to ~150 lines | [#345](https://github.com/paruff/uFawkesObs/issues/345) | ✅ Done | `README.md`, `docs/TROUBLESHOOTING.md` |
| Add test coverage measurement | [#343](https://github.com/paruff/uFawkesObs/issues/343) | ✅ Done | `pytest.ini`, `Makefile` |
| Close stale RELEASE_PLEASE_TOKEN issue | [#353](https://github.com/paruff/uFawkesObs/issues/353) | ✅ Done | Closed — release-please works with fallback token |

**LB-04 update (2026-09-24):** the network-path blocker is resolved — a
self-hosted GitHub Actions runner is now registered on the deploy target
itself (a Synology DS920+), giving CI a LAN route it never had before.
Root cause of the original SSH instability (#381) turned out to be that
every deploy job ran on GitHub-hosted cloud runners with no route to the
LAN at all, not host-key regeneration. The drill itself (`docs/ROLLBACK_DRILL.md`
Precondition 1 onward) still hasn't been run — do that once #381 closes
with a confirmed-successful deploy, not before.

**H2 exit criteria (remaining):**
- [ ] LB-04: Full rollback drill completed over SSH with sandbox host
- [ ] All docs pass reality sweep (no stale aspirational markers)

---

## H3 — Fawkes K8s Migration (Backlog)

**Goal:** Migrate from Docker Compose to Fawkes Kubernetes track.

| Milestone | Theme | Deliverables | Status | Issue |
|---|---|---|---|---|
| **M5-01** | K8s Strategy ADR | Architecture Decision Record for K8s migration to Fawkes track | ✅ Done | [#84](https://github.com/paruff/uFawkesObs/issues/84) |
| **M5-02** | Helm Chart | Umbrella chart for core stack, targeting Fawkes deployment | ✅ Done | [#85](https://github.com/paruff/uFawkesObs/issues/85) |
| **M5-03** | k3d Simulator | Local K8s bootstrap + Makefile targets, Fawkes-compatible | ✅ Done | [#86](https://github.com/paruff/uFawkesObs/issues/86) |
| **M5-04** | K8s Acceptance CI | GitHub Actions workflow for K8s acceptance tests, Fawkes-integrated | ✅ Done | [#87](https://github.com/paruff/uFawkesObs/issues/87) |

**H3 exit criteria:**
- [ ] Helm chart passes `helm lint` with 0 warnings
- [ ] `make k3d-up` boots a local cluster and deploys the chart
- [ ] K8s acceptance tests pass in CI
- [ ] Fawkes integration validated (not just local K8s)

---

**Rationale:** uFawkesObs is the Compose-tier stepping stone. Teams graduating to production-grade observability target Fawkes (Kubernetes track), not uFawkesObs. This milestone documents the migration path, not an in-place upgrade.

Every release requires:

1. **All milestone tasks complete** — checked against this document
2. **CI green** — all required status checks pass on `main`
3. **Docs updated** — ARCHITECTURE.md, KNOWN_LIMITATIONS.md, CHANGE_IMPACT_MAP.md, CONTRACTS.md reflect the release
4. **CHANGELOG.md updated** — release-please automates this from conventional commits, per [`docs/RELEASE_PROCESS.md`](docs/RELEASE_PROCESS.md)
5. **Tag applied** — `v<semver>` annotated tag
6. **Deployed and verified** — per [`docs/DEPLOYMENT_STRATEGY.md`](docs/DEPLOYMENT_STRATEGY.md): SSH push, post-deploy smoke verification, automatic rollback on failure

---

## Traceability

Every milestone task traces back to:
- **VISION.md** core principles (which principle does this serve?)
- **discovery-draft.md** JTBD (does this move toward the north star?)
- **spec.md** functional requirements (OBS-F##, OBS-N##)
- **GitHub issue** (actual work tracking)

| Milestone | Vision Principle | Spec Reference | GitHub Issue |
|---|---|---|---|
| M1 | Composition Over Compilation, Self-Monitoring | OBS-F01–F06, OBS-N01–N05 | #55–#58 |
| M2 | GitOps Reconciliation | OBS-F10–F12 | #71, #74, #75 |
| M3 | Composition Over Compilation | OBS-F10–F12 | #76–#79 |
| M4 | GitOps Reconciliation | OBS-F20–F23 | #80–#83 |
| LB-01–LB-07 | All principles | OBS-N01–N05 | #179–#185 |
| M5 | Reproducible Local Simulation | OBS-F30–F32 | #84–#87 |

---

## How This Connects

| Document | Horizon | What It Answers |
|---|---|---|
| [`VISION.md`](VISION.md) | Years | Why does this product exist? What are the non-goals? |
| **MILESTONES.md** (this file) | Months | What are we building next, and in what order? |
| [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) | Weeks | What specific tasks are ready to be worked? |
| [`plan-for-the-day.md`](plan-for-the-day.md) | Today | What am I doing right now? |
