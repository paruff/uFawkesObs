# Plan: unbreak Acceptance Full on main

**Traces to:** Acceptance Full red on main since 08dd43f (#673).

## Root cause

The OBS-SLI-006 gate requires every feature-complete dashboard to show data.
`Host Metrics (OTLP agents)` charts series pushed by an external Mac/NAS
agent. CI runs no agent, so the dashboard is empty there by construction.
The last green run is bd2bbc2, the commit before it was added.

## Changes

1. Add the dashboard to `KNOWN_INCOMPLETE_DASHBOARDS` in
   `tests/acceptance/steps/slo_steps.py`, with the reason, beside the
   existing IoT entry. It is still reported, only excluded from pass/fail.

## Verification Strategy

| Criterion                                  | Evidence                                   | How                                                    |
| ------------------------------------------ | ------------------------------------------ | ------------------------------------------------------ |
| Gate no longer fails on the host dashboard | OBS-SLI-006 passes; dashboard still listed | Acceptance Full on this PR (`workflow_dispatch`) / main |
| Other dashboards still gated               | Gate fails if any other dashboard is empty | unchanged assertion; only one set entry added          |
| Not covered                                | The dashboard showing real data            | needs a running agent; tracked in its own plan.md      |
