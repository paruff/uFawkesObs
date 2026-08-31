.PHONY: help init check-env up up-apps up-dora up-full down logs status grafana-folder-descriptions validate-configs test-unit test-integration test-acceptance test-acceptance-smoke test-acceptance-full test-acceptance-chaos install-acceptance-deps install-integration-deps test ci-local pr

# Grafana runs as UID 472
GRAFANA_UID := 472
# Prometheus and Alertmanager run as nobody (UID 65534)
NOBODY_UID := 65534
# Loki and Tempo run as UID 10001
LGTM_UID := 10001

## help: print this help message
help:
	@grep -E '^## [a-z]' Makefile | sed 's/^## //' | awk -F': ' '{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

## init: create data directories with mode 755 and print required chown commands
init:
	@echo "Creating data directories (mode 755) — run the chown commands printed below to set ownership..."
	install -d -m 755 data/grafana
	install -d -m 755 data/prometheus
	install -d -m 755 data/alertmanager
	install -d -m 755 data/loki
	install -d -m 755 data/tempo
	install -d -m 755 data/alloy
	# ponytail: dora-api/dora-compute run as a system-assigned (non-fixed)
	# UID, so 777 avoids a per-build UID lookup for one local SQLite file;
	# tighten with a documented UID if this ever needs to be more locked down.
	install -d -m 777 data/dora
	@echo ""
	@echo "⚠️  On Linux, if containers cannot write to data/ directories, run:"
	@echo "   sudo chown -R $(GRAFANA_UID) data/grafana         # Grafana UID"
	@echo "   sudo chown -R $(NOBODY_UID) data/prometheus data/alertmanager  # nobody UID"
	@echo "   sudo chown -R $(LGTM_UID) data/loki data/tempo   # Loki/Tempo UID"
	@echo "   (Alloy mounts data/alloy as root; no chown needed)"
	@echo ""
	@echo "✅ data/ directories ready"

## check-env: validate required environment variables
check-env:
	./scripts/check-env.sh

## up: start the core observability stack
up: check-env
	docker compose --profile core up -d

## up-apps: start the core stack plus demo telemetry generator
up-apps: check-env
	docker compose --profile core --profile apps up -d

## up-dora: start the core stack plus DORA metrics (self-contained, SQLite-only)
up-dora: check-env
	docker compose --profile core --profile dora up -d

## up-full: start core + apps + dora together -- matches Acceptance Full
## (Post-Merge) in CI exactly; use this before 'make test-acceptance-full'
up-full: check-env
	docker compose --profile core --profile apps --profile dora up -d

## down: stop all services
down:
	docker compose down

## logs: tail logs for all running services
logs:
	docker compose logs -f

## status: show running containers and health endpoints
status:
	docker compose ps
	@echo ""
	@echo "Health endpoints:"
	@curl -sf http://localhost:9090/-/ready  > /dev/null && echo "  ✅ Prometheus  :9090" || echo "  ❌ Prometheus  :9090"
	@curl -sf http://localhost:3200/ready    > /dev/null && echo "  ✅ Tempo       :3200" || echo "  ❌ Tempo       :3200"
	@curl -sf http://localhost:3100/ready    > /dev/null && echo "  ✅ Loki        :3100" || echo "  ❌ Loki        :3100"
	@curl -sf http://localhost:3000/api/health > /dev/null && echo "  ✅ Grafana     :3000" || echo "  ❌ Grafana     :3000"
	@curl -sf http://localhost:9093/-/healthy > /dev/null && echo "  ✅ Alertmanager:9093" || echo "  ❌ Alertmanager:9093"
	@curl -sf http://localhost:8888/metrics > /dev/null && echo "  ✅ OTel Coll.  :8888" || echo "  ❌ OTel Coll.  :8888"
	@curl -sf http://localhost:12345/-/ready > /dev/null && echo "  ✅ Alloy       :12345" || echo "  ❌ Alloy       :12345"

## grafana-folder-descriptions: label dashboard folders (Platform/Services
## maintained, Application legacy) -- run once after `make up`
grafana-folder-descriptions:
	set -a && . ./.env && set +a && ./scripts/set-grafana-folder-descriptions.sh

## validate-configs: validate Prometheus/OTel/Tempo config files with each
##   tool's own binary via pinned Docker images -- mirrors Quality &
##   Security Gates / Validate Configs in CI exactly. Requires Docker only,
##   no stack needs to be running.
validate-configs:
	@echo "========================================"
	@echo "🟡 Config Validation (Prometheus/OTel/Tempo)"
	@echo "========================================"
	docker run --rm -v $(PWD)/config/prometheus:/etc/prometheus \
		--entrypoint promtool prom/prometheus:v3.5.4 \
		check config /etc/prometheus/prometheus.yaml
	docker run --rm -v $(PWD)/config/otel/collector.yaml:/etc/otel/config.yaml \
		otel/opentelemetry-collector-contrib:0.120.0 \
		validate --config=/etc/otel/config.yaml
	docker run --rm -v $(PWD)/config/tempo/tempo.yaml:/etc/tempo.yaml \
		grafana/tempo:2.4.1 \
		-config.file=/etc/tempo.yaml -config.verify=true
	@echo "✅ All configs valid"

