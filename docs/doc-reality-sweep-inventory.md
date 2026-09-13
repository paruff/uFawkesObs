# Doc-Reality Sweep Inventory — uFawkesObs

This inventory classifies every TODO/FIXME/aspirational/not yet implemented/coming soon/placeholder marker found across the 5 documented files, per the three-bucket model.

## Bucket 1: Legitimate Disclosure

*Real, current limitation stated deliberately. Leave it; make sure it reads as a limitation and not a roadmap promise.*

| File | Line | Marker Type | Classification |
|------|------|-------------|----------------|
| `docs/ai-observability-guide.md` | 102 | `placeholder` (explicit) | `ai:suggestion_acceptance_rate:ratio` returns `0` until AI SDK emits acceptance metrics. This is an intentional placeholder noting the metric is not yet emitted by the SDK. |
| `docs/ai-observability-guide.md` | 163 | `placeholder` (explicit) | Continuation of the above — the rework metric discussion acknowledges the placeholder state. |
| `docs/fawkes-migration.md` | 316 | `aspirational` | "The current model is SSH push with `make up`. A staged [future model]..." — correctly marks the current SSH-push model as a known limitation in transition. |
| `docs/KNOWN_LIMITATIONS.md` | 184 | `placeholder` / `REPLACE_ME` | "`changeme`, or still a `REPLACE_ME*` placeholder. Starting the stack with a raw..." — explicitly documents a known placeholder that must be resolved before production use. |
| `docs/multi-stack-integration.md` | 172-173 | `note` (Docker Compose flag) | `--profile placeholder` is valid Docker Compose v2 syntax (show all services regardless of profile labeling). Documented usage, not a roadmap promise. |

## Bucket 2: Stale

*Describes something since built or since abandoned. Fix or delete.*

| File | Line | Marker Type | Classification |
|------|------|-------------|----------------|
| N/A | N/A | N/A | No stale markers identified in the 5 files. All markers either describe current limitations or future intentions. |

## Bucket 3: Undated Promise

"Coming soon" with no issue behind it. Either link an issue or remove the sentence; a public repo should not promise work nobody has committed to.

| File | Line | Marker Type | Classification |
|------|------|-------------|----------------|
| `docs/CONTRACTS.md` | 238 | `not yet implemented` | "The plan (not yet implemented) is for **uFawkesPipe** to host the" — references a future responsibility for uFawkesPipe without linking an issue, without a timeline, and the phrase "not yet implemented" is an undated promise. This should either: (a) link the tracking issue that owns this work, or (b) be removed if the plan has been abandoned. |

## Summary

| Bucket | Count | Files |
|--------|-------|-------|
| 1. Legitimate Disclosure | 5 | ai-observability-guide.md (2), fawkes-migration.md (1), KNOWN_LIMITATIONS.md (1), multi-stack-integration.md (1) |
| 2. Stale | 0 | — |
| 3. Undated Promise | 1 | CONTRACTS.md (1) |

## Recommended Next Steps

1. **Bucket 3 — CONTRACTS.md:238**: Decide whether the uFawkesPipe hosting plan is (a) tracked in a GitHub issue and should have a link added, or (b) has been abandoned and the sentence should be removed. Do not bulk-edit until this decision is made.

2. **Bucket 1 — All others**: Leave as-is. Each reads as a deliberate limitation or technical note, not a roadmap promise.

3. **Re-run the sweep periodically** (e.g., per release cycle) to catch new aspirational markers before they go stale.

**Method**: Mechanical grep for `TODO`, `FIXME`, `aspirational`, `not yet implemented`, `coming soon`, `placeholder` across `docs/`. Each match was read in context and classified by the author.
