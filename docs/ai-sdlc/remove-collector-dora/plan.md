# Plan: delete config/otel/collector-dora.yaml

**Traces to:** #750

## Changes

1. Delete `config/otel/collector-dora.yaml`. The DORA Collector container
   was removed earlier and nothing mounts or loads this file.
2. Delete its test, `tests/unit/test_otel_collector_dora_config.py`.
3. Update `docs/CONTRACTS.md` so it no longer points at the deleted file.

No compose, dashboard or runtime behaviour changes.

## Verification Strategy

| Criterion                        | Evidence                                          | How                                                       |
| -------------------------------- | ------------------------------------------------- | --------------------------------------------------------- |
| No live reference to the file    | Only history, comments and a docs-test list name it | `grep -rn "collector-dora.yaml" --exclude-dir=.git .`     |
| Config validators still pass     | `make lint-config` exits 0                        | `make lint-config`                                        |
| Artifact chain satisfied         | `Artifact chain intact`                           | `bash scripts/check-artifact-chain.sh origin/main HEAD`   |
| Not covered                      | Consumers outside this repo are not searched      | The issue states the file is dead                         |
