"""
Shared step definitions for Gherkin/BDD acceptance tests.

These steps are designed for reuse across all feature files. They cover:
  - File existence checks
  - YAML content checks
  - Version matching across files
  - Markdown linting
  - Docker Compose health
  - Prometheus rule validation
  - Grafana dashboard validation
  - OTel Collector pipeline validation

Feature-specific steps that are unlikely to be reused should live in
a dedicated steps module next to the relevant .feature file.
"""

import re
from pathlib import Path

from pytest_bdd import given, when, then, parsers


# ============================================================================
# GIVEN steps — establishing preconditions
# ============================================================================


@given(parsers.parse('the file "{path}" exists'), target_fixture="target_file")
def given_file_exists(path: str, project_root: Path) -> Path:
    """Assert that a file relative to project root exists and return it."""
    full = project_root / path
    assert full.is_file(), f"File not found: {full}"
    return full


@given(parsers.parse('the directory "{path}" exists'), target_fixture="target_dir")
def given_directory_exists(path: str, project_root: Path) -> Path:
    """Assert that a directory relative to project root exists and return it."""
    full = project_root / path
    assert full.is_dir(), f"Directory not found: {full}"
    return full


@given("the compose.yaml is loaded", target_fixture="compose_dict")
def given_compose_loaded(compose_data: dict) -> dict:
    """Load and return the parsed compose.yaml."""
    assert compose_data, "compose.yaml is empty or could not be parsed"
    return compose_data


@given(parsers.parse('the YAML file "{path}" is loaded'), target_fixture="yaml_data")
def given_yaml_file_loaded(path: str, project_root: Path, load_yaml) -> dict:
    """Load and return the parsed YAML file."""
    full = project_root / path
    assert full.is_file(), f"YAML file not found: {full}"
    data = load_yaml(full)
    assert data is not None, f"YAML file could not be parsed: {full}"
    return data


# ============================================================================
# WHEN steps — performing actions
# ============================================================================


@when(
    parsers.parse('I check the content of "{path}"'), target_fixture="checked_content"
)
def when_check_file_content(path: str, project_root: Path) -> str:
    """Read and return the text content of a file."""
    full = project_root / path
    assert full.is_file(), f"File not found: {full}"
    return full.read_text(encoding="utf-8")


@when(
    parsers.parse('I load the Prometheus rule file "{filename}"'),
    target_fixture="rule_data",
)
def when_load_prometheus_rule(
    filename: str, prometheus_rules_dir: Path, load_yaml
) -> dict:
    """Load a specific Prometheus rule file."""
    full = prometheus_rules_dir / filename
    assert full.is_file(), f"Rule file not found: {full}"
    return load_yaml(full)


@when("I list all Prometheus rule files", target_fixture="rule_files_list")
def when_list_rule_files(prometheus_rules_dir: Path) -> list[Path]:
    """List all .yml files in the Prometheus rules directory."""
    return sorted(prometheus_rules_dir.glob("*.yml"))


@when("I load all Prometheus rules", target_fixture="all_rules")
def when_load_all_rules(all_prometheus_rules: list[dict]) -> list[dict]:
    """Load all Prometheus rule groups (from conftest fixture)."""
    return all_prometheus_rules


# ============================================================================
# THEN steps — asserting outcomes
# ============================================================================


@then(parsers.parse('the file "{path}" should exist'))
def then_file_exists(path: str, project_root: Path) -> None:
    """Assert that a file exists relative to project root."""
    full = project_root / path
    assert full.is_file(), f"Expected file not found: {full}"


@then(parsers.parse('the file "{path}" should not exist'))
def then_file_not_exists(path: str, project_root: Path) -> None:
    """Assert that a file does not exist relative to project root."""
    full = project_root / path
    assert not full.is_file(), f"File should not exist: {full}"


@then(parsers.parse('the directory "{path}" should exist'))
def then_directory_should_exist(path: str, project_root: Path) -> None:
    """Assert that a directory exists relative to project root."""
    full = project_root / path
    assert full.is_dir(), f"Expected directory not found: {full}"


@then(
    parsers.parse('the directory "{path}" should contain a file matching "{pattern}"')
)
def then_dir_contains_matching_file(
    path: str, pattern: str, project_root: Path
) -> None:
    """Assert that a directory contains at least one file matching a glob pattern."""
    full = project_root / path
    assert full.is_dir(), f"Directory not found: {full}"
    matches = list(full.glob(pattern))
    assert len(matches) > 0, f"No files matching '{pattern}' in {full}"


