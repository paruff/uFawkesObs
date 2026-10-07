# Plan: adopt uFawkesPipe's shared shift-left hooks

**Traces to:** uFawkes.dev [`docs/ai-sdlc/shift-left/spec.md`](https://github.com/paruff/uFawkes.dev/blob/main/docs/ai-sdlc/shift-left/spec.md)
(R1–R6, R9) and its [plan](https://github.com/paruff/uFawkes.dev/blob/main/docs/ai-sdlc/shift-left/plan.md),
phase C3 | **Status:** In progress

uFawkesPipe publishes the suite's shift-left hooks and tools once, by tag.
This repo pins that tag and holds one file of its own, `scripts/shift-left.sh`,
which runs the tools that aren't hooks (doctor, agent gate, triage,
`require-tool`) from the same pinned clone.

| Step | What                                                                                                                  |
| ---- | --------------------------------------------------------------------------------------------------------------------- |
| C3a  | Clear what the shared hooks find (SHA pins, cooldowns, ADR-034 pins, one injection), uFawkesObs#615                   |
| C3b  | The shared hooks (parity, semgrep, Trivy, stamps), actionlint and schema hooks, `require-tool` for tool-backed hooks, `.shift-left.yml`, the doctor at session start, the agent gate, the devcontainer, `make doctor` |
| C3c  | A mypy type check over `dora/` (shift-left plan F1, decided 2026-10-06), and the one bug it found: `MetricsDB` queried a connection that is `None` outside `async with`, uFawkesObs#623 |

## Verification Strategy

| Check                                   | How                                                                                       |
| --------------------------------------- | ----------------------------------------------------------------------------------------- |
| Every hook runs in CI or says why not   | `bash scripts/shift-left.sh check-shift-left-parity` (also a hook): every hook in CI or listed    |
| CI's two stages pass                     | Both stages run locally as Pre-flight runs them (`SKIP` from `.shift-left.yml`), then CI |
| The checks actually run in a clone      | `make doctor`                                                                             |
| Nothing slips back                       | uFawkes.dev's `/status/` matrix, rebuilt daily                                            |
| `dora/` type-checks, and using `MetricsDB` before `connect()` fails clearly | `pre-commit run mypy --all-files`; `tests/unit/test_dora_metrics_sqlite.py::test_querying_before_connect_says_so` (written first, failed with `AttributeError`, now a `RuntimeError` naming the fix) |
