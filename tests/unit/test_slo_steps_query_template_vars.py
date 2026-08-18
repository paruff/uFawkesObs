"""Unit tests for resolving Grafana query-variable tokens in PromQL exprs.

Regression coverage for the OBS-SLI-006 investigation: query_dashboard_panels
in tests/acceptance/steps/slo_steps.py only resolves the panel-level
datasource template variable (via _resolve_template_datasource_uid) --
it never substitutes query-type variables (e.g. $service, $instance) that
appear inside the panel's own PromQL expr, such as
`http_requests_total{job=~"$service"}`. Confirmed live (2026-08-18)
against a running stack: every "Services" folder dashboard uses exactly
this pattern, and Prometheus receiving the literal string "$service" as
a label matcher value matches zero series -- explaining a 100% failure
rate across that entire dashboard folder.

Loaded directly via importlib rather than
`from tests.acceptance.steps.query_template_vars import ...` -- see
test_dora_acceptance_workload.py for why (avoids pulling in
tests.acceptance.workloads.__init__'s opentelemetry.sdk dependency via
package init, which this pure-function module has no need for).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "query_template_vars_under_test",
    REPO_ROOT / "tests" / "acceptance" / "steps" / "query_template_vars.py",
)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
resolve_query_template_vars = _mod.resolve_query_template_vars


SERVICE_TEMPLATING = {
    "list": [
        {"name": "datasource", "type": "datasource", "query": "prometheus"},
        {
            "name": "service",
            "type": "query",
            "allValue": ".+",
            "query": "label_values(up, job)",
        },
        {
            "name": "instance",
            "type": "query",
            "allValue": ".+",
            "query": 'label_values(up{job=~"$service"}, instance)',
        },
    ]
}

NO_ALLVALUE_TEMPLATING = {
    "list": [
        {"name": "service", "type": "query", "query": "label_values(up, job)"},
    ]
}

WINDOW_TEMPLATING = {
    "list": [
        {
            "name": "window",
            "type": "interval",
            "query": "7d,30d,90d",
            "current": {"text": "30d", "value": "30d"},
        },
    ]
}


class TestResolveQueryTemplateVars:
    def test_substitutes_dollar_brace_form(self) -> None:
        expr = 'sum(rate(http_requests_total{job=~"${service}"}[5m]))'
        resolved = resolve_query_template_vars(expr, SERVICE_TEMPLATING)
        assert "${service}" not in resolved
        assert 'job=~".+"' in resolved

    def test_substitutes_dollar_bare_form(self) -> None:
        expr = (
            'sum(rate(http_requests_total{job=~"$service",instance=~"$instance"}[5m]))'
        )
        resolved = resolve_query_template_vars(expr, SERVICE_TEMPLATING)
        assert "$service" not in resolved
        assert "$instance" not in resolved
        assert 'job=~".+"' in resolved
        assert 'instance=~".+"' in resolved

    def test_defaults_to_dot_plus_not_dot_star_when_no_allvalue(self) -> None:
        """Regression test: Loki rejects a stream selector whose only
        matcher is equivalent to matching everything including empty
        (e.g. {compose_service=~".*"}) with 400 "queries require at
        least one regexp or equality matcher that does not match empty".
        ".+" (at least one char) satisfies both Prometheus and Loki;
        ".*" only satisfies Prometheus. Confirmed live 2026-08-18."""
        expr = 'sum(rate({compose_service=~"$service"}[5m]))'
        resolved = resolve_query_template_vars(expr, NO_ALLVALUE_TEMPLATING)
        assert 'compose_service=~".+"' in resolved
        assert ".*" not in resolved

    def test_substitutes_interval_type_variable_in_range_vector(self) -> None:
        """Regression test: DORA Overview's Deployment Frequency panel uses
        an interval-type $window variable inside a range vector duration
        (last_over_time(...[$window])) -- the query-type-only substitution
        left "[$window]" as a literal, invalid PromQL duration, causing a
        400. Confirmed live 2026-08-18."""
        expr = "last_over_time(dora_deployment_frequency_per_week[$window])"
        resolved = resolve_query_template_vars(expr, WINDOW_TEMPLATING)
        assert resolved == "last_over_time(dora_deployment_frequency_per_week[30d])"

    def test_leaves_unrelated_dollar_text_alone(self) -> None:
        expr = 'up{job="$servicewithsuffix"}'
        resolved = resolve_query_template_vars(expr, SERVICE_TEMPLATING)
        # "$service" is a prefix of "$servicewithsuffix" but must not match
        # as a whole-token substitution
        assert resolved == expr

    def test_ignores_datasource_type_variables(self) -> None:
        expr = 'up{job=~"$datasource"}'
        resolved = resolve_query_template_vars(expr, SERVICE_TEMPLATING)
        # datasource-type vars are handled by _resolve_template_datasource_uid
        # elsewhere, not by this function
        assert resolved == expr

    def test_no_templating_is_a_noop(self) -> None:
        expr = 'up{job="static"}'
        assert resolve_query_template_vars(expr, {}) == expr
