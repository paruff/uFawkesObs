"""Unit tests for the acceptance-test DORA event workload generator.

Regression coverage for the OBS-SLI-006 investigation: the previous
tests/acceptance/workloads/dora_events.py sent OTLP trace spans (via
DORAWorkload) that never reached uFawkesObs's own dora/ingestion REST API
-- the same "OTLP instead of REST" mismatch found and fixed in uFawkesPipe
PR #70 -- and was never actually invoked by any scenario (dead code). These
tests pin the replacement: a REST payload that validates against the real
deployment-event.schema.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from tests.acceptance.workloads.dora_events import build_deployment_event

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "dora" / "events" / "deployment-event.schema.json"


@pytest.fixture(scope="module")
def deployment_schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


class TestBuildDeploymentEvent:
    def test_validates_against_deployment_event_schema(
        self, deployment_schema: dict
    ) -> None:
        event = build_deployment_event()
        jsonschema.validate(event, deployment_schema)

    def test_defaults_to_success_status(self) -> None:
        event = build_deployment_event()
        assert event["status"] == "success"

    def test_honors_overrides(self) -> None:
        event = build_deployment_event(
            repo="paruff/example",
            service="checkout",
            environment="staging",
            status="failed",
        )
        assert event["repo"] == "paruff/example"
        assert event["service"] == "checkout"
        assert event["environment"] == "staging"
        assert event["status"] == "failed"

    def test_rejects_invalid_status_at_schema_validation(
        self, deployment_schema: dict
    ) -> None:
        event = build_deployment_event(status="not-a-real-status")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(event, deployment_schema)
