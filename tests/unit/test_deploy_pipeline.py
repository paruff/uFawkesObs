"""
Unit tests guarding the LB-04 rollback drill wiring (#182).

These tests lock in the conditions in `.github/workflows/deploy.yml` that the
rollback drill in `docs/ROLLBACK_DRILL.md` depends on:

* a bad `config/otel/**` (or `config/alertmanager/**`) commit is classified as
  `non_reloadable_config`, so it takes the `deploy-compose-restart` path rather
  than the config-reload path;
* `deploy-compose-restart` requires the `compose-restart` environment approval;
* `post-deploy-verify` probes the host health script with a bounded timeout;
* the `rollback` job fires only when `post-deploy-verify` fails, is pinned to a
  released `reusable-rollback` workflow, and receives all four deploy secrets.

Run:  pytest tests/unit/test_deploy_pipeline.py -v
      (no running stack required — reads YAML statically)
"""

from __future__ import annotations

import pathlib
import re
from typing import Any

import pytest
import yaml

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEPLOY_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "deploy.yml"

REUSABLE_ROLLBACK_PREFIX = "paruff/ufawkespipe/.github/workflows/reusable-rollback.yml@"

REQUIRED_DEPLOY_SECRETS: tuple[str, ...] = (
    "DEPLOY_HOST",
    "DEPLOY_USER",
    "DEPLOY_KEY",
    "DEPLOY_HOST_KEY",
)

PINNED_REF_RE = re.compile(r"(?:v[0-9]+\.[0-9]+\.[0-9]+|[0-9a-f]{40})$")

BAD_DRILL_PATHS: tuple[str, ...] = (
    "config/otel/collector.yaml",
    "config/alertmanager/alertmanager.yml",
)


