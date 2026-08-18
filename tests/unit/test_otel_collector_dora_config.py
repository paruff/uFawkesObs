"""Regression test: config/otel/collector-dora.yaml must not export DORA
metrics to a nonexistent target.

The `otlp/dora` exporter forwarded to
`${DORA_OTEL_ENDPOINT:-http://ufawkesdora-ingestion:4318}` — but
dora/ingestion/api/main.py is REST-only (FastAPI, port 8088, no OTLP
receiver), and dora-api only exposes port 8088. DORA data actually flows
via POST /event, not OTLP. This exporter never had anything listening on
the other end.
"""

import yaml


def test_metrics_dora_pipeline_has_no_dead_otlp_exporter(config_dir):
    collector_dora_path = config_dir / "otel" / "collector-dora.yaml"
    with open(collector_dora_path) as f:
        config = yaml.safe_load(f)

    assert "otlp/dora" not in config.get("exporters", {}), (
        "otlp/dora pointed at ufawkesdora-ingestion:4318, but dora-api "
        "is REST-only (POST /event) — nothing was ever listening there"
    )

    dora_pipeline = config["service"]["pipelines"]["metrics/dora"]
    assert "otlp/dora" not in dora_pipeline.get("exporters", []), (
        "metrics/dora pipeline must not reference the removed otlp/dora exporter"
    )