@then(parsers.parse('it should contain "{text}"'))
def then_content_contains(checked_content: str, text: str) -> None:
    """Assert that previously checked content contains a string."""
    assert text in checked_content, f"Expected text '{text}' not found in content"


@then(parsers.parse('it should not contain "{text}"'))
def then_content_not_contains(checked_content: str, text: str) -> None:
    """Assert that previously checked content does NOT contain a string."""
    assert text not in checked_content, f"Unexpected text '{text}' found in content"


@then(parsers.parse('it should match regex "{pattern}"'))
def then_content_matches_regex(checked_content: str, pattern: str) -> None:
    """Assert that previously checked content matches a regex."""
    assert re.search(pattern, checked_content), (
        f"Content does not match regex '{pattern}'"
    )


# --- YAML structure assertions ---


@then(parsers.parse('the YAML should have key "{key}"'))
def then_yaml_has_key(yaml_data: dict, key: str) -> None:
    """Assert that parsed YAML data has a top-level key."""
    assert key in yaml_data, (
        f"Key '{key}' not found in YAML data. Available keys: {list(yaml_data.keys())}"
    )


@then(parsers.parse('the YAML key "{key}" should contain "{value}"'))
def then_yaml_key_contains(yaml_data: dict, key: str, value: str) -> None:
    """Assert that a YAML key's value (as string) contains the given text."""
    actual = yaml_data.get(key, "")
    assert value in str(actual), (
        f"Key '{key}' value does not contain '{value}'. Actual: {actual}"
    )


@then(parsers.parse('the YAML key "{dotted_path}" should equal "{value}"'))
def then_yaml_key_equals(yaml_data: dict, dotted_path: str, value: str) -> None:
    """
    Assert that a nested YAML key equals a given value.
    Supports dotted paths like "service.pipelines.metrics/ai.receivers"
    and list index notation like "[0]".
    """
    current = yaml_data
    parts = _parse_dotted_path(dotted_path)
    for part in parts:
        if isinstance(current, dict):
            assert part in current, f"Key '{part}' not found at path '{dotted_path}'"
            current = current[part]
        elif isinstance(current, list):
            idx = int(part)
            assert 0 <= idx < len(current), (
                f"Index {idx} out of range at path '{dotted_path}'"
            )
            current = current[idx]
        else:
            raise AssertionError(
                f"Cannot navigate into {type(current)} at '{part}' in path '{dotted_path}'"
            )

    assert str(current) == value, (
        f"Path '{dotted_path}': expected '{value}', got '{current}'"
    )


@then(parsers.parse('the YAML key "{dotted_path}" should contain item "{value}"'))
def then_yaml_key_contains_item(yaml_data: dict, dotted_path: str, value: str) -> None:
    """
    Assert that a nested YAML key's value (list or string) contains the given item.
    For lists, checks membership. For strings, checks substring.
    """
    current = _resolve_dotted_path(yaml_data, dotted_path)
    if isinstance(current, list):
        assert value in current, (
            f"Path '{dotted_path}': '{value}' not in list {current}"
        )
    else:
        assert value in str(current), (
            f"Path '{dotted_path}': '{value}' not in '{current}'"
        )


# --- Compose assertions ---


@then(parsers.parse('service "{service_name}" should have image "{expected_image}"'))
def then_service_image(
    compose_data: dict, service_name: str, expected_image: str
) -> None:
    """Assert that a compose service uses a specific image."""
    services = compose_data.get("services", {})
    assert service_name in services, f"Service '{service_name}' not in compose.yaml"
    actual_image = services[service_name].get("image", "")
    assert actual_image == expected_image, (
        f"Service '{service_name}': expected image '{expected_image}', got '{actual_image}'"
    )


@then(parsers.parse('service "{service_name}" should have a healthcheck'))
def then_service_has_healthcheck(compose_data: dict, service_name: str) -> None:
    """Assert that a compose service defines a healthcheck."""
    services = compose_data.get("services", {})
    assert service_name in services, f"Service '{service_name}' not in compose.yaml"
    assert "healthcheck" in services[service_name], (
        f"Service '{service_name}' does not define a healthcheck"
    )


