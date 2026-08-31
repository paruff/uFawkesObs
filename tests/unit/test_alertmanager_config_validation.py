"""Validation tests for Alertmanager config and the LB-03 notification recipes.

Covers the tested Slack and Discord notification channel recipes in
`config/alertmanager/alertmanager.yml`:
  - the recipes must use `${SLACK_WEBHOOK_URL}` / the Discord bridge, never a
    hardcoded webhook secret
  - the default stack must stay webhook-only (nothing enabled out of the box)
  - the `alertmanager-discord` bridge service in compose.yaml must be pinned
    and confined to the internal network

Run:  pytest tests/unit/test_alertmanager_config_validation.py -v
      (no running stack required — reads files statically)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ALERTMANAGER_CFG = (
    Path(__file__).resolve().parents[2] / "config" / "alertmanager" / "alertmanager.yml"
)
COMPOSE_PATH = Path(__file__).resolve().parents[2] / "compose.yaml"
ENV_EXAMPLE_PATH = Path(__file__).resolve().parents[2] / ".env.example"

EXPECTED_DISCORD_IMAGE = "rogerrum/alertmanager-discord:1.0.7"
SLACK_WEBHOOK_PLACEHOLDER = "T0000000/B0000000/XXXX"


@pytest.fixture(scope="module")
def alertmanager_raw() -> str:
    """Return the raw alertmanager config so commented recipes are visible."""
    return ALERTMANAGER_CFG.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def alertmanager_data() -> dict:
    """Return the parsed alertmanager config (comments stripped)."""
    with open(ALERTMANAGER_CFG, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "alertmanager.yml must parse to a mapping"
    return data


@pytest.fixture(scope="module")
def compose_data() -> dict:
    """Return the parsed compose.yaml as a dict."""
    with open(COMPOSE_PATH, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "compose.yaml must parse to a mapping"
    return data


@pytest.fixture(scope="module")
def env_example() -> str:
    """Return the raw .env.example contents."""
    return ENV_EXAMPLE_PATH.read_text(encoding="utf-8")


class TestDefaultRoutingUnchanged:
    """The default stack must keep sending alerts to the local test sink."""

    def test_default_receiver_is_webhook_only(self, alertmanager_data: dict) -> None:
        assert alertmanager_data["route"]["receiver"] == "default-webhook", (
            "Default Alertmanager receiver must remain the local test webhook"
        )

    def test_default_webhook_receiver_present(self, alertmanager_data: dict) -> None:
        receiver_names = [r["name"] for r in alertmanager_data["receivers"]]
        assert "default-webhook" in receiver_names

    def test_no_active_slack_or_discord_receiver(self, alertmanager_data: dict) -> None:
        """Slack/Discord receivers must stay commented out by default."""
        for receiver in alertmanager_data["receivers"]:
            assert "slack_configs" not in receiver, (
                f"Receiver '{receiver['name']}' has active slack_configs — "
                "must stay commented out (LB-03 recipe)"
            )
            for cfg in receiver.get("webhook_configs", []):
                assert not str(cfg.get("url", "")).startswith(
                    ("https://discord.com", "http://alertmanager-discord")
                ), f"Receiver '{receiver['name']}' has an active Discord webhook"


class TestSlackRecipe:
    """The documented Slack recipe must exist and avoid hardcoded secrets."""

    def test_slack_recipe_uses_secret_file(self, alertmanager_raw: str) -> None:
        """Alertmanager doesn't expand ${VAR} in its own config file — that
        substitution only applies to compose.yaml. The recipe must use
        api_url_file against the Compose-managed secret instead (confirmed
        live against a real Slack workspace, LB-03/#181)."""
        assert "api_url_file: /run/secrets/slack_webhook_url" in alertmanager_raw, (
            "Slack recipe must reference api_url_file, not ${SLACK_WEBHOOK_URL} "
            "substitution (which Alertmanager does not perform)"
        )
        assert 'api_url: "${SLACK_WEBHOOK_URL}"' not in alertmanager_raw, (
            "Slack recipe must not use the broken ${SLACK_WEBHOOK_URL} "
            "substitution pattern — confirmed non-functional live"
        )

    def test_slack_recipe_is_fully_commented(self, alertmanager_raw: str) -> None:
        slack_lines = [
            ln for ln in alertmanager_raw.splitlines() if "slack_configs" in ln
        ]
        assert slack_lines, "No slack_configs example found in alertmanager.yml"
        assert all(ln.lstrip().startswith("#") for ln in slack_lines), (
            "Slack recipe must remain commented out by default"
        )

    def test_no_hardcoded_slack_webhook_secret(self, alertmanager_raw: str) -> None:
        """Any hooks.slack.com/services URL must be a documented placeholder."""
        for ln in alertmanager_raw.splitlines():
            if "hooks.slack.com/services" not in ln:
                continue
            assert SLACK_WEBHOOK_PLACEHOLDER in ln, (
                f"Concrete-looking Slack webhook URL found: {ln.strip()}"
            )


class TestDiscordRecipe:
    """The Discord recipe must route through the pinned internal bridge."""

    def test_discord_recipe_points_at_bridge(self, alertmanager_raw: str) -> None:
        assert "http://alertmanager-discord:9094" in alertmanager_raw, (
            "Discord recipe must reference the alertmanager-discord bridge"
        )

    def test_discord_recipe_is_fully_commented(self, alertmanager_raw: str) -> None:
        for ln in alertmanager_raw.splitlines():
            if "alertmanager-discord:9094" in ln:
                assert ln.lstrip().startswith("#"), (
                    "Discord receiver must stay commented out by default"
                )

    def test_bridge_service_present_and_pinned(self, compose_data: dict) -> None:
        services = compose_data["services"]
        assert "alertmanager-discord" in services
        assert services["alertmanager-discord"]["image"] == EXPECTED_DISCORD_IMAGE

    def test_bridge_is_in_notifications_profile(self, compose_data: dict) -> None:
        profiles = compose_data["services"]["alertmanager-discord"].get("profiles", [])
        assert "notifications" in profiles, (
            "alertmanager-discord must be gated behind the 'notifications' profile "
            "so the default core stack is unchanged"
        )

    def test_bridge_has_no_host_port_exposure(self, compose_data: dict) -> None:
        ports = compose_data["services"]["alertmanager-discord"].get("ports")
        assert not ports, (
            f"alertmanager-discord must not publish host ports, found: {ports}"
        )

    def test_bridge_is_on_observability_network(self, compose_data: dict) -> None:
        networks = compose_data["services"]["alertmanager-discord"].get("networks")
        assert networks == ["observability"] or (
            isinstance(networks, dict) and "observability" in networks
        ), f"alertmanager-discord must join observability network, found: {networks}"

    def test_bridge_webhook_env_is_interpolable(self, compose_data: dict) -> None:
        """DISCORD_WEBHOOK must not fail compose interpolation when unset."""
        env = compose_data["services"]["alertmanager-discord"].get("environment", [])
        assert any("DISCORD_WEBHOOK" in str(item) for item in env), (
            "alertmanager-discord must receive DISCORD_WEBHOOK from .env"
        )
        env_str = "\n".join(str(item) for item in env)
        assert "DISCORD_WEBHOOK_URL" in env_str and ":?}" not in env_str.replace(
            "${DISCORD_WEBHOOK_URL:-}", ""
        ), "DISCORD_WEBHOOK must use a safe default (no required-var interpolation)"


class TestEnvExample:
    """.env.example must document both webhook variables with placeholders."""

    @pytest.mark.parametrize(
        "var,placeholder",
        [
            ("SLACK_WEBHOOK_URL", "REPLACE_ME"),
            ("DISCORD_WEBHOOK_URL", "REPLACE_ME"),
        ],
    )
    def test_webhook_vars_documented(
        self, env_example: str, var: str, placeholder: str
    ) -> None:
        for ln in env_example.splitlines():
            if ln.startswith(f"{var}="):
                assert placeholder in ln, (
                    f"{var} must use a placeholder in .env.example"
                )
                return
        pytest.fail(f"{var} is missing from .env.example")

    def test_alertmanager_gets_slack_webhook_secret(self, compose_data: dict) -> None:
        """The webhook reaches Alertmanager as a Compose secret file
        (api_url_file), not a container env var Alertmanager can't read
        into its own config — see test_slack_recipe_uses_secret_file."""
        secrets = compose_data.get("secrets", {})
        assert "slack_webhook_url" in secrets, (
            "compose.yaml must declare a slack_webhook_url secret"
        )
        assert secrets["slack_webhook_url"].get("environment") == "SLACK_WEBHOOK_URL", (
            "slack_webhook_url secret must source from the SLACK_WEBHOOK_URL env var"
        )
        service_secrets = compose_data["services"]["alertmanager"].get("secrets", [])
        assert "slack_webhook_url" in service_secrets, (
            "alertmanager service must mount the slack_webhook_url secret"
        )

    def test_dora_slack_var_replaced(self, alertmanager_raw: str) -> None:
        """DORA_SLACK_WEBHOOK_URL was consolidated into SLACK_WEBHOOK_URL."""
        assert "DORA_SLACK_WEBHOOK_URL" not in alertmanager_raw
