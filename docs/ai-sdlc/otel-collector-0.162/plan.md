# Plan: bump otel-collector-contrib to 0.162.0

**Traces to:** #474 (clear fixable CRITICAL trivy findings so the image-scan gate can block)

## Changes

1. `compose.yaml`: `otel/opentelemetry-collector-contrib` 0.120.0 → 0.162.0, digest-pinned.
   0.120.0 carried fixable CRITICALs in pgx, amqp091-go, grpc and the Go stdlib.
2. `config/otel/collector.yaml`: two upstream removals forced a config migration.
   - The `loki` exporter no longer exists; logs now go through `otlphttp/loki`
     to Loki's native `http://loki:3100/otlp`.
   - `service.telemetry.metrics.address` is replaced by a `readers.pull.prometheus`
     reader on `0.0.0.0:8888`, keeping the self-metrics port unchanged.
3. Test pins, living docs and the obs-stack/otel-collector skills updated to match.

## Verification Strategy

| Criterion                          | Evidence                                                          | How                                                                                   |
| ---------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Image has no fixable CRITICAL CVEs | trivy reports none                                                | `trivy image --severity CRITICAL --ignore-unfixed --exit-code 1` on the pinned image  |
| Config is valid on the new version | `validate` exits 0                                                | `docker run … validate --config=/etc/otel/config.yaml`                                |
| Logs still reach Loki              | An OTLP log POSTed to the collector is queryable as `{service_name="smoke"}` | Temp-network smoke test with collector 0.162.0 + Loki 3.6.17                  |
| Self-metrics still served          | `:8888/metrics` returns 200                                       | Same smoke test                                                                       |
| Compose and pins consistent        | `docker compose config` valid; version-pin tests pass             | `docker compose config -q`; CI unit and acceptance jobs                               |
| Not covered                        | Dashboards/alerts keyed on the old log label names                | Labels change to `service_name`/`severity_text`/`detected_level`; flagged in the PR   |
