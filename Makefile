.PHONY: help init check-env up up-apps up-dora up-full down logs status grafana-folder-descriptions validate-configs test-unit test-integration test-conformance test-acceptance test-acceptance-smoke test-acceptance-full test-acceptance-chaos install-acceptance-deps install-integration-deps test ci-local pr lint-tools lint-workflows lint-dockerfiles validate-alertmanager validate-alloy scan-images release-preview

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
	pip install -q -r tests/acceptance/requirements.lock

## install-integration-deps: install integration test Python dependencies
install-integration-deps:
	pip install -q -r tests/integration/requirements.lock

## test-unit: run unit tests only
test-unit:
	pip install -q -r tests/unit/requirements.lock
	pytest tests/unit/ --cov=dora --cov-report=term-missing --cov-report=html:reports/coverage

## relock: regenerate every requirements.lock from its source
##   requirements*.txt in a clean venv. Run after editing any source file;
##   commit the regenerated lock alongside it. See docs/DETERMINISM.md.
relock:
	@set -e; \
	for src in tests/unit/requirements.txt tests/integration/requirements.txt tests/acceptance/requirements.txt dora/compute/requirements.txt dora/ingestion/requirements-ingestion.txt; do \
		out="$${src%.txt}"; \
		if [ "$$src" = "dora/ingestion/requirements-ingestion.txt" ]; then out="dora/ingestion/requirements-ingestion"; fi; \
		echo "🔒 Relocking $$src -> $$out.lock"; \
		venv=$$(mktemp -d); \
		python3 -m venv "$$venv"; \
		"$$venv/bin/pip" install -q --upgrade pip; \
		"$$venv/bin/pip" install -q -r "$$src"; \
		"$$venv/bin/pip" freeze | grep -viE '^pip==|^setuptools==|^wheel==' | sort > "$$out.lock.new"; \
		{ head -n $$(grep -n '^# Generated:' "$$out.lock" | head -1 | cut -d: -f1) "$$out.lock" | sed "s/^# Generated:.*/# Generated: $$(date -u +%Y-%m-%d)/"; cat "$$out.lock.new"; } > "$$out.lock.tmp"; \
		mv "$$out.lock.tmp" "$$out.lock"; \
		rm -f "$$out.lock.new"; \
		rm -rf "$$venv"; \
	done; \
	echo "✅ All lock files regenerated — review the diff and commit"

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

## test-conformance: run the InSpec profile (inspec/ufawkesobs-conformance)
##   against the live stack's actually-running containers -- checks health
##   status, port bindings, image digests, and volume types match
##   compose.yaml (AGENTS.md §4). Requires 'make up' first. Not CI-gated yet
##   (#414/#415) -- run manually; services from profiles you haven't started
##   are reported skipped, not failed.
test-conformance:
	@echo "========================================"
	@echo "🟤 Conformance Tests (InSpec, AGENTS.md §4)"
	@echo "========================================"
	@set -e; \
	tmpbin=$$(mktemp -d); \
	trap 'rm -rf "$$tmpbin"' EXIT; \
	cid=$$(docker create docker:27-cli@sha256:851f91d241214e7c6db86513b270d58776379aacc5eb9c4a87e5b47115e3065c); \
	docker cp "$$cid:/usr/local/bin/docker" "$$tmpbin/docker"; \
	docker rm "$$cid" > /dev/null; \
	chmod +x "$$tmpbin/docker"; \
	docker run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v "$$tmpbin/docker:/usr/local/bin/docker:ro" \
		-v $(PWD)/compose.yaml:/compose.yaml:ro \
		-v $(PWD)/inspec/ufawkesobs-conformance:/profile \
		chef/inspec:5.22.3@sha256:46b3152c0a70b4235ff732fe1013712353b6a5efb40e4ea10334242bb539a8bb \
		exec /profile --chef-license=accept-silent --no-distinct-exit

# Match CI's DORA compute cadence. compose.yaml defaults
# DORA_COMPUTE_INTERVAL_SECONDS to 3600, while ci-acceptance-full.yml sets 15 --
# so a locally-run acceptance suite waited up to an hour for a seeded DORA event
# to reach the dashboard where CI waited fifteen seconds, making the documented
# local path quietly racier than the gate it is meant to rehearse (#359).
# Exported, not passed inline: the value has to reach the dora-api container.
export DORA_COMPUTE_INTERVAL_SECONDS ?= 15

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

# ─── Extra lint / scan / release tooling ────────────────────────────────────
# Not wired into CI. Binaries (actionlint, hadolint, trivy, yq) come from
# .devcontainer/install-tools.sh; config validators run the exact image
# compose.yaml pins, read with yq so the two can't drift.
require = @command -v $(1) >/dev/null || { echo "❌ $(1) not found -- run .devcontainer/install-tools.sh"; exit 1; }
compose_image = $(shell yq -r '.services.$(1).image' compose.yaml)

## lint-tools: run lint-workflows, lint-dockerfiles, validate-alertmanager, validate-alloy
lint-tools: lint-workflows lint-dockerfiles validate-alertmanager validate-alloy

## lint-workflows: lint GitHub Actions workflows with actionlint (+ shellcheck warnings on run: blocks)
lint-workflows:
	$(call require,actionlint)
	SHELLCHECK_OPTS="--severity=warning" actionlint

## lint-dockerfiles: lint every Dockerfile with hadolint (prints all, fails on errors)
lint-dockerfiles:
	$(call require,hadolint)
	git ls-files '*Dockerfile*' | xargs hadolint --no-color --failure-threshold error

## validate-alertmanager: amtool check-config using compose.yaml's alertmanager image
validate-alertmanager:
	$(call require,yq)
	docker run --rm --entrypoint amtool \
		-v $(PWD)/config/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro \
		$(call compose_image,alertmanager) check-config /etc/alertmanager/alertmanager.yml

## validate-alloy: parse the Alloy config with compose.yaml's alloy image
validate-alloy:
	$(call require,yq)
	docker run --rm -v $(PWD)/config/alloy/config.river:/etc/alloy/config.river:ro \
		$(call compose_image,alloy) fmt /etc/alloy/config.river > /dev/null
	@echo "✅ config.river parses"

## scan-images: trivy scan of every compose.yaml image (HIGH/CRITICAL, report only)
scan-images:
	$(call require,yq)
	$(call require,trivy)
	yq -r '.services[].image | select(. != null)' compose.yaml | sort -u | \
		while read -r img; do \
			echo "── $$img"; \
			trivy image --quiet --severity HIGH,CRITICAL --ignore-unfixed "$$img" || exit 1; \
		done

## release-preview: dry-run release-please -- shows the next release PR without creating it
release-preview:
	$(call require,gh)
	npx -y release-please@17.11.2 release-pr --dry-run \
		--token="$$(gh auth token)" --repo-url=paruff/uFawkesObs \
		--config-file=release-please-config.json \
		--manifest-file=.release-please-manifest.json
