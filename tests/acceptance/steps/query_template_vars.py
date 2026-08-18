"""Resolve Grafana query-variable tokens ($var / ${var}) inside a PromQL expr.

Pure, dependency-free (stdlib only) so tests/unit can exercise it without
pulling in tests.acceptance.workloads' opentelemetry.sdk dependency.

query_dashboard_panels (slo_steps.py) previously only resolved the panel's
own datasource template variable -- it never substituted query-type
variables (job=~"$service", instance=~"$instance", etc.) used inside the
query expression itself. Prometheus receives the literal string "$service"
as a label matcher, which matches nothing.
"""

from __future__ import annotations

import re


def resolve_query_template_vars(expr: str, templating: dict) -> str:
    """Substitute query-type template variables in a PromQL expr with a
    match-anything regex, so panels using $var/${var} in label matchers
    return whatever data actually exists rather than matching nothing.

    Datasource-type variables are handled separately by
    _resolve_template_datasource_uid and are not touched here.
    """
    for var_def in templating.get("list", []):
        if var_def.get("type") != "query":
            continue
        name = var_def.get("name")
        if not name:
            continue
        all_value = var_def.get("allValue") or ".*"
        pattern = rf"\$\{{{re.escape(name)}\}}|\${re.escape(name)}\b"
        expr = re.sub(pattern, all_value, expr)
    return expr