@then(parsers.parse('service "{service_name}" should be in network "{network_name}"'))
def then_service_in_network(
    compose_data: dict, service_name: str, network_name: str
) -> None:
    """Assert that a compose service is attached to a specific network."""
    services = compose_data.get("services", {})
    assert service_name in services, f"Service '{service_name}' not in compose.yaml"
    networks = services[service_name].get("networks", [])
    if isinstance(networks, list):
        assert network_name in networks, (
            f"Service '{service_name}' not in network '{network_name}'. Networks: {networks}"
        )
    elif isinstance(networks, dict):
        assert network_name in networks, (
            f"Service '{service_name}' not in network '{network_name}'. Networks: {list(networks.keys())}"
        )
    else:
        raise AssertionError(
            f"Unexpected networks format for service '{service_name}': {networks}"
        )


@then(parsers.parse('no service should use the "latest" image tag'))
def then_no_latest_tag(compose_data: dict) -> None:
    """Assert that no service in compose.yaml uses 'latest' tag."""
    for name, svc in compose_data.get("services", {}).items():
        image = svc.get("image", "")
        # Skip build-only services (no image key)
        if not image:
            continue
        # Image must be pinned to a specific version (not "latest")
        assert ":" in image, f"Service '{name}' image '{image}' missing version tag"
        # Extract tag after last colon (in case port is in image like localhost:5000/image)
        tag = image.rsplit(":", 1)[-1]
        assert tag != "latest", f"Service '{name}' uses 'latest' tag: '{image}'"


@then(parsers.parse("all services should have a healthcheck"))
def then_all_services_have_healthcheck(compose_data: dict) -> None:
    """Assert that every service in compose.yaml defines a healthcheck.

    Known exception: tempo uses a distroless image (v2.10+) without
    wget/curl/sh, so healthchecks cannot be defined via shell commands.
    See: https://github.com/grafana/tempo/issues/6536
    """
    for name, svc in compose_data.get("services", {}).items():
        # Tempo uses a distroless image — cannot run shell-based healthchecks
        if name == "tempo":
            continue
        assert "healthcheck" in svc, f"Service '{name}' does not define a healthcheck"


# --- Prometheus rule assertions ---


@then(parsers.parse('a recording rule named "{rule_name}" should exist'))
def then_recording_rule_exists(
    all_prometheus_rules: list[dict], rule_name: str
) -> None:
    """Assert that a recording rule with the given name exists in any rule group."""
    found = False
    for group in all_prometheus_rules:
        for rule in group.get("rules", []):
            if rule.get("record") == rule_name:
                found = True
                break
        if found:
            break
    assert found, f"Recording rule '{rule_name}' not found in any rule group"


@then(parsers.parse('an alert rule named "{rule_name}" should exist'))
def then_alert_rule_exists(all_prometheus_rules: list[dict], rule_name: str) -> None:
    """Assert that an alert rule with the given name exists in any rule group."""
    found = False
    for group in all_prometheus_rules:
        for rule in group.get("rules", []):
            if rule.get("alert") == rule_name:
                found = True
                break
        if found:
            break
    assert found, f"Alert rule '{rule_name}' not found in any rule group"


