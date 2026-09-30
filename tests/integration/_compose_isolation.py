from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import uuid
import warnings
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import yaml
from testcontainers.compose import DockerCompose

_HOST_DATA_PREFIX = "./data/"
_COMPOSE_FILENAME = "compose.yaml"


def _ephemeral_port_mappings(ports: list[Any]) -> list[str]:
    mapped_ports: list[str] = []
    for port in ports:
        if isinstance(port, str):
            port_spec, _, protocol = port.partition("/")
            # This keeps only the container-side port from short syntax forms
            # used in this repo (e.g. host:container and host_ip:host:container).
            # IPv6 host-bind variants are out of scope for this stack today.
            container_port = port_spec.split(":")[-1].strip()
            if not container_port:
                continue
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


def _absolutize(relative_path: str, repo_root: pathlib.Path) -> str:
    return str((repo_root / relative_path.removeprefix("./")).resolve())


def _rewrite_volume(volume: Any, repo_root: pathlib.Path) -> Any:
    if isinstance(volume, str):
        parts = volume.split(":")
        if len(parts) >= 2:
            source = parts[0]
            target = parts[1]
            mode = parts[2] if len(parts) > 2 else ""

            if source.startswith(_HOST_DATA_PREFIX):
                warnings.warn(
                    f"Replacing data bind mount {source} with ephemeral volume at {target}",
                    stacklevel=2,
                )
                rewritten: dict[str, Any] = {"type": "volume", "target": target}
                if mode and "ro" in mode.split(","):
                    rewritten["read_only"] = True
                return rewritten

            if source.startswith("./"):
                source = _absolutize(source, repo_root)
                if mode:
                    return f"{source}:{target}:{mode}"
                return f"{source}:{target}"
        return volume

    if isinstance(volume, dict):
        source = str(volume.get("source", ""))
        mount_type = volume.get("type")
        if mount_type == "bind" and source.startswith(_HOST_DATA_PREFIX):
            warnings.warn(
                f"Replacing data bind mount {source} with ephemeral volume at {volume['target']}",
                stacklevel=2,
            )
            rewritten = {"type": "volume", "target": volume["target"]}
            if volume.get("read_only"):
                rewritten["read_only"] = True
            return rewritten
        if mount_type == "bind" and source.startswith("./"):
            rewritten = dict(volume)
            rewritten["source"] = _absolutize(source, repo_root)
            return rewritten
        return volume

    return volume


def _write_isolated_compose_file(repo_root: pathlib.Path) -> str:
    compose_path = repo_root / _COMPOSE_FILENAME
    compose_config = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    compose_config.pop("name", None)

    for service in compose_config.get("services", {}).values():
        service.pop("container_name", None)

        if "ports" in service:
            service["ports"] = _ephemeral_port_mappings(service["ports"])

        if "volumes" in service:
            service["volumes"] = [
                _rewrite_volume(volume, repo_root) for volume in service["volumes"]
            ]

        build = service.get("build")
        if isinstance(build, dict) and isinstance(build.get("context"), str):
            if build["context"].startswith("./"):
                build["context"] = _absolutize(build["context"], repo_root)

    for config in compose_config.get("configs", {}).values():
        config_file = config.get("file") if isinstance(config, dict) else None
        if isinstance(config_file, str) and config_file.startswith("./"):
            config["file"] = _absolutize(config_file, repo_root)

    with tempfile.NamedTemporaryFile(
        "w", prefix="testcontainers-isolated-", suffix=".yaml", delete=False
    ) as isolated_file:
        yaml.safe_dump(compose_config, isolated_file, sort_keys=False)
        return isolated_file.name


def _docker_ps_ids(filters: list[str]) -> set[str]:
    command = ["docker", "ps", "-a", "--format", "{{.ID}}"]
    for filter_value in filters:
        command.extend(["--filter", filter_value])
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _project_container_ids(project_name: str, services: list[str] | None = None) -> set[str]:
    project_filter = f"label=com.docker.compose.project={project_name}"

    if not services:
        return _docker_ps_ids([project_filter])

    container_ids: set[str] = set()
    for service in services:
        service_filter = f"label=com.docker.compose.service={service}"
        container_ids.update(_docker_ps_ids([project_filter, service_filter]))
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

        had_failure = False
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
        except Exception:
            had_failure = True
            raise
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

            try:
                protected_after = _project_container_ids(
                    protected_project, protected_services
                )
                if protected_after != protected_before:
                    message = (
                        f"Fixture teardown modified running '{protected_project}' containers: "
                        f"before={sorted(protected_before)} after={sorted(protected_after)}"
                    )
                    if had_failure:
                        warnings.warn(message, stacklevel=2)
                    else:
                        raise RuntimeError(message)
            except Exception as error:
                if had_failure:
                    warnings.warn(
                        "Failed to verify protected project state after fixture teardown: "
                        f"{error}",
                        stacklevel=2,
                    )
                else:
                    raise
    finally:
        if os.path.exists(isolated_compose_file):
            os.unlink(isolated_compose_file)
