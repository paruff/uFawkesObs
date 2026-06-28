# CI Diagnosis — PR #124

```
Failure:      Validate Configs / Validate Prometheus config
              Build & Validate / Build & Validate
Location:     promtool check config on config/prometheus/prometheus.yaml
Evidence:     FAILED: "/etc/prometheus/rules/ai-rules.yml" does not point to an existing file
Likely Cause: File placed at config/prometheus/ai-rules.yml instead of config/prometheus/rules/ai-rules.yml
Confidence:   HIGH
Proposed Fix: Move config/prometheus/ai-rules.yml into config/prometheus/rules/ai-rules.yml.
              Volume mount in compose.yaml is ./config/prometheus/rules/:/etc/prometheus/rules/,
              so only files in config/prometheus/rules/ are available at the /etc/prometheus/rules/ path.
              The rule_files reference in prometheus.yaml ("/etc/prometheus/rules/ai-rules.yml") is correct
              but the file needs to physically exist inside the mounted directory.
```
