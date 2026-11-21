# Plan: dev environment where the signal actually arrives

**Traces to:** #750 (goal), #742, #743, #744, #745, #746, #747, #748, #749

## Changes

1. `make lint-config`: one Docker-only gate over every config validator (compose, promtool config and rules, Collector, Tempo, Loki, amtool, Alloy). `validate`, `ci-local` and the `ci-quality` job run it. Tempo goes through `scripts/validate-tempo.sh` because `-config.verify` fails on the intentional MCP-enabled warning.
2. `make smoke-telemetry` (`tests/smoke/`): send a trace, log and metric to the Collector, poll Tempo, Loki and Prometheus, fail naming the missing signal. Runs in the acceptance smoke job.
3. `make doctor` also checks Docker, `.env` and compose ports (`scripts/doctor-stack.sh`); `docs/DEVELOPING.md`; AGENTS.md canonical commands.
4. Collector self-monitoring panels and a wider drop alert; skills `signal-quality-audit` and `observability-correlation`.
5. Pinned marketplace skills and read-only Grafana and Tempo MCP servers (`docs/AGENT_MCP.md`).

## Verification Strategy

| Criterion | Evidence | How |
| --- | --- | --- |
| Clean tree passes the config gate | `make lint-config` exits 0 | `make lint-config` |
| Bad configs are caught | A broken rule, a pipeline naming a missing exporter, an unset `${VAR}` and a broken Tempo config each fail | Break one at a time, run `make lint-config` |
| Signal arrives end to end | All three signals reported arrived | `make smoke-telemetry` on a running stack |
| Loss is detected | Removing the Tempo exporter makes it fail naming `traces` | Edit `collector.yaml`, restart the Collector, run `make smoke-telemetry` |
| doctor reports prerequisites | Missing `.env` and a busy port each fail with a fix hint | `bash scripts/doctor-stack.sh` |
| Panels return data | Each new panel query returns a series | Query Prometheus with the panel expressions |
| Repo checks pass | Unit tests, hooks and the CI jobs are green | `pytest tests/unit/`; `pre-commit run --all-files`; PR checks |
| Not covered | Marketplace SHA refs, `uvx mcp-grafana` with a real token, `memory_limiter_refused_*` before a refusal occurs | Needs the owner's machine or a fault injection |
