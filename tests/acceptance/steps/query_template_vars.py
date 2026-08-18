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
    """Substitute Grafana template variable tokens in a PromQL/LogQL expr.

    - "query"-type variables (label matchers, e.g. job=~"$service") are
      replaced with a match-at-least-one-char regex. ".+" rather than
      ".*": Loki rejects a stream selector whose only matcher is
      equivalent to matching everything including empty (400 "queries
      require at least one regexp or equality matcher that does not
      match empty") -- ".+" satisfies both Loki and Prometheus.
    - "interval"-type variables (range vector durations, e.g.
      [$window]) are replaced with their current selected value --
      these aren't label matchers, so a regex substitution would
      produce invalid syntax (e.g. "[.+]" is not a valid duration).

    Datasource-type variables are handled separately by
    _resolve_template_datasource_uid and are not touched here.
    """
    for var_def in templating.get("list", []):
        name = var_def.get("name")
        if not name:
            continue
        var_type = var_def.get("type")
        if var_type == "query":
            replacement = var_def.get("allValue") or ".+"
        elif var_type == "interval":
            replacement = (
                var_def.get("current", {}).get("value")
                or var_def.get("query", "").split(",")[0]
            )
        else:
            continue
        pattern = rf"\$\{{{re.escape(name)}\}}|\${re.escape(name)}\b"
        expr = re.sub(pattern, replacement, expr)
    return expr
