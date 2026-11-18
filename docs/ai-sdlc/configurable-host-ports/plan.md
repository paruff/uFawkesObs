# Plan: configurable host ports for Grafana and the telemetry generator

**Traces to:** paruff/uFawkesPipe#223 (NAS test and integration environment).

## Problem

On the Synology NAS, host port 3000 is taken (Sure) and 5001 is DSM's HTTPS port, so
`grafana` and `telemetry-generator` cannot publish their default ports there. The NAS runs
Docker Compose v2.20.1, which has no `!override`, so an override file cannot drop a published
port: the host side has to be a variable in `compose.yaml`.

## Changes

1. `compose.yaml`: `"${GRAFANA_PORT:-3000}:3000"` and `"${TELEMETRY_GENERATOR_PORT:-5001}:5000"`.
   Defaults equal the old values, so nothing changes for anyone who sets nothing.
2. `.env.example`: document both variables.
3. `inspec/ufawkesobs-conformance/`: the ports control compared the running container with the
   *raw text* of each mapping. Splitting `${GRAFANA_PORT:-3000}:3000` on `:` also splits at the
   `:-` inside the expression, giving host IP `${GRAFANA_PORT` and host port `-3000}`, so the
   control failed on CI. A new library, `libraries/compose_ports.rb`, expands `${VAR}` and
   `${VAR:-default}` the way Compose does (the variable if set and non-empty, else the
   default) before splitting, and the control calls it.

## Verification Strategy

| Criterion | Evidence | How |
| --- | --- | --- |
| Defaults unchanged | Ports 3000 and 5001 are still published when nothing is set | `docker compose --profile '*' config` with the default `.env.example` |
| Overrides take effect | `GRAFANA_PORT=3300` publishes 3300 | same command with the variable set |
| Compose declares configurable ports | Both mappings use `${VAR:-default}` and `.env.example` documents the variables | `tests/unit/test_compose_host_ports.py` |
| The InSpec control reads variables correctly | Plain, loopback, default, set, empty and loopback-with-variable mappings parse to the right IP and ports | `tests/unit/test_inspec_compose_ports.py` (written first, red, then green) |
| Nothing else changed in the control | The 16 other mappings in `compose.yaml` parse identically to the old splitter; only the two new ones differ | a one-off comparison run before the fix was committed |
| The real conformance run | `Conformance Tests (InSpec)` passes on this PR | CI |
| Not covered | A conformance run against a stack started with non-default ports | the run needs the same variables in its environment; `ComposePorts.expand` reads `ENV` |
