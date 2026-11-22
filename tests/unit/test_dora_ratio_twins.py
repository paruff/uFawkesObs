"""#729: dora_cfr_ratio / dora_rework_rate_ratio publish beside the _pct names."""

import re

from dora.compute.metrics import render_prometheus_text


def _sample(text: str, name: str) -> str:
    match = re.search(rf"^{name}\{{[^}}]*\}} (\S+)$", text, re.MULTILINE)
    assert match, f"{name} missing from exposition"
    return match.group(1)


def test_ratio_twins_equal_pct_names():
    text = render_prometheus_text(
        [
            {
                "team_id": "org/repo",
                "change_failure_rate": 0.25,
                "rework_rate_pct": 0.1,
                "dora_tier_cfr": "high",
                "dora_tier_rework_rate": "elite",
            }
        ]
    )
    assert _sample(text, "dora_cfr_ratio") == _sample(text, "dora_cfr_pct") == "0.25"
    assert (
        _sample(text, "dora_rework_rate_ratio")
        == _sample(text, "dora_rework_rate_pct")
        == "0.1"
    )
    assert 'dora_cfr_ratio{team_id="org/repo",tier="high"}' in text
    assert "# TYPE dora_cfr_ratio gauge" in text
