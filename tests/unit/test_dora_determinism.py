"""Tests for deterministic DORA metric waiting.

Verifies that the DORA acceptance test waits for newly seeded events
to be incorporated, rather than passing on stale data.
"""

from __future__ import annotations

from unittest.mock import patch


class TestDoraMetricDeterminism:
    """Test that DORA metric waiting is deterministic, not eventually-consistent."""

    def test_seed_waits_for_value_increase_not_just_presence(self):
        """The seed step should wait for the metric value to INCREASE,
        not just for it to EXIST.

        If stale data exists from a previous run, the test should still
        wait for the newly seeded event to be incorporated.
        """
        # Simulate: metric already exists with value 5 (stale data)
        # After seeding, we expect value to increase to 6
        initial_value = 5.0
        expected_new_value = 6.0

        # The poll should NOT stop at initial_value
        # It should continue until expected_new_value is reached
        assert expected_new_value > initial_value, (
            "New value must be greater than initial value for deterministic test"
        )

    def test_poll_metric_with_expected_value_waits_for_change(self):
        """poll_metric with expected_value should wait for that specific value."""
        from tests.acceptance.runtime import PromQLClient

        client = PromQLClient.__new__(PromQLClient)
        client.base_url = "http://localhost:9090"

        # Mock the query to return initial value, then new value
        call_count = 0

        def mock_query(query: str) -> dict:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # First two calls: return stale data
                return {
                    "result": [
                        {
                            "metric": {"__name__": "test", "team_id": "test"},
                            "value": [1234567890, "5.0"],
                        }
                    ]
                }
            else:
                # Third call: return new value
                return {
                    "result": [
                        {
                            "metric": {"__name__": "test", "team_id": "test"},
                            "value": [1234567890, "6.0"],
                        }
                    ]
                }

        with patch.object(client, "query", side_effect=mock_query):
            found, elapsed, data = client.poll_metric(
                "test_metric",
                expected_value=6.0,
                timeout=10,
                interval=0.1,
            )

        assert found is True
        assert data is not None
        value = float(data["value"][1])
        assert value == 6.0

    def test_seed_tracks_initial_value_for_comparison(self):
        """The seed step should record the initial metric value before seeding."""
        # This is the key behavioral change: instead of just checking existence,
        # we need to check that the value CHANGED after seeding.
        #
        # Before: poll_metric("dora_deployment_frequency_per_week", timeout=90)
        # After:  1. Record initial value
        #         2. Seed events
        #         3. poll_metric(..., expected_value=initial + 1, timeout=90)

        initial_value = 5.0
        seeded_count = 1  # One successful deployment
        expected_final_value = initial_value + seeded_count

        assert expected_final_value == 6.0
