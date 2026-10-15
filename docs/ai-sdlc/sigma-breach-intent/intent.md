# Intent: a σ-band breach opens an intent issue (Stage 6)

uFawkesObs#602, part of the suite release plan ("After this plan").

## Problem

A DORA metric can drift well outside its normal range for a team and nobody
is prompted to act. The AI-SDLC cycle (`intent → spec → plan`) has no way back
in from production signals.

## Desired outcome

When a team's DORA metric stays more than 3σ worse than its own 30-day mean
for 24h, an `intent` issue is opened in the affected repo, in the same format
`dojo-feedback-intent.yml` uses. One open issue per team and metric.

## Out of scope

- Writing the `intent.md` itself: humans decide the intent.
- Automated remediation (the CFR rollback in #502 is separate).
