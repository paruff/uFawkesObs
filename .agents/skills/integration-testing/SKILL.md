---
name: integration-testing
description: "Validate the OBS + PIPE + GitOps + Kubernetes flow end to end: pipeline artifacts, the GitOps commit, controller reconciliation, deployment and smoke tests. Use when verifying a release path or after changing any hand-off between those stages. Implements DORA AI Capabilities 4, 5, 6, 7."
license: MIT
compatibility: Claude Code, GitHub Copilot, OpenCode, Cursor, Codex, Gemini CLI
metadata:
  author: paruff
  suite: uFawkesAI
  form: rule
---

# Skill: integration-testing

> **Load trigger:** "load integration-testing skill" · **DORA:** AI Capabilities 4, 5, 6, 7

Checks each hand-off in the delivery path, then the whole path.

```text
code change -> PIPE builds, tests, scans -> artifacts (image, SBOM, signature)
  -> OBS receives them -> OBS updates the GitOps repo -> controller reconciles -> K8s deploys -> smoke tests
```

## The four checks

| Check | Inputs | Pass when |
| --- | --- | --- |
| PIPE to OBS | a pipeline run, `version.json`, the GitOps repo | OBS receives the right image tag and digest, `version.json`, SBOM and signature are present, and OBS creates a valid commit with valid YAML manifests |
| OBS to GitOps | OBS output, the GitOps repo | commits are well-formed and follow the commit convention; dev, staging and prod overlays resolve; no schema violations; only the expected files change |
| GitOps to controller | the GitOps repo, the cluster (Flux or ArgoCD) | reconciliation is triggered and applies the manifests, the rollout succeeds, health checks pass, the controller logs no errors |
| Full stack | the whole system | the pipeline completes, the GitOps update is valid, reconciliation and deployment are healthy, and smoke tests pass |

Run the checks in that order; stop at the first failure and report which hand-off broke.

## Output

Write one report per check (`pipe-obs-report.json`, `obs-gitops-report.json`, `controller-integration-report.json`,
`full-integration-report.json`) with this shape:

```json
{
  "skill": "integration-testing",
  "check": "obs-to-gitops",
  "status": "pass | fail",
  "details": {"commit": "abc123", "overlays": {"dev": "pass", "staging": "pass", "prod": "pass"}, "manifests_valid": true}
}
```

Also keep `manifest-diff.txt` (PIPE to OBS and OBS to GitOps) and `cluster-state.json` (full stack), and compare cluster
state with Git to confirm they match.

## Success criteria

End-to-end correctness, a healthy rollout, valid GitOps commits, and no schema violations.
