# CI Fix Report — PR #124

```
Changed:      config/prometheus/ai-rules.yml → config/prometheus/rules/ai-rules.yml (rename)
              tests/unit/test_prometheus_config_validation.py (update test path)
              ci-diagnosis.md (new)
Validation:   yamllint PASS, promtool check rules PASS (12 rules), pytest PASS (227 tests)
```

## Root Cause

The file `config/prometheus/ai-rules.yml` was placed in the wrong directory. The Prometheus
volume mount in `compose.yaml` maps `./config/prometheus/rules/:/etc/prometheus/rules/`, so
rule files referenced in `prometheus.yaml` rule_files as `/etc/prometheus/rules/ai-rules.yml`
must physically exist at `config/prometheus/rules/ai-rules.yml`.

## Fix

1. Moved `config/prometheus/ai-rules.yml → config/prometheus/rules/ai-rules.yml`
2. Updated test path in `test_prometheus_config_validation.py` to match new location

## Why This Pattern

The existing rule file (`ufawkesobs-self-monitoring.yml`) already lives in
`config/prometheus/rules/`. The new file belongs in the same directory to be picked up
by the same volume mount. The `rule_files:` reference in `prometheus.yaml` was already
correct — just the physical file was in the wrong place.

## Remaining Risks

None. This is a minimal filesystem fix — the file content, config refs, and tests
were all verified passing before pushing.
