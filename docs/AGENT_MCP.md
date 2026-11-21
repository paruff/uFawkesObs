# Agent MCP servers (read-only)

`.mcp.json` and `.opencode/opencode.json` define `grafana` (mcp-grafana, `--disable-write`) and `tempo` (`http://localhost:3200/api/mcp`, enabled in `config/tempo/tempo.yaml`). Tempo MCP passes trace data to your LLM provider.

Grafana token, never committed or pasted in a prompt:

1. Grafana, Administration, Users and access, Service accounts: create one with role **Viewer**, then add a token.
2. `export GRAFANA_SERVICE_ACCOUNT_TOKEN=<token>` (and `GRAFANA_URL` if not `http://localhost:3000`).
3. Check it, because `claude mcp list` shows Connected even for a bad token:
   `curl -s -H "Authorization: Bearer $GRAFANA_SERVICE_ACCOUNT_TOKEN" http://localhost:3000/api/user` must return the service account, not `invalid API key`.
