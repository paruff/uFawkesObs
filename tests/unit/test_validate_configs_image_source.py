"""Regression tests for config-validator image source consistency."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE_PATH = REPO_ROOT / "Makefile"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ci-quality.yml"


def test_makefile_validate_configs_uses_compose_image_macro() -> None:
    content = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert (
        "compose_image = $(shell yq -r '.services[\"$(1)\"].image' compose.yaml)"
        in content
    )
    assert "$(call require,yq)" in content
    assert "$(call compose_image,prometheus)" in content
    assert "$(call compose_image,otel-collector)" in content
    assert "$(call compose_image,tempo)" in content
    assert "grafana/tempo:2.4.1" not in content


def test_ci_validate_configs_uses_images_derived_from_compose() -> None:
    content = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "Resolve validator images from compose.yaml" in content
    assert (
        "docker compose --env-file .env.example --profile '*' config --format json"
        in content
    )
    assert ".services.prometheus.image" in content
    assert '.services["otel-collector"].image' in content
    assert ".services.tempo.image" in content
    assert '"$PROMETHEUS_IMAGE"' in content
    assert '"$OTEL_IMAGE"' in content
    assert '"$TEMPO_IMAGE"' in content
    assert "grafana/tempo:2.4.1" not in content
