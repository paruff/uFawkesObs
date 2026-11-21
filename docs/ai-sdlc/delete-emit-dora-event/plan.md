# Plan: delete scripts/emit-dora-event.sh

**Traces to:** #734 (suite decision, uFawkesAI#288; uFawkesAI `docs/ai-sdlc/dora-events/spec.md` REQ-006)

## Changes

1. Delete `scripts/emit-dora-event.sh`. No workflow here calls it and it never
   posts to `/event`; uFawkesAI's copy is the only emitter.
2. Delete its test, `scripts/test-emit-dora-event.sh`.
3. Remove the test from the `SUITES` list in `scripts/run-unit-tests.sh` and the
   `emit-dora-event` term from the `unit-tests` hook filter in
   `.pre-commit-config.yaml`.

No behaviour, config, compose or dashboard changes.

## Verification Strategy

| Criterion                       | Evidence                                                      | How                                                         |
| ------------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------- |
| No reference to the script left | The search returns nothing                                    | `grep -rn emit-dora-event --exclude-dir=.git .`             |
| Remaining unit suites still run | `run-unit-tests: all 3 suites passed`                         | `bash scripts/run-unit-tests.sh`                            |
| Hooks pass                      | pre-commit and the CI jobs are green                          | `pre-commit run --all-files`; PR checks                     |
| Not covered                     | Callers outside this repo, if any, are not searched           | The issue states no workflow here calls it                  |
