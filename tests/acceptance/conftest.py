"""
Pytest configuration for uFawkesObs acceptance tests.

Provides shared fixtures, pytest-bdd markers, and step definition imports.
Step definition modules are imported here so pytest-bdd can discover their
fixtures. Since pytest only scans conftest.py and test modules for fixtures,
we re-publish step fixture names into conftest.py's namespace.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Iterator, Optional

import pytest
import requests

from tests.acceptance.runtime import (
    ObservabilityStack,
    GrafanaClient,
    LokiClient,
    OTLPClient,
    PromQLClient,
    SERVICE_HEALTH_URLS,
)

# ── Import step definitions ─────────────────────────────────────────
# Import modules first so their @given/@when/@then decorators fire.
# Then re-publish step fixtures in conftest.py's namespace so pytest's
# fixture discovery can find them.

import tests.acceptance.steps.shared_steps as _shared_steps
import tests.acceptance.steps.otel_steps as _otel_steps
import tests.acceptance.steps.loki_steps as _loki_steps
import tests.acceptance.steps.alertmanager_steps as _alertmanager_steps
import tests.acceptance.steps.dashboard_steps as _dashboard_steps

for _step_mod in [
    _shared_steps,
    _otel_steps,
    _loki_steps,
    _alertmanager_steps,
    _dashboard_steps,
]:
    for _name in dir(_step_mod):
        if _name.startswith("pytestbdd_stepdef_") or _name.startswith(
            "pytestbdd_stepimpl_"
        ):
            globals()[_name] = getattr(_step_mod, _name)


# ──────────────────────────────────────────────────────────────────────
# Pytest-bdd markers
# ──────────────────────────────────────────────────────────────────────


def pytest_configure(config):
    """Register custom markers for acceptance test levels."""
    config.addinivalue_line(
        "markers", "smoke: Fast pre-merge smoke tests (target: <3 min total)"
    )
    config.addinivalue_line(
        "markers", "full: Comprehensive post-merge SLO and contract tests"
    )
    config.addinivalue_line("markers", "chaos: Nightly chaos/failure injection tests")
    config.addinivalue_line("markers", "contract: Cross-plane telemetry contract tests")


def pytest_addoption(parser):
    """Add custom CLI options."""
    parser.addoption(
        "--stack-mode",
        action="store",
        default="auto",
        choices=["auto", "existing", "none"],
        help="How to manage the Docker Compose stack: 'auto' (start if not running), "
        "'existing' (use already running stack, no lifecycle mgmt), "
        "'none' (no stack at all, for unit-like checks)",
    )
    parser.addoption(
        "--evidence-dir",
        action="store",
        default=None,
        help="Directory to store test evidence artifacts",
    )


# ──────────────────────────────────────────────────────────────────────
# Session-scoped fixtures
# ──────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def stack(request) -> Iterator[ObservabilityStack]:
    """Provide an ObservabilityStack instance with lifecycle management.

    By default, starts the stack if not already running (auto mode).
    Use `--stack-mode=existing` to skip lifecycle management when
    running tests against a manually started stack.
    """
    mode = request.config.getoption("--stack-mode")
    evidence_dir = request.config.getoption("--evidence-dir")

    stack_instance = ObservabilityStack()

    if evidence_dir:
        stack_instance.set_evidence_dir(Path(evidence_dir))

    if mode == "auto":
        # Check if stack is already running or needs to be started
        try:
            resp = requests.get("http://localhost:9090/-/healthy", timeout=3)
            if resp.status_code == 200:
                print("✅ Stack appears to be running (Prometheus healthy)")
            else:
                print("⚠️  Stack may not be running — starting...")
                health = stack_instance.start()
                print(health.summary())
        except requests.RequestException:
            print("🚀 Starting stack (no existing stack detected)...")
            health = stack_instance.start()
            print(health.summary())

    yield stack_instance

    if mode == "auto":
        # Only stop if we started the stack
        print("🛑 Stopping stack (auto mode cleanup)...")
        stack_instance.stop()


@pytest.fixture(scope="session")
def wait_for_stack(stack: ObservabilityStack) -> None:
    """Wait for all stack services to be healthy.

    This fixture should be requested by any test that depends on the
    full stack being operational.
    """
    health = stack.wait_for_healthy()
    assert health.all_healthy, f"Stack not healthy:\n{health.summary()}"
    print(health.summary())

    # Extra settling time for all services to stabilize
    time.sleep(10)


# ──────────────────────────────────────────────────────────────────────
# Function-level fixtures
# ──────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def stack_healthy(request) -> bool:
    """Quick health check: are all services responsive?

    This is a lightweight check (not a full wait) for tests that
    need to validate per-request health.
    """
    for url in SERVICE_HEALTH_URLS.values():
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code != 200:
                return False
        except requests.RequestException:
            return False
    return True


@pytest.fixture(scope="function")
def promql(stack: ObservabilityStack) -> PromQLClient:
    """Get a PromQL client."""
    return stack.promql()


@pytest.fixture(scope="function")
def loki_client(stack: ObservabilityStack) -> LokiClient:
    """Get a Loki client."""
    return stack.loki()


@pytest.fixture(scope="function")
def grafana(stack: ObservabilityStack) -> GrafanaClient:
    """Get a Grafana client."""
    return stack.grafana()


@pytest.fixture(scope="function")
def otlp(stack: ObservabilityStack) -> OTLPClient:
    """Get an OTLP client for sending test telemetry."""
    return stack.otlp()


# ──────────────────────────────────────────────────────────────────────
# CLI option access
# ──────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def evidence_dir(request) -> Optional[Path]:
    """Get the evidence directory path from CLI options."""
    path = request.config.getoption("--evidence-dir")
    if path:
        return Path(path)
    return None
