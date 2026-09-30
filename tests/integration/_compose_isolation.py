from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import yaml
from testcontainers.compose import DockerCompose


def _ephemeral_port_mappings(ports: list[Any]) -> list[str]:
    mapped_ports: list[str] = []
    for port in ports:
        if isinstance(port, str):
            port_spec, _, protocol = port.partition("/")
            container_port = port_spec.split(":")[-1].strip()
            if protocol and protocol != "tcp":
                mapped_ports.append(f"{container_port}/{protocol}")
            else:
                mapped_ports.append(container_port)
            continue

        if isinstance(port, dict):
            target = port.get("target")
            if target is None:
                continue
            protocol = port.get("protocol", "tcp")
            if protocol == "tcp":
                mapped_ports.append(str(target))
            else:
                mapped_ports.append(f"{target}/{protocol}")

    return mapped_ports


def _ephemeral_data_volume(volume: Any) -> Any:
    if isinstance(volume, str):
        parts = volume.split(":")
        if len(parts) >= 2 and parts[0].startswith("./data/"):
            rewritten: dict[str, Any] = {"type": "volume", "target": parts[1]}
            if len(parts) > 2 and "ro" in parts[2].split(","):
                rewritten["read_only"] = True
            return rewritten
        return volume

    if isinstance(volume, dict):
        source = str(volume.get("source", ""))
        mount_type = volume.get("type")
        if mount_type == "bind" and source.startswith("./data/"):
            rewritten = {"type": "volume", "target": volume["target"]}
            if volume.get("read_only"):
                rewritten["read_only"] = True
            return rewritten
        return volume

    return volume


def _write_isolated_compose_file(repo_root: pathlib.Path) -> str:
    compose_path = repo_root / "compose.yaml"
    compose_config = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    compose_config.pop("name", None)
    for service in compose_config.get("services", {}).values():
        service.pop("container_name", None)
        if "ports" in service:
            service["ports"] = _ephemeral_port_mappings(service["ports"])
        if "volumes" in service:
            service["volumes"] = [
                _ephemeral_data_volume(volume) for volume in service["volumes"]
            ]

    with tempfile.NamedTemporaryFile(
        "w", prefix=".testcontainers-isolated-", suffix=".yaml", dir=repo_root, delete=False
    ) as isolated_file:
        yaml.safe_dump(compose_config, isolated_file, sort_keys=False)
        return isolated_file.name


def _project_container_ids(project_name: str, services: list[str] | None = None) -> set[str]:
    command = [
        "docker",
        "ps",
        "-a",
        "--filter",
        f"label=com.docker.compose.project={project_name}",
        "--format",
        "{{.ID}} {{.Label \"com.docker.compose.service\"}}",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    service_filter = set(services or [])

    container_ids: set[str] = set()
    for line in result.stdout.splitlines():
        parts = line.strip().split(maxsplit=1)
        if not parts:
            continue
        container_id = parts[0]
        service_name = parts[1] if len(parts) > 1 else ""
        if service_filter and service_name not in service_filter:
            continue
        container_ids.add(container_id)
    return container_ids


@contextmanager
def isolated_compose(
    *,
    repo_root: pathlib.Path,
    env_file: str | None = None,
    profiles: list[str] | None = None,
    services: list[str] | None = None,
    protected_project: str = "ufawkesobs",
    protected_services: list[str] | None = None,
) -> Iterator[DockerCompose]:
    isolated_compose_file = _write_isolated_compose_file(repo_root)
    try:
        original_project_name = os.environ.get("COMPOSE_PROJECT_NAME")
        original_grafana_password = os.environ.get("GRAFANA_ADMIN_PASSWORD")
        original_slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")
        isolated_project_name = f"tc-{uuid.uuid4().hex[:10]}"
        protected_before = _project_container_ids(protected_project, protected_services)

        os.environ["COMPOSE_PROJECT_NAME"] = isolated_project_name
        os.environ.setdefault("GRAFANA_ADMIN_PASSWORD", "admin")
        os.environ.setdefault("SLACK_WEBHOOK_URL", "")
        try:
            with DockerCompose(
                context=str(repo_root),
                compose_file_name=isolated_compose_file,
                env_file=env_file,
                profiles=profiles,
                services=services,
                wait=True,
            ) as compose:
                yield compose
        finally:
            if original_project_name is None:
                os.environ.pop("COMPOSE_PROJECT_NAME", None)
            else:
                os.environ["COMPOSE_PROJECT_NAME"] = original_project_name

            if original_grafana_password is None:
                os.environ.pop("GRAFANA_ADMIN_PASSWORD", None)
            else:
                os.environ["GRAFANA_ADMIN_PASSWORD"] = original_grafana_password

            if original_slack_webhook is None:
                os.environ.pop("SLACK_WEBHOOK_URL", None)
            else:
                os.environ["SLACK_WEBHOOK_URL"] = original_slack_webhook

            protected_after = _project_container_ids(protected_project, protected_services)
            if protected_after != protected_before:
                raise RuntimeError(
                    f"Fixture teardown modified running '{protected_project}' containers: "
                    f"before={sorted(protected_before)} after={sorted(protected_after)}"
                )
    finally:
        if os.path.exists(isolated_compose_file):
            os.unlink(isolated_compose_file)