## install-acceptance-deps: install acceptance test Python dependencies
install-acceptance-deps:
	pip install -q -r tests/acceptance/requirements.txt

## install-integration-deps: install integration test Python dependencies
install-integration-deps:
	pip install -q -r tests/integration/requirements.txt

## test-unit: run unit tests only
test-unit:
	pip install -q -r tests/unit/requirements.txt
	pytest tests/unit/

## test-integration: run real component integration tests (Prometheus
##   scraping, OTel Collector, Grafana, Tempo, Loki, dashboards) against a
##   live stack -- mirrors Unit & Integration Tests / Integration Tests in
##   CI. Requires 'make up' first.
test-integration: install-integration-deps
	@echo "========================================"
	@echo "🟠 Integration Tests"
	@echo "========================================"
	PROMETHEUS_URL=http://localhost:9090 \
	OTEL_METRICS_URL=http://localhost:8888 \
	GRAFANA_URL=http://localhost:3000 \
	GRAFANA_USER=admin \
	GRAFANA_PASSWORD=admin \
	TEMPO_URL=http://localhost:3200 \
	LOKI_URL=http://localhost:3100 \
	pytest tests/integration/ -v --tb=short

## test-acceptance-smoke: run smoke acceptance tests via pytest-bdd (fast, pre-merge)
##   Requires stack to be running (run 'make up' first)
##   Use --stack-mode=existing to skip lifecycle management
test-acceptance-smoke: install-acceptance-deps
	@echo "========================================"
	@echo "🟢 Acceptance Smoke Tests (pre-merge)"
	@echo "========================================"
	@pytest tests/acceptance/ -m "smoke" -v --tb=short --stack-mode=existing

## test-acceptance-full: run full acceptance tests via pytest-bdd (comprehensive, post-merge)
##   Requires 'make up-full' first (core + apps + dora, matching CI exactly)
test-acceptance-full: install-acceptance-deps
	@echo "========================================"
	@echo "🟣 Acceptance Full Tests (post-merge)"
	@echo "========================================"
	@pytest tests/acceptance/ -m "full" -v --tb=short --stack-mode=existing \
		--evidence-dir=tests/acceptance/reports/full

## test-acceptance-chaos: run chaos resilience tests via pytest-bdd
##   Requires stack to be running (run 'make up' first) -- mirrors
##   Chaos Resilience (Nightly) in CI. Kills/restarts real containers.
test-acceptance-chaos: install-acceptance-deps
	@echo "========================================"
	@echo "🔴 Chaos Resilience Tests"
	@echo "========================================"
	@pytest tests/acceptance/ -m "chaos" -v --tb=short --stack-mode=existing \
		--evidence-dir=tests/acceptance/reports/chaos

## test-acceptance: run all acceptance tests via pytest-bdd (manual/local use)
##   ⚠️  Legacy shell scripts are deprecated and will be removed in a future release
test-acceptance: install-acceptance-deps
	@echo "========================================"
	@echo "🔵 Acceptance Test Suite (pytest-bdd)"
	@echo "========================================"
	@pytest tests/acceptance/ -m "smoke or full" -v --tb=short --stack-mode=existing

## test: run unit tests then acceptance tests (requires stack to be running: make up)
test: test-unit test-acceptance

## ci-local: run the fast pyramid locally in CI order -- pre-commit, config
##   validation, unit tests, integration tests, acceptance smoke. Requires
##   'make up' first (integration/smoke need a live stack). Doesn't include
##   Acceptance Full or Chaos (slow, deliberately post-merge/nightly only in
##   CI) -- run those explicitly via test-acceptance-full/test-acceptance-chaos
##   when you actually want them.
ci-local: pre-commit-run validate-configs test-unit test-integration test-acceptance-smoke
	@echo ""
	@echo "✅ Local pyramid passed -- matches Repo Hygiene, Quality & Security"
	@echo "   Gates, Unit & Integration Tests, and Acceptance Smoke in CI."

# GitOps targets
pre-commit-setup: ## Install pre-commit hooks
	@pip install pre-commit
	@pre-commit install
	@pre-commit install --hook-type commit-msg
	@echo "✅ Pre-commit hooks installed (pre-commit + commit-msg)"

pre-commit-run: ## Run all pre-commit hooks
	@pre-commit run --all-files

## pr: stage, commit (with pre-commit), push, and create a PR
##   Usage: make pr MSG="fix(prometheus): correct scrape interval"
##          make pr                                          # auto-generate message
pr:
	./scripts/pr-create.sh "$(MSG)"
