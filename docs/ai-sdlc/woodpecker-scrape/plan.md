# Plan: scrape Woodpecker /metrics and add a community dashboard

**Traces to:** #740

## Changes

1. `woodpecker` scrape job (dns_sd, suite mode only) in `config/prometheus/prometheus.yaml`, authenticated with a bearer token file.
2. The token file is `config/prometheus/woodpecker_metrics_token`, an empty committed placeholder. Compose mounts `WOODPECKER_METRICS_TOKEN_FILE` over it when set. It lives beside the config because the shared build job runs `promtool check config` with only `config/prometheus` mounted, so a path elsewhere fails validation.
3. `dashboards/platform/woodpecker.json` community dashboard; `.env.example` documents the variable.

## Verification Strategy

| Criterion | Evidence | How |
| --- | --- | --- |
| Config validates as CI runs it | promtool prints SUCCESS | `docker run --rm -v $PWD/config/prometheus:/etc/prometheus --entrypoint promtool prom/prometheus:v2.55.1 check config /etc/prometheus/prometheus.yaml` |
| Compose still resolves with the variable unset | exit 0 | `docker compose config -q` |
| Dashboard and config gates pass | exit 0 | `make lint-config` |
| Repo checks pass | CI green | `pre-commit run --all-files`; PR checks |
| Not covered | Scraping a live Woodpecker server with a real token | Needs a uFawkesPipe suite deployment |