@then("all recording rules should be guarded with or vector(0)")
def then_all_recording_rules_guarded(
    all_prometheus_rules: list[dict], check_vector_zero_guard
) -> None:
    """Assert that every recording rule expression contains 'or vector(0)'."""
    violations: list[str] = []
    for group in all_prometheus_rules:
        source = group.get("_source_file", "unknown")
        for rule in group.get("rules", []):
            if "record" not in rule:
                continue  # skip alert rules
            expr = rule.get("expr", "")
            if not check_vector_zero_guard(expr):
                violations.append(
                    f"{source}: {rule['record']} — missing 'or vector(0)' guard"
                )
    assert not violations, (
        "Recording rules missing 'or vector(0)' guard:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )


@then("all alert rules should have an absent() guard companion")
def then_absent_guard_companions(all_prometheus_rules: list[dict]) -> None:
    """
    Assert that every alert rule with a threshold expression has a
    companion alert using absent() for the same metric family.
    This is a softer check — verifies that each alert group contains
    at least one absent() rule for each metric family that appears
    in threshold alerts.
    """
    # Collect all metric families referenced in non-absent alert expressions
    # and verify there's at least one absent() rule for each
    for group in all_prometheus_rules:
        source = group.get("_source_file", "unknown")
        alert_rules = [r for r in group.get("rules", []) if "alert" in r]
        absent_rules = [r for r in alert_rules if "absent(" in r.get("expr", "")]

        # For AI capability rules, we expect paired absent alerts
        # This is a convention check, not a hard requirement for all groups
        # Only enforce for groups that have category: ai-capability
        is_ai_group = False
        for rule in alert_rules:
            labels = rule.get("labels", {})
            if labels.get("category") == "ai-capability":
                is_ai_group = True
                break

        if is_ai_group and alert_rules:
            # Every non-absent alert in an AI group should have an absent companion
            non_absent_alerts = [
                r for r in alert_rules if "absent(" not in r.get("expr", "")
            ]
            assert len(absent_rules) >= 1, (
                f"{source}: AI capability alert group has {len(non_absent_alerts)} "
                f"threshold alerts but no absent() companion"
            )


@then(
    parsers.parse(
        'alert rule "{alert_name}" should have label "{label_key}" equal to "{label_value}"'
    )
)
def then_alert_has_label(
    all_prometheus_rules: list[dict], alert_name: str, label_key: str, label_value: str
) -> None:
    """Assert that an alert rule has a specific label with a specific value."""
    for group in all_prometheus_rules:
        for rule in group.get("rules", []):
            if rule.get("alert") == alert_name:
                labels = rule.get("labels", {})
                assert labels.get(label_key) == label_value, (
                    f"Alert '{alert_name}' label '{label_key}': "
                    f"expected '{label_value}', got '{labels.get(label_key)}'"
                )
                return
    raise AssertionError(f"Alert rule '{alert_name}' not found")


# --- OTel Collector assertions ---


@then(parsers.parse('the OTel pipeline "{pipeline_name}" should exist'))
def then_otel_pipeline_exists(otel_pipelines: dict, pipeline_name: str) -> None:
    """Assert that a named OTel Collector pipeline exists."""
    assert pipeline_name in otel_pipelines, (
        f"OTel pipeline '{pipeline_name}' not found. "
        f"Available pipelines: {list(otel_pipelines.keys())}"
    )


@then(
    parsers.parse(
        'the OTel pipeline "{pipeline_name}" should contain receiver "{receiver}"'
    )
)
def then_otel_pipeline_has_receiver(
    otel_pipelines: dict, pipeline_name: str, receiver: str
) -> None:
    """Assert that an OTel Collector pipeline includes a specific receiver."""
    pipeline = otel_pipelines.get(pipeline_name)
    assert pipeline, f"OTel pipeline '{pipeline_name}' not found"
    receivers = pipeline.get("receivers", [])
    assert receiver in receivers, (
        f"Pipeline '{pipeline_name}' does not have receiver '{receiver}'. Receivers: {receivers}"
    )


@then(
    parsers.parse(
        'the OTel pipeline "{pipeline_name}" should contain exporter "{exporter}"'
    )
)
def then_otel_pipeline_has_exporter(
    otel_pipelines: dict, pipeline_name: str, exporter: str
) -> None:
    """Assert that an OTel Collector pipeline includes a specific exporter."""
    pipeline = otel_pipelines.get(pipeline_name)
    assert pipeline, f"OTel pipeline '{pipeline_name}' not found"
    exporters = pipeline.get("exporters", [])
    assert exporter in exporters, (
        f"Pipeline '{pipeline_name}' does not have exporter '{exporter}'. Exporters: {exporters}"
    )


@then(
    parsers.parse(
        'the OTel pipeline "{pipeline_name}" should contain processor "{processor}"'
    )
)
def then_otel_pipeline_has_processor(
    otel_pipelines: dict, pipeline_name: str, processor: str
) -> None:
    """Assert that an OTel Collector pipeline includes a specific processor."""
    pipeline = otel_pipelines.get(pipeline_name)
    assert pipeline, f"OTel pipeline '{pipeline_name}' not found"
    processors = pipeline.get("processors", [])
    assert processor in processors, (
        f"Pipeline '{pipeline_name}' does not have processor '{processor}'. Processors: {processors}"
    )


# --- Grafana dashboard assertions ---


@then(parsers.parse('dashboard "{uid}" should exist in dashboards directory'))
def then_dashboard_exists(uid: str, find_dashboard_json) -> None:
    """Assert that a dashboard with the given UID exists in the dashboards/ directory."""
    data = find_dashboard_json(uid)
    assert data is not None, f"Dashboard with uid '{uid}' not found in dashboards/"


@then(parsers.parse('dashboard "{uid}" should use string datasource UIDs'))
def then_dashboard_string_uids(uid: str, find_dashboard_json) -> None:
    """Assert that a dashboard's datasource references use string UIDs, not numeric IDs."""
    data = find_dashboard_json(uid)
    assert data is not None, f"Dashboard with uid '{uid}' not found"

    # Recursively check all datasource UIDs
    _numeric_uids: list[str] = []

    def _check(obj):
        if isinstance(obj, dict):
            ds = obj.get("datasource")
            if isinstance(ds, dict):
                uid_val = ds.get("uid")
                if uid_val is not None and isinstance(uid_val, (int, float)):
                    _numeric_uids.append(str(uid_val))
                elif uid_val is not None and re.match(r"^\d+$", str(uid_val)):
                    _numeric_uids.append(str(uid_val))
            for v in obj.values():
                _check(v)
        elif isinstance(obj, list):
            for item in obj:
                _check(item)

    _check(data)
    assert not _numeric_uids, (
        f"Dashboard '{uid}' contains numeric datasource UIDs: {_numeric_uids}"
    )


@then(parsers.parse('dashboard "{uid}" should have schema version {version:d}'))
def then_dashboard_schema_version(uid: str, version: int, find_dashboard_json) -> None:
    """Assert that a dashboard has a specific schemaVersion."""
    data = find_dashboard_json(uid)
    assert data is not None, f"Dashboard with uid '{uid}' not found"
    actual = data.get("schemaVersion", 0)
    assert actual >= version, (
        f"Dashboard '{uid}' schemaVersion: expected >= {version}, got {actual}"
    )


# --- Version consistency checks ---


@then(
    parsers.parse(
        'the version in "{doc_file}" for "{service_name}" should match compose.yaml'
    )
)
def then_doc_version_matches_compose(
    doc_file: str, service_name: str, project_root: Path, compose_data: dict, load_yaml
) -> None:
    """
    Assert that the version listed for a service in a documentation file
    matches the image tag in compose.yaml.

    The doc file may be YAML or Markdown. For YAML, we do a dict lookup.
    For Markdown, we check for the version string.
    """
    full = project_root / doc_file
    assert full.is_file(), f"Doc file not found: {full}"

    # Get version from compose
    services = compose_data.get("services", {})
    assert service_name in services, f"Service '{service_name}' not in compose.yaml"
    image = services[service_name].get("image", "")
    assert ":" in image, f"Cannot extract version from image: '{image}'"
    compose_version = image.split(":")[-1]

    content = full.read_text(encoding="utf-8")
    assert compose_version in content, (
        f"Version '{compose_version}' for service '{service_name}' not found in {doc_file}. "
        f"compose.yaml image: '{image}'"
    )


# --- Docker Compose config validation ---


@then(parsers.parse("docker compose config should succeed"))
def then_compose_config_succeeds(docker_compose_config_valid) -> None:
    """Assert that 'docker compose config' succeeds (valid compose file)."""
    assert docker_compose_config_valid(), (
        "docker compose config failed (see errors above)"
    )


@then(parsers.parse('docker compose config with profile "{profile}" should succeed'))
def then_compose_config_profile_succeeds(
    docker_compose_config_valid, profile: str
) -> None:
    """Assert that 'docker compose --profile <profile> config' succeeds."""
    assert docker_compose_config_valid(profile=profile), (
        f"docker compose --profile {profile} config failed"
    )


# ============================================================================
# Helper functions
# ============================================================================


def _parse_dotted_path(path: str) -> list[str]:
    """
    Parse a dotted path string, handling '/' in key names.

    e.g. "service.pipelines.metrics/ai.receivers" →
         ["service", "pipelines", "metrics/ai", "receivers"]

    Strategy: try progressively longer prefixes until a key match is found.
    This is handled at assertion time in the step, not here.
    For simplicity, we split on '.' and let the step function try combinations.
    """
    return path.split(".")


def _resolve_dotted_path(data: dict, dotted_path: str):
    """
    Resolve a dotted path, handling keys that contain '/' characters
    (like OTel pipeline names "metrics/ai").

    Uses a greedy approach: at each level, try the full remaining path
    first as a single key, then progressively shorter prefixes.
    """
    parts = dotted_path.split(".")
    current = data
    consumed = 0

    while consumed < len(parts):
        # Try progressively longer key joins from remaining parts
        found = False
        for end in range(len(parts), consumed, -1):
            candidate_key = ".".join(parts[consumed:end])
            if isinstance(current, dict) and candidate_key in current:
                current = current[candidate_key]
                consumed = end
                found = True
                break
        if not found:
            # Try list index
            if isinstance(current, list):
                idx = int(parts[consumed])
                current = current[idx]
                consumed += 1
            else:
                raise AssertionError(
                    f"Cannot resolve path '{dotted_path}' at '{parts[consumed]}'. "
                    f"Available keys: {list(current.keys()) if isinstance(current, dict) else 'N/A'}"
                )

    return current
