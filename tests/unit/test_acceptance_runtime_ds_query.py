"""Unit tests for GrafanaClient.ds_query's datasource-type support.

Regression coverage for the OBS-SLI-006 investigation: ds_query hardcoded
"type": "prometheus" in every query payload regardless of the datasource
actually being queried, and query_dashboard_panels (slo_steps.py) only
ever attempted panels where ds_type == "prometheus" -- meaning every
Loki-backed dashboard (Application Performance, Application Performance -
Logs, IoT Devices & MQTT) was never queried at all, even though real data
existed (confirmed live 2026-08-18 via a direct Loki API query showing
real log throughput for a running app, while the same panel's check in
the acceptance test reported "no data").
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from tests.acceptance.runtime import GrafanaClient


class TestDsQueryDatasourceType:
    def test_defaults_to_prometheus(self) -> None:
        client = GrafanaClient()
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200, json=lambda: {"results": {}}
            )
            client.ds_query("prometheus-uid", "up")
            payload = mock_post.call_args.kwargs["json"]
            assert payload["queries"][0]["datasource"]["type"] == "prometheus"
            assert payload["queries"][0]["expr"] == "up"

    def test_accepts_loki_datasource_type(self) -> None:
        client = GrafanaClient()
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200, json=lambda: {"results": {}}
            )
            client.ds_query("loki-uid", '{compose_service=~".+"}', ds_type="loki")
            payload = mock_post.call_args.kwargs["json"]
            assert payload["queries"][0]["datasource"]["type"] == "loki"
            assert payload["queries"][0]["expr"] == '{compose_service=~".+"}'
            assert payload["queries"][0]["queryType"] == "range"
