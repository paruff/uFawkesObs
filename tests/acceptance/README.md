# Acceptance Testing — uFawkesObs

> See [tests/README.md](../README.md) for the test pyramid and marker
> taxonomy (which suite runs pre-merge vs. post-merge vs. nightly). This doc
> is the how-to for running acceptance tests yourself.

## Primary suite: pytest-bdd

The primary acceptance suite is pytest-bdd (15 feature files, 94 scenarios) and is what CI runs:

```bash
make up                      # stack must be running first
make test-acceptance-smoke   # fast, pre-merge
make test-acceptance-full    # comprehensive, post-merge (SLOs and contracts)
```

## Complementary check: OBS-ACCEPTANCE-001

`test-otel-pipeline.sh` walks the OTel → Prometheus → Grafana chain using
plain `curl`, with no Python client library in the path, so it catches
breakage the suite's clients would mask. It also runs in CI as part of
Acceptance Smoke.

```bash
make up
sleep 30
./tests/acceptance/observability-pipeline/test-otel-pipeline.sh
```

It validates:

1. **OpenTelemetry Collector** → Exports self-telemetry metrics
2. **Prometheus** → Scrapes and stores OTel Collector metrics
3. **Grafana** → Queries and visualizes metrics

Expected output:

```
✅ OTel Collector healthy (0s)
✅ Prometheus scraping OTel metrics (1s, 1 metrics)
✅ Grafana datasource configured (0s)
✅ SUCCESS: OTel metrics visible in Grafana
  Data points: 15
  Sample value: 123.456
========================================
✅ ACCEPTANCE TEST PASSED
========================================
```

### Manual verification

If you prefer to verify manually:

1. **Open Grafana**: http://localhost:3000 (credentials from `.env`)
2. **Navigate to**: Explore → Prometheus datasource
3. **Run Query**: `otelcol_process_uptime`
4. **Expected**: Graph showing uptime increasing over time

### Using the E2E runner

The E2E runner provides additional control over test execution:

```bash
# Run with automatic service detection
./tests/acceptance/e2e-runner.sh

# Force start services before testing
./tests/acceptance/e2e-runner.sh --start-services

# Run test and clean up after
./tests/acceptance/e2e-runner.sh --cleanup

# Quick health check only
./tests/acceptance/e2e-runner.sh --scenario quick-check
```

### Test results

Test results are saved in `tests/acceptance/observability-pipeline/reports/` with timestamped directories containing:

- `summary.md` - Human-readable test report
- `report.json` - Machine-readable results for CI/CD
- `e2e-test-evidence.md` - Detailed test evidence
- `grafana-query-response.json` - Raw Grafana API response
- `test-execution.log` - Complete execution log

### Troubleshooting

If tests fail, check:

1. **Services running**: `docker compose ps`
2. **OTel metrics**: `curl http://localhost:8888/metrics | grep otelcol`
3. **Prometheus target**: http://localhost:9090/targets
4. **Grafana health**: `curl http://localhost:3000/api/health`

### Running in your own CI

> **Note:** Add a repository secret named `GRAFANA_ADMIN_PASSWORD` in **GitHub → Settings → Secrets and variables → Actions** before running this workflow. Use a secure non-default value (not `admin`, `changeme`, or `REPLACE_ME_set_a_real_password_here`).

```yaml
# GitHub Actions example
jobs:
  observability-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run acceptance test
        env:
          GRAFANA_ADMIN_PASSWORD: ${{ secrets.GRAFANA_ADMIN_PASSWORD }}
        run: |
          mkdir -p data/prometheus data/grafana
          chmod -R 777 data/
          make up
          sleep 30
          ./tests/acceptance/observability-pipeline/test-otel-pipeline.sh
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: acceptance-test-report
          path: tests/acceptance/observability-pipeline/reports/**/summary.md
```

## Unit tests for configuration validation

The repository includes unit tests that validate configuration files for
all observability components — OpenTelemetry Collector, Prometheus,
Grafana, Tempo, and Loki — catching configuration errors before deployment.

```bash
pip install -r tests/unit/requirements.txt
pytest tests/unit/

# Or a specific component:
pytest tests/unit/test_otel_config_validation.py
pytest tests/unit/test_prometheus_config_validation.py
pytest tests/unit/test_grafana_config_validation.py
pytest tests/unit/test_tempo_config_validation.py
pytest tests/unit/test_loki_config_validation.py
```

What's validated: YAML syntax, required sections/fields, port ranges, URL
formats, time duration formats, component references, pipeline
configurations, and common misconfigurations. 239 tests total. See
[tests/unit/README.md](../unit/README.md) for detail.