def _load_workflow(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        pytest.fail(f"Expected file not found: {path}")
    text = path.read_text(encoding="utf-8")
    doc = yaml.safe_load(text)
    if True in doc:  # PyYAML 1.1 parses the GitHub `on:` key as boolean True
        doc["on"] = doc.pop(True)
    return doc


def _glob_to_regex(pattern: str) -> str:
    """Translate a glob supporting `**` (crossing directories) to a regex."""
    out: list[str] = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "*":
            if i + 1 < len(pattern) and pattern[i + 1] == "*":
                if i + 2 < len(pattern) and pattern[i + 2] == "/":
                    out.append("(?:[^/]+/)*")
                    i += 3
                else:
                    out.append("(?:.*)")
                    i += 2
            else:
                out.append("[^/]*")
                i += 1
        elif ch == "?":
            out.append("[^/]")
            i += 1
        elif ch == "[":
            end = pattern.find("]", i)
            if end != -1:
                out.append(pattern[i : end + 1])
                i = end + 1
            else:
                out.append("\\[")
                i += 1
        else:
            out.append(re.escape(ch))
            i += 1
    return "".join(out)


def _in_group(patterns: list[str], path: str) -> bool:
    """Return whether `path` matches a dorny/paths-filter group's patterns."""
    matched = False
    for raw in patterns:
        negated = raw.startswith("!")
        pattern = raw[1:] if negated else raw
        hit = re.fullmatch(_glob_to_regex(pattern), path) is not None
        if negated and hit:
            return False
        matched = matched or hit
    return matched


@pytest.fixture(scope="module")
def deploy_workflow() -> dict[str, Any]:
    """Return the parsed GitOps Reconciliation Deploy workflow."""
    return _load_workflow(DEPLOY_WORKFLOW_PATH)


@pytest.fixture(scope="module")
def path_filters(
    deploy_workflow: dict[str, Any],
) -> dict[str, list[str]]:
    """Return the detect-changes path-filter groups as name to patterns."""
    steps = deploy_workflow["jobs"]["detect-changes"]["steps"]
    filter_step = next(step for step in steps if step.get("id") == "filter")
    filters_block: str = filter_step["with"]["filters"]
    return yaml.safe_load(filters_block)


class TestDeployTrigger:
    """Deploy must be driven solely by the post-merge acceptance gate (LB-05).

    The former `push` trigger dispatched runs whose deploy secrets were always
    unavailable (see #183), so it only produced red runs. The authoritative
    deploy now fires from the `workflow_run` event of the Acceptance Full
    (Post-Merge) workflow.
    """

    def test_deploy_has_no_push_trigger(self, deploy_workflow: dict[str, Any]) -> None:
        assert "push" not in deploy_workflow["on"], (
            "deploy.yml must not trigger on push — push-triggered runs always "
            "failed with empty deploy secrets (#183)"
        )

    def test_deploy_is_gated_on_acceptance_full(
        self, deploy_workflow: dict[str, Any]
    ) -> None:
        run = deploy_workflow["on"]["workflow_run"]
        assert "Acceptance Full (Post-Merge)" in run["workflows"]
        assert "completed" in run["types"]
        assert "main" in run["branches"]


class TestRollbackWiring:
    """The drill's core assertion: post-deploy-verify failure fires rollback."""

    def test_rollback_requires_post_deploy_verify(
        self, deploy_workflow: dict[str, Any]
    ) -> None:
        job = deploy_workflow["jobs"]["rollback"]
        needs = job.get("needs", [])
        if isinstance(needs, str):
            needs = [needs]
        assert "post-deploy-verify" in needs

    def test_rollback_fires_only_when_verify_fails(
        self, deploy_workflow: dict[str, Any]
    ) -> None:
        condition = deploy_workflow["jobs"]["rollback"].get("if", "")
        assert "failure()" in condition
        assert "needs.post-deploy-verify.result" in condition
        assert "'failure'" in condition

    def test_rollback_uses_pinned_reusable_workflow(
        self, deploy_workflow: dict[str, Any]
    ) -> None:
        uses = deploy_workflow["jobs"]["rollback"].get("uses", "")
        assert uses.startswith(REUSABLE_ROLLBACK_PREFIX), (
            f"Unexpected rollback workflow: {uses}"
        )
        ref = uses.rsplit("@", 1)[-1]
        assert PINNED_REF_RE.search(ref), f"Rollback workflow ref not pinned: {ref}"

    def test_rollback_receives_all_deploy_secrets(
        self, deploy_workflow: dict[str, Any]
    ) -> None:
        secrets = deploy_workflow["jobs"]["rollback"].get("secrets", {})
        assert secrets, "rollback job must forward deploy secrets"
        for name in REQUIRED_DEPLOY_SECRETS:
            value = secrets.get(name, "")
            assert name in value, f"rollback job missing secret {name}"

    def test_rollback_restarts_with_make_up(
        self, deploy_workflow: dict[str, Any]
    ) -> None:
        restart = deploy_workflow["jobs"]["rollback"]["with"]["restart-command"]
        assert "make up" in restart


class TestPostDeployVerify:
    """The drill relies on post-deploy-verify being a real, bounded health gate."""

    def test_verify_waits_for_a_deploy_job(
        self, deploy_workflow: dict[str, Any]
    ) -> None:
        verify = deploy_workflow["jobs"]["post-deploy-verify"]
        assert {"deploy-config-reload", "deploy-compose-restart"} <= set(
            verify["needs"]
        )
        assert "always()" in verify.get("if", "")

    def test_verify_has_bounded_timeout(self, deploy_workflow: dict[str, Any]) -> None:
        timeout = deploy_workflow["jobs"]["post-deploy-verify"].get("timeout-minutes")
        assert timeout is not None and int(timeout) > 0

    def test_verify_probes_host_health_script(
        self, deploy_workflow: dict[str, Any]
    ) -> None:
        steps = deploy_workflow["jobs"]["post-deploy-verify"]["steps"]
        joined = "\n".join(str(step) for step in steps)
        assert "wait-healthy.sh" in joined
        assert "localhost:8888" in joined


class TestDrillPathClassification:
    """The drill's bad-deploy recipe must hit the compose-restart path."""

    @pytest.mark.parametrize("bad_path", BAD_DRILL_PATHS)
    def test_bad_config_is_non_reloadable(
        self,
        deploy_workflow: dict[str, Any],
        path_filters: dict[str, list[str]],
        bad_path: str,
    ) -> None:
        assert _in_group(path_filters["non_reloadable_config"], bad_path)
        assert not _in_group(path_filters["reload"], bad_path)
        assert not _in_group(path_filters["compose"], bad_path)

    def test_bad_config_triggers_compose_restart_environment(
        self, deploy_workflow: dict[str, Any]
    ) -> None:
        job = deploy_workflow["jobs"]["deploy-compose-restart"]
        assert job.get("environment") == "compose-restart"
        assert "non_reloadable_config_changed" in job.get("if", "")

    def test_prometheus_stays_on_config_reload_path(
        self, path_filters: dict[str, list[str]]
    ) -> None:
        known_path = "config/prometheus/prometheus.yml"
        assert _in_group(path_filters["reload"], known_path)
        assert not _in_group(path_filters["non_reloadable_config"], known_path)
