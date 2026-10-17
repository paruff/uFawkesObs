# Mac agent -> uFawkesObs

Ships host metrics, logs and OTLP from a Mac to the stack's collector
(`192.168.1.10:4317`, LAN only, unauthenticated).

```sh
# No brew formula exists. Download the release matching the NAS collector (0.162.0):
ARCH=$(uname -m | sed 's/x86_64/amd64/')   # arm64 stays arm64
cd "$(mktemp -d)" && curl -fsSLO https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.162.0/otelcol-contrib_0.162.0_darwin_${ARCH}.tar.gz
tar xzf otelcol-contrib_*.tar.gz otelcol-contrib && sudo install otelcol-contrib /usr/local/bin/
otelcol-contrib validate --config=config.yaml   # run from deploy/mac-agent/ after setting HOST_NAME
cd - && sudo cp config.yaml /usr/local/etc/ufawkes-obs-agent.yaml
# edit HOST_NAME in the plist, then:
cp io.ufawkes.obs-agent.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/io.ufawkes.obs-agent.plist
```

Verify: Grafana -> Dashboards -> "Host Metrics (OTLP agents)" (separate PR), or in Prometheus
`count by (host_name) ({__name__=~"app_metrics_system_.*"})`.

Apps on the Mac: `export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4317`.
Claude Code: also `CLAUDE_CODE_ENABLE_TELEMETRY=1`.

Metrics arrive as `app_metrics_system_*` (OTLP via the collector's Prometheus
exporter), not `node_*`, so node-exporter dashboards do not apply.
Adjust the `filelog` include paths to the logs you care about.
