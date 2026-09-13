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

**H2 exit criteria (remaining):**
- [ ] LB-04: Full rollback drill completed over SSH with sandbox host
- [ ] All docs pass reality sweep (no stale aspirational markers)

---

## H3 — Kubernetes & Scale (Backlog)

**Goal:** Scale from Docker Compose to cloud-native Kubernetes environments.

| Milestone | Theme | Deliverables | Status | Issue |
|---|---|---|---|---|
| **M5-01** | K8s Strategy ADR | Architecture Decision Record for K8s migration | ✅ Done | [#84](https://github.com/paruff/uFawkesObs/issues/84) |
| **M5-02** | Helm Chart | Umbrella chart for core stack | ✅ Done | [#85](https://github.com/paruff/uFawkesObs/issues/85) |
| **M5-03** | k3d Simulator | Local K8s bootstrap + Makefile targets | ✅ Done | [#86](https://github.com/paruff/uFawkesObs/issues/86) |
| **M5-04** | K8s Acceptance CI | GitHub Actions workflow for K8s acceptance tests | ✅ Done | [#87](https://github.com/paruff/uFawkesObs/issues/87) |

**H3 exit criteria:**
- [ ] Helm chart passes `helm lint` with 0 warnings
- [ ] `make k3d-up` boots a local cluster and deploys the chart
- [ ] K8s acceptance tests pass in CI

---

## Release Gates

Every release requires:

1. **All milestone tasks complete** — checked against this document
2. **CI green** — all required status checks pass on `main`
3. **Docs updated** — ARCHITECTURE.md, KNOWN_LIMITATIONS.md, CHANGE_IMPACT_MAP.md reflect the release
4. **CHANGELOG.md updated** — release-please automates this from conventional commits
5. **Tag applied** — `v<semver>` annotated tag

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
